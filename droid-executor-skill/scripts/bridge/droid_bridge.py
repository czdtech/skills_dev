#!/usr/bin/env python3
import json
import os
import subprocess
import time
from typing import Any, Dict, List, Optional

from server_lib import run_server, logger

# 配置超时时间（默认 10 分钟 = 600 秒）
# 可通过环境变量 DROID_TIMEOUT 自定义
DROID_TIMEOUT = int(os.getenv("DROID_TIMEOUT", "600"))

def get_droid_cmd_base() -> List[str]:
    """Constructs Droid CLI base command."""
    env_cmd = os.getenv("DROID_CLI_CMD")
    if env_cmd:
        return env_cmd.split()
    # 官方 CLI 支持 --output-format json，返回固定字段，便于二次加工
    # --auto high 允许自动执行而无需权限确认
    return ["droid", "exec", "--output-format", "json", "--auto", "high"]

def build_prompt(payload: Dict[str, Any]) -> str:
    """Constructs natural language prompt for Droid."""
    objective = payload.get("objective") or payload.get("task_id") or "Execute the described task."
    instructions = payload.get("instructions") or ""
    ctx = payload.get("context") or {}
    # Handle case where context is a string (e.g. passed from a simple client)
    if isinstance(ctx, str):
        ctx = {"summary": ctx}
        
    files = ctx.get("files_of_interest") or []
    constraints = payload.get("constraints") or []
    acceptance = payload.get("acceptance_criteria") or []

    parts: List[str] = []
    parts.append(f"Objective: {objective}")
    if instructions:
        parts.append(f"Instructions: {instructions}")
    if files:
        parts.append("Relevant files: " + ", ".join(files))
    if constraints:
        parts.append("Constraints: " + "; ".join(constraints))
    if acceptance:
        parts.append("Acceptance criteria: " + "; ".join(acceptance))

    parts.append("")
    parts.append(
        "Act as an implementation-focused coding agent. "
        "Execute the necessary edits and commands in the current repository to satisfy the objective "
        "and acceptance criteria. Return a concise JSON summary of what you did. "
        "Only describe actions actually performed; do NOT speculate about environment/ports/config if you did not verify them. "
        "If asked not to modify files or run commands, do nothing and report that no operations were executed."
    )

    return "\n".join(parts)

def _clip(text: Optional[str], limit: int = 800) -> str:
    if not text:
        return ""
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[-limit:]


def _normalize_list(obj: Dict[str, Any], keys: List[str]) -> List[Any]:
    for key in keys:
        value = obj.get(key)
        if isinstance(value, list):
            return value
    return []


def _map_commands(raw_commands: List[Any]) -> List[Dict[str, Any]]:
    mapped = []
    for item in raw_commands:
        if isinstance(item, str):
            mapped.append({
                "command": item,
                "exit_code": None,
                "stdout_excerpt": "",
                "stderr_excerpt": "",
            })
        elif isinstance(item, dict):
            mapped.append({
                "command": item.get("command") or item.get("cmd") or "",
                "exit_code": item.get("exit_code") or item.get("code"),
                "stdout_excerpt": item.get("stdout") or item.get("stdout_excerpt") or "",
                "stderr_excerpt": item.get("stderr") or item.get("stderr_excerpt") or "",
            })
    return mapped


def _map_files(raw_files: List[Any]) -> List[Dict[str, Any]]:
    mapped = []
    for item in raw_files:
        if isinstance(item, str):
            mapped.append({
                "path": item,
                "change_type": "modified",
                "highlights": [],
            })
        elif isinstance(item, dict):
            mapped.append({
                "path": item.get("path") or item.get("file") or "",
                "change_type": item.get("change_type") or item.get("type") or "modified",
                "highlights": item.get("highlights") or item.get("notes") or [],
            })
    return mapped


def _map_issues(raw_issues: List[Any]) -> List[Dict[str, Any]]:
    mapped = []
    for item in raw_issues:
        if isinstance(item, str):
            mapped.append({
                "type": "note",
                "description": item,
                "suggested_action": "",
            })
        elif isinstance(item, dict):
            mapped.append({
                "type": item.get("type") or item.get("category") or "issue",
                "description": item.get("description") or item.get("message") or "",
                "suggested_action": item.get("suggested_action") or item.get("action") or "",
            })
    return mapped


def _normalize_success_output(raw_data: Any, raw_stdout: str) -> Dict[str, Any]:
    base = {
        "status": "success",
        "summary": "",
        "files_changed": [],
        "commands_run": [],
        "tests": {},
        "logs": [],
        "issues": [],
    }

    if isinstance(raw_data, dict):
        status = raw_data.get("status")
        if status:
            base["status"] = status
        base["summary"] = (
            raw_data.get("summary")
            or raw_data.get("message")
            or raw_data.get("result_summary")
            or raw_data.get("result")
            or ""
        )
        base["files_changed"] = _map_files(
            _normalize_list(raw_data, ["files_changed", "files", "changes"])
        )
        base["commands_run"] = _map_commands(
            _normalize_list(raw_data, ["commands_run", "commands", "executed_commands"])
        )
        tests = raw_data.get("tests") or raw_data.get("test_results")
        if isinstance(tests, dict):
            base["tests"] = {
                "passed": tests.get("passed"),
                "details": tests.get("details") or tests.get("summary") or "",
            }
        base["logs"] = raw_data.get("logs") if isinstance(raw_data.get("logs"), list) else []
        if raw_data.get("result") and raw_data.get("result") not in base["logs"]:
            base["logs"].append(str(raw_data.get("result")))
        base["issues"] = _map_issues(
            _normalize_list(raw_data, ["issues", "problems", "warnings"])
        )
    else:
        base["summary"] = str(raw_data)

    if not base["summary"]:
        base["summary"] = _clip(raw_stdout) or "Execution completed"
    if not base["logs"] and raw_stdout.strip():
        base["logs"] = [_clip(raw_stdout)]

    # 如果没有修改文件也没有执行命令，避免模型臆测端口/环境信息，强制使用固定摘要并清空日志/问题
    if not base["files_changed"] and not base["commands_run"]:
        base["summary"] = "No operations executed; no files changed; no commands run."
        base["logs"] = []
        base["issues"] = []

    return base


def _parse_cli_json(raw_text: str) -> Optional[Dict[str, Any]]:
    """Attempts to parse Droid CLI output, tolerating spinner logs."""
    candidate = raw_text.strip()
    if not candidate:
        return None
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        pass

    lines = [line.strip() for line in candidate.splitlines() if line.strip()]
    for line in reversed(lines):
        if line.startswith('{') and line.endswith('}'):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
    return None


def _error_result(status: str, summary: str, cmd: List[str], proc_stdout: str = "", proc_stderr: str = "", issue_type: str = "env_issue") -> Dict[str, Any]:
    command_entry = {
        "command": " ".join(cmd),
        "exit_code": None,
        "stdout_excerpt": _clip(proc_stdout),
        "stderr_excerpt": _clip(proc_stderr),
    }
    logs = [item for item in [_clip(proc_stdout), _clip(proc_stderr)] if item]
    issue = {
        "type": issue_type,
        "description": summary,
        "suggested_action": "Check Droid CLI logs for details.",
    }
    return {
        "status": status,
        "summary": summary,
        "files_changed": [],
        "commands_run": [command_entry],
        "tests": {},
        "logs": logs,
        "issues": [issue],
    }


def handle_execute(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handles the execution request."""
    logger.info("Received execution request")
    
    # === 输入验证 ===
    objective = payload.get("objective", "").strip()
    if not objective:
        logger.warning("Rejected request: empty objective")
        return {
            "status": "error",
            "summary": "Objective 不能为空。请提供明确的任务目标。",
            "files_changed": [],
            "commands_run": [],
            "tests": {},
            "logs": [],
            "issues": [{
                "type": "validation_error",
                "description": "Objective 字段为空或仅包含空白字符",
                "suggested_action": "请在 payload 中提供有效的 objective 字段"
            }]
        }
    
    # 验证输入长度（防止过长导致性能问题）
    if len(objective) > 50000:
        logger.warning(f"Rejected request: objective too long ({len(objective)} chars)")
        return {
            "status": "error",
            "summary": f"Objective 过长 ({len(objective)} 字符)，请限制在 50000 字符以内。",
            "files_changed": [],
            "commands_run": [],
            "tests": {},
            "logs": [],
            "issues": [{
                "type": "validation_error",
                "description": "Objective 长度超过限制",
                "suggested_action": "简化任务描述或拆分为多个子任务"
            }]
        }
    
    instructions = payload.get("instructions", "")
    if len(instructions) > 100000:
        logger.warning(f"Rejected request: instructions too long ({len(instructions)} chars)")
        return {
            "status": "error",
            "summary": f"Instructions 过长 ({len(instructions)} 字符)，请限制在 100000 字符以内。",
            "files_changed": [],
            "commands_run": [],
            "tests": {},
            "logs": [],
            "issues": [{
                "type": "validation_error",
                "description": "Instructions 长度超过限制",
                "suggested_action": "简化指令描述或拆分任务"
            }]
        }
    
    logger.info(f"Objective: {objective[:200]}{'...' if len(objective) > 200 else ''}")
    logger.debug(f"Full payload keys: {list(payload.keys())}")
    
    prompt = build_prompt(payload)
    
    cmd = get_droid_cmd_base() + [prompt]
    
    ctx = payload.get("context") or {}
    if isinstance(ctx, str):
        ctx = {"summary": ctx}
        
    repo_root = ctx.get("repo_root") or "."

    logger.info(f"Executing Droid CLI in {repo_root}")
    logger.info(f"Command: {' '.join(cmd[:3])}... (prompt length: {len(prompt)} chars)")
    logger.info(f"Timeout: {DROID_TIMEOUT}s")
    
    start_time = time.time()
    try:
        proc = subprocess.run(
            cmd,
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
            timeout=DROID_TIMEOUT
        )
        duration = time.time() - start_time
        logger.info(f"Droid execution completed in {duration:.1f}s")
        
        if proc.returncode != 0:
            logger.error(f"Droid CLI failed: {proc.stderr}")
            summary = f"Droid CLI failed with code {proc.returncode}"
            return _error_result(
                status="failed",
                summary=summary,
                cmd=cmd,
                proc_stdout=proc.stdout,
                proc_stderr=proc.stderr,
            )
        
        parsed = _parse_cli_json(proc.stdout)
        if parsed is None:
            logger.warning("Could not parse Droid output as JSON, returning raw text")
            output_data = {"summary": "See logs", "logs": [proc.stdout]}
        else:
            output_data = parsed

        return _normalize_success_output(output_data, proc.stdout)

    except FileNotFoundError:
        logger.error("Droid CLI not found")
        summary = "Droid/Factory CLI not found. Please install droid or set DROID_CLI_CMD."
        return _error_result(
            status="failed",
            summary=summary,
            cmd=cmd,
            issue_type="env_issue",
        )
    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        logger.error(f"Droid execution timed out after {duration:.1f}s (limit: {DROID_TIMEOUT}s)")
        summary = f"Droid 执行超时（{DROID_TIMEOUT}秒）。任务可能过于复杂，建议拆分为更小的子任务。"
        return _error_result(
            status="timeout",
            summary=summary,
            cmd=cmd,
            issue_type="timeout",
        )
    except Exception as e:
        logger.error(f"Error executing Droid: {e}")
        return _error_result(
            status="failed",
            summary=str(e),
            cmd=cmd,
            issue_type="unknown",
        )

if __name__ == "__main__":
    port = int(os.getenv("PORT", "53002"))
    run_server(port, "/execute", handle_execute)
