"""Codex CLI client - subprocess 直连调用 Codex CLI"""
import json
import os
import re
import subprocess
import tempfile
from typing import Any

# 环境变量配置
CODEX_TIMEOUT = int(os.getenv("CODEX_TIMEOUT", "1800"))  # 超时（秒），默认 30 分钟
CODEX_MODEL = os.getenv("CODEX_MODEL")  # 模型，如 gpt-5.1-codex-max, o3
CODEX_SANDBOX = os.getenv("CODEX_SANDBOX", "read-only")  # 沙箱模式: read-only, workspace-write
CODEX_REASONING_EFFORT = os.getenv("CODEX_REASONING_EFFORT")  # 推理程度: minimal, low, medium, high
CODEX_SKIP_GIT_CHECK = os.getenv("CODEX_SKIP_GIT_CHECK", "true").lower() == "true"  # 跳过 git 仓库检查
CODEX_EXTRA_FLAGS = os.getenv("CODEX_EXTRA_FLAGS", "")  # 额外 CLI 参数

# 系统角色提示（可通过环境变量自定义）
DEFAULT_SYSTEM_PROMPT = """You are a Socratic technical mentor. Your role is NOT to give direct answers or recommendations. \
Instead, guide the user to discover the best solution through:
1. Thought-provoking questions that challenge assumptions
2. Revealing hidden contradictions or logical inconsistencies
3. Exploring unexplored alternatives and edge cases
4. Deep 'why' questions that uncover root causes

IMPORTANT: Do NOT recommend a specific solution. Help the user think more deeply and discover insights themselves."""

CODEX_SYSTEM_PROMPT = os.getenv("CODEX_SYSTEM_PROMPT", DEFAULT_SYSTEM_PROMPT)

# 会话 ID 存储
_last_session_id: str | None = None


def get_codex_cmd(session_id: str | None = None, resume_last: bool = False) -> list[str]:
    """构建 Codex CLI 命令。"""
    is_resume = bool(session_id or resume_last)

    if session_id:
        cmd = ["codex", "exec", "resume", session_id]
    elif resume_last:
        cmd = ["codex", "exec", "resume", "--last"]
    else:
        if env_cmd := os.getenv("CODEX_CLI_CMD"):
            return env_cmd.split()
        cmd = ["codex", "exec", "--sandbox", CODEX_SANDBOX]
        if CODEX_SKIP_GIT_CHECK:
            cmd.append("--skip-git-repo-check")

    # resume 模式不支持 --model 参数
    if not is_resume and CODEX_MODEL:
        cmd.extend(["--model", CODEX_MODEL])

    # 添加推理程度参数
    if CODEX_REASONING_EFFORT:
        cmd.extend(["-c", f"model_reasoning_effort=\"{CODEX_REASONING_EFFORT}\""])

    # 添加额外参数
    if CODEX_EXTRA_FLAGS:
        cmd.extend(CODEX_EXTRA_FLAGS.split())

    return cmd


def extract_session_id(output: str) -> str | None:
    """从 Codex CLI 输出中提取会话 ID。"""
    patterns = [
        r"Session ID:\s*([a-f0-9-]+)",
        r"session[_-]?id[:\s]+([a-f0-9-]+)",
        r'"conversationId":\s*"([^"]+)"',
        r'"threadId":\s*"([^"]+)"',
    ]
    for pattern in patterns:
        if match := re.search(pattern, output, re.IGNORECASE):
            return match.group(1)
    return None


def build_prompt(payload: dict[str, Any]) -> str:
    """构建苏格拉底式提示词。"""
    problem = payload.get("problem") or "(No problem provided)"
    context = payload.get("context") or ""
    candidate_plans = payload.get("candidate_plans") or []
    focus_areas = payload.get("focus_areas") or []
    questions = payload.get("questions_for_codex") or []
    non_goals = payload.get("non_goals") or []
    phase = payload.get("phase") or "initial"

    lines = [
        CODEX_SYSTEM_PROMPT,
        "",
        "Design decision to examine:",
        f"- problem: {problem}",
    ]
    if context:
        lines.append(f"- context: {context}")
    if focus_areas:
        lines.append(f"- focus_areas: {', '.join(focus_areas)}")
    if questions:
        lines.append("- user_questions:")
        lines.extend(f"  • {q}" for q in questions)
    if non_goals:
        lines.append("- non_goals:")
        lines.extend(f"  • {item}" for item in non_goals)
    lines.append(f"- conversation_phase: {phase}")

    if candidate_plans:
        lines.extend(["", "Candidate plans to examine:"])
        for idx, plan in enumerate(candidate_plans, start=1):
            name = plan.get("name") or f"plan-{idx}"
            desc = plan.get("description") or ""
            lines.append(f"- {name}: {desc}")
            if assumptions := plan.get("assumptions"):
                lines.append(f"  assumptions: {', '.join(assumptions)}")
            if suspicions := plan.get("suspicions"):
                lines.append(f"  concerns: {', '.join(suspicions)}")

    lines.extend([
        "",
        "CRITICAL: You MUST respond with ONLY a JSON object using EXACTLY these keys (no other keys allowed):\n"
        "{\n"
        '  "socratic_questions": ["Question that challenges thinking...", ...],\n'
        '  "assumption_challenges": [{"assumption": "...", "why_problematic": "...", "what_if_wrong": "..."}, ...],\n'
        '  "contradictions_revealed": [{"conflict": "...", "tension_between": "...", "question_to_resolve": "..."}, ...],\n'
        '  "unexplored_paths": [{"path": "...", "why_worth_exploring": "...", "key_question": "..."}, ...],\n'
        '  "deeper_inquiry": [{"question": "Why...?", "what_it_reveals": "..."}, ...],\n'
        '  "guided_insights": [{"observation": "...", "implication": "..."}, ...],\n'
        '  "synthesis": {"key_tensions": "...", "critical_unknowns": "...", "next_thinking_steps": "..."}\n'
        "}\n\n"
        "DO NOT include: recommendation, preferred_plan, alternatives, clarifying_questions, or any direct advice.\n"
        "Your role is to GUIDE thinking, not to GIVE answers."
    ])
    return "\n".join(lines)


def write_schema_file() -> str:
    """写入 JSON Schema 文件。"""
    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "socratic_questions": {"type": "array", "items": {"type": "string"}},
            "assumption_challenges": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "assumption": {"type": "string"},
                        "why_problematic": {"type": "string"},
                        "what_if_wrong": {"type": "string"},
                    },
                    "required": ["assumption", "why_problematic", "what_if_wrong"],
                },
            },
            "contradictions_revealed": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "conflict": {"type": "string"},
                        "tension_between": {"type": "string"},
                        "question_to_resolve": {"type": "string"},
                    },
                    "required": ["conflict", "tension_between", "question_to_resolve"],
                },
            },
            "unexplored_paths": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "path": {"type": "string"},
                        "why_worth_exploring": {"type": "string"},
                        "key_question": {"type": "string"},
                    },
                    "required": ["path", "why_worth_exploring", "key_question"],
                },
            },
            "deeper_inquiry": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "question": {"type": "string"},
                        "what_it_reveals": {"type": "string"},
                    },
                    "required": ["question", "what_it_reveals"],
                },
            },
            "guided_insights": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "observation": {"type": "string"},
                        "implication": {"type": "string"},
                    },
                    "required": ["observation", "implication"],
                },
            },
            "synthesis": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "key_tensions": {"type": "string"},
                    "critical_unknowns": {"type": "string"},
                    "next_thinking_steps": {"type": "string"},
                },
                "required": ["key_tensions", "critical_unknowns", "next_thinking_steps"],
            },
        },
        "required": [
            "socratic_questions", "assumption_challenges", "contradictions_revealed",
            "unexplored_paths", "deeper_inquiry", "guided_insights", "synthesis",
        ],
    }
    tmp = tempfile.NamedTemporaryFile("w", delete=False, suffix=".schema.json")
    json.dump(schema, tmp)
    tmp.close()
    return tmp.name


def call_codex(payload: dict[str, Any]) -> dict[str, Any]:
    """调用 Codex CLI 并返回结果。"""
    global _last_session_id

    session_id = payload.get("session_id")
    resume_last = payload.get("resume_last", False)
    is_resume = bool(session_id or resume_last)

    prompt = build_prompt(payload)
    cmd = get_codex_cmd(session_id=session_id, resume_last=resume_last)

    schema_path = output_path = None
    if not is_resume:
        schema_path = write_schema_file()
        fd, output_path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        cmd += ["--output-schema", schema_path, "-o", output_path]

    try:
        proc = subprocess.run(
            cmd + [prompt],
            text=True,
            capture_output=True,
            timeout=CODEX_TIMEOUT,
        )

        if proc.returncode != 0:
            return {"error": "codex_cli_failed", "exit_code": proc.returncode, "stderr": proc.stderr[-2000:]}

        # 读取输出
        content = ""
        if output_path and os.path.exists(output_path):
            with open(output_path) as f:
                content = f.read().strip()
        elif is_resume:
            content = proc.stdout.strip()

        if not content:
            return {"error": "codex_output_empty", "raw_output": proc.stdout}

        # 解析 JSON
        try:
            result = json.loads(content)
        except json.JSONDecodeError:
            result = {"raw_text": content}

        # 提取会话 ID
        if new_id := extract_session_id(proc.stdout) or extract_session_id(proc.stderr):
            _last_session_id = new_id
            result["session_id"] = new_id
        elif session_id:
            result["session_id"] = session_id
        elif _last_session_id:
            result["session_id"] = _last_session_id

        return result

    except subprocess.TimeoutExpired:
        return {"error": "timeout", "message": f"Codex execution timed out ({CODEX_TIMEOUT}s)"}
    except FileNotFoundError:
        return {"error": "codex_cli_not_found", "message": "Codex CLI not found"}
    finally:
        if schema_path and os.path.exists(schema_path):
            os.unlink(schema_path)
        if output_path and os.path.exists(output_path):
            os.unlink(output_path)
