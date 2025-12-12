"""Droid CLI client - async subprocess 直连调用 Droid CLI"""
import asyncio
import json
import os
from typing import Any


def get_droid_cmd() -> list[str]:
    """构建 Droid CLI 命令。

    支持的环境变量（在 .mcp.json 中配置）：
    - DROID_MODEL: 模型名称（如 custom:MiniMax-M2-0）
    - DROID_ENABLED_TOOLS: 启用的工具集（默认 LS,Read,Glob,Grep,Edit,Create,Execute）
    - DROID_AUTO_LEVEL: 自动化级别（默认 high）
    - DROID_REASONING_EFFORT: 推理深度（默认使用 CLI 默认值）
    """
    if env_cmd := os.getenv("DROID_CLI_CMD"):
        return env_cmd.split()

    enabled_tools = os.getenv("DROID_ENABLED_TOOLS", "LS,Read,Glob,Grep,Edit,Create,Execute")
    auto_level = os.getenv("DROID_AUTO_LEVEL", "high")

    cmd = [
        "droid", "exec",
        "--output-format", "json",
        "--auto", auto_level,
        "--enabled-tools", enabled_tools,
    ]

    # 可选参数：仅在设置时添加
    if model := os.getenv("DROID_MODEL"):
        cmd.extend(["-m", model])

    if reasoning := os.getenv("DROID_REASONING_EFFORT"):
        cmd.extend(["--reasoning-effort", reasoning])

    return cmd


def build_prompt(payload: dict[str, Any]) -> str:
    """构建 Droid 执行提示词。"""
    objective = payload.get("objective") or "Execute the described task."
    instructions = payload.get("instructions") or ""
    ctx = payload.get("context") or {}
    if isinstance(ctx, str):
        ctx = {"summary": ctx}

    files = ctx.get("files_of_interest") or []
    constraints = payload.get("constraints") or []
    acceptance = payload.get("acceptance_criteria") or []

    parts = [f"Objective: {objective}"]
    if instructions:
        parts.append(f"Instructions: {instructions}")
    if files:
        parts.append("Relevant files: " + ", ".join(files))
    if constraints:
        parts.append("Constraints: " + "; ".join(constraints))
    if acceptance:
        parts.append("Acceptance criteria: " + "; ".join(acceptance))

    parts.extend([
        "",
        "Act as an implementation-focused coding agent. "
        "Execute the necessary edits and commands in the current repository to satisfy the objective "
        "and acceptance criteria. Return a concise JSON summary of what you did."
    ])

    return "\n".join(parts)


def _clip(text: str | None, limit: int = 800) -> str:
    if not text:
        return ""
    text = text.strip()
    return text[-limit:] if len(text) > limit else text


def _parse_json(raw: str) -> dict | None:
    """解析 Droid CLI JSON 输出。"""
    if not raw.strip():
        return None
    try:
        return json.loads(raw.strip())
    except json.JSONDecodeError:
        pass

    for line in reversed(raw.strip().splitlines()):
        line = line.strip()
        if line.startswith('{') and line.endswith('}'):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
    return None


def _normalize_output(data: dict | None, stdout: str) -> dict[str, Any]:
    """标准化输出格式。"""
    base = {
        "status": "success",
        "summary": "",
        "files_changed": [],
        "commands_run": [],
        "tests": {},
        "logs": [],
        "issues": [],
    }

    if not data:
        base["summary"] = _clip(stdout) or "Execution completed"
        if stdout.strip():
            base["logs"] = [_clip(stdout)]
        return base

    # 支持官方 droid exec JSON 格式
    if data.get("type") == "result":
        base["status"] = "failed" if data.get("is_error") or data.get("subtype") == "error" else "success"
        base["summary"] = data.get("result") or ""
        if data.get("session_id"):
            base["logs"].append(f"session_id: {data['session_id']}")
        if data.get("duration_ms"):
            base["logs"].append(f"duration: {data['duration_ms']}ms")
    else:
        base["status"] = data.get("status") or "success"
        base["summary"] = data.get("summary") or data.get("message") or data.get("result") or ""

    # 映射文件变更
    for key in ["files_changed", "files", "changes"]:
        if files := data.get(key):
            base["files_changed"] = [
                {"path": f if isinstance(f, str) else f.get("path", ""), "change_type": "modified", "highlights": []}
                for f in files
            ]
            break

    # 映射命令
    for key in ["commands_run", "commands"]:
        if cmds := data.get(key):
            base["commands_run"] = [
                {"command": c if isinstance(c, str) else c.get("command", ""), "exit_code": None if isinstance(c, str) else c.get("exit_code"), "stdout_excerpt": "", "stderr_excerpt": ""}
                for c in cmds
            ]
            break

    if not base["summary"]:
        base["summary"] = _clip(stdout) or "Execution completed"

    return base


def _error_result(status: str, summary: str, stdout: str = "", stderr: str = "") -> dict[str, Any]:
    """构建错误结果。"""
    return {
        "status": status,
        "summary": summary,
        "files_changed": [],
        "commands_run": [],
        "tests": {},
        "logs": [item for item in [_clip(stdout), _clip(stderr)] if item],
        "issues": [{"type": "error", "description": summary, "suggested_action": "Check Droid CLI logs"}],
    }


async def call_droid_async(payload: dict[str, Any]) -> dict[str, Any]:
    """异步调用 Droid CLI 并返回结果。

    支持的环境变量：
    - DROID_TIMEOUT: 单任务超时秒数（默认 1800，即 30 分钟）
    """
    timeout = int(os.getenv("DROID_TIMEOUT", "1800"))

    objective = (payload.get("objective") or "").strip()
    if not objective:
        return _error_result("error", "Objective 不能为空")
    if len(objective) > 50000:
        return _error_result("error", f"Objective 过长 ({len(objective)} 字符)")

    instructions = payload.get("instructions") or ""
    if len(instructions) > 100000:
        return _error_result("error", f"Instructions 过长 ({len(instructions)} 字符)")

    prompt = build_prompt(payload)
    cmd = get_droid_cmd()

    ctx = payload.get("context") or {}
    if isinstance(ctx, str):
        ctx = {"summary": ctx}

    if repo_root := ctx.get("repo_root"):
        cmd.extend(["--cwd", repo_root])

    cmd.append(prompt)

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                proc.communicate(),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            return _error_result("timeout", f"Droid 执行超时（{timeout}秒）")

        stdout = stdout_bytes.decode() if stdout_bytes else ""
        stderr = stderr_bytes.decode() if stderr_bytes else ""

        if proc.returncode != 0:
            return _error_result("failed", f"Droid CLI failed with code {proc.returncode}", stdout, stderr)

        return _normalize_output(_parse_json(stdout), stdout)

    except FileNotFoundError:
        return _error_result("error", "Droid CLI not found")


def call_droid(payload: dict[str, Any]) -> dict[str, Any]:
    """同步调用（兼容原有接口）。"""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # 已在事件循环中，创建新任务
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            future = pool.submit(asyncio.run, call_droid_async(payload))
            return future.result()
    else:
        return asyncio.run(call_droid_async(payload))
