#!/usr/bin/env python3
import json
import os
import subprocess
import tempfile
import time
from typing import Any, Dict, List

from server_lib import run_server, logger

# 配置超时时间（默认 30 分钟 = 1800 秒）
# 可通过环境变量 CODEX_TIMEOUT 自定义
CODEX_TIMEOUT = int(os.getenv("CODEX_TIMEOUT", "1800"))

def get_codex_cmd_base() -> List[str]:
    """Constructs Codex CLI base command."""
    env_cmd = os.getenv("CODEX_CLI_CMD")
    if env_cmd:
        return env_cmd.split()
    return ["codex", "exec", "--skip-git-repo-check", "--sandbox", "read-only"]

def build_prompt(payload: Dict[str, Any]) -> str:
    """Constructs natural language prompt for Codex."""
    problem = payload.get("problem") or "(No problem provided)"
    context = payload.get("context") or ""
    candidate_plans = payload.get("candidate_plans") or []
    focus_areas = payload.get("focus_areas") or []
    questions = payload.get("questions_for_codex") or []
    non_goals = payload.get("non_goals") or []
    phase = payload.get("phase") or "initial"

    lines: List[str] = []
    lines.append(
        "You are a senior technical design advisor. "
        "You will receive a JSON object describing a design decision that Claude Code is about to make. "
        "Your job is to carefully analyze it and respond ONLY with a JSON object that matches the provided JSON Schema."
    )
    lines.append("")
    lines.append("Decision request:")
    lines.append(f"- problem: {problem}")
    if context:
        lines.append(f"- context: {context}")
    if focus_areas:
        lines.append(f"- focus_areas: {', '.join(focus_areas)}")
    if questions:
        lines.append("- questions:")
        for q in questions:
            lines.append(f"  • {q}")
    if non_goals:
        lines.append("- non_goals:")
        for item in non_goals:
            lines.append(f"  • {item}")
    lines.append(f"- conversation_phase: {phase}")

    if candidate_plans:
        lines.append("")
        lines.append("Candidate plans:")
        for idx, plan in enumerate(candidate_plans, start=1):
            name = plan.get("name") or f"plan-{idx}"
            desc = plan.get("description") or ""
            assumptions = plan.get("assumptions") or []
            suspicions = plan.get("suspicions") or []
            lines.append(f"- {name}: {desc}")
            if assumptions:
                lines.append(f"  assumptions: {', '.join(assumptions)}")
            if suspicions:
                lines.append(f"  concerns: {', '.join(suspicions)}")

    lines.append("")
    lines.append(
        "Think step by step, but do NOT show your reasoning. "
        "Instead, output a single JSON object that matches the JSON Schema you are given. "
        "Do not include any extra keys, comments, or surrounding text."
    )
    lines.append(
        "The JSON must include clarifying_questions (<=5 strings), assumption_check entries with status among"
        " ['plausible','risky','invalid'], at least one alternative, tradeoffs per dimension, "
        "a recommendation object {preferred_plan, reason, confidence}, followup_suggestions, and raw_text."
    )

    return "\n".join(lines)

def write_schema_file() -> str:
    """Writes JSON Schema file for Codex output."""
    schema: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "clarifying_questions": {
                "type": "array",
                "items": {"type": "string"},
            },
            "assumption_check": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                        "status": {
                            "type": "string",
                            "enum": ["plausible", "risky", "invalid"],
                        },
                        "comment": {"type": "string"},
                    },
                    "required": ["text", "status", "comment"],
                    "additionalProperties": False,
                },
            },
            "alternatives": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "pros": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "cons": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "applicable_when": {"type": "string"},
                    },
                    "required": ["name", "description", "pros", "cons", "applicable_when"],
                    "additionalProperties": False,
                },
            },
            "tradeoffs": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "dimension": {"type": "string"},
                        "notes": {"type": "string"},
                    },
                    "required": ["dimension", "notes"],
                    "additionalProperties": False,
                },
            },
            "recommendation": {
                "type": "object",
                "properties": {
                    "preferred_plan": {"type": "string"},
                    "reason": {"type": "string"},
                    "confidence": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                    },
                },
                "required": ["preferred_plan", "reason", "confidence"],
                "additionalProperties": False,
            },
            "followup_suggestions": {
                "type": "array",
                "items": {"type": "string"},
            },
            "raw_text": {"type": "string"},
        },
        "required": [
            "clarifying_questions",
            "assumption_check",
            "alternatives",
            "tradeoffs",
            "recommendation",
            "followup_suggestions",
            "raw_text",
        ],
        "additionalProperties": False,
    }

    tmp = tempfile.NamedTemporaryFile("w", delete=False, suffix=".schema.json")
    json.dump(schema, tmp)
    tmp.flush()
    tmp.close()
    return tmp.name

def handle_analyze(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handles the analysis request."""
    logger.info("Received analysis request")
    
    # === 输入验证 ===
    problem = payload.get("problem", "").strip()
    if not problem:
        logger.warning("Rejected request: empty problem")
        return {
            "error": "validation_error",
            "message": "Problem field cannot be empty. Please provide a clear problem description."
        }
    
    # 验证输入长度
    if len(problem) > 100000:
        logger.warning(f"Rejected request: problem too long ({len(problem)} chars)")
        return {
            "error": "validation_error",
            "message": f"Problem is too long ({len(problem)} characters). Please limit to 100,000 characters."
        }
    
    context = payload.get("context", "")
    if len(context) > 200000:
        logger.warning(f"Rejected request: context too long ({len(context)} chars)")
        return {
            "error": "validation_error",
            "message": f"Context is too long ({len(context)} characters). Please limit to 200,000 characters."
        }
    
    logger.info(f"Problem: {problem[:200]}{'...' if len(problem) > 200 else ''}")
    logger.debug(f"Full payload keys: {list(payload.keys())}")
    
    prompt = build_prompt(payload)
    schema_path = write_schema_file()
    
    # Create a temp file for the output
    output_fd, output_path = tempfile.mkstemp(suffix=".json")
    os.close(output_fd)
    
    # Construct command: output to the temp file
    cmd = get_codex_cmd_base() + ["--output-schema", schema_path, "-o", output_path]

    logger.info(f"Executing Codex CLI")
    logger.info(f"Command: {' '.join(cmd[:5])}... (prompt length: {len(prompt)} chars)")
    logger.info(f"Timeout: {CODEX_TIMEOUT}s (30 minutes)")
    
    start_time = time.time()
    try:
        proc = subprocess.run(
            cmd + [prompt],
            text=True,
            capture_output=True,
            check=False,
            timeout=CODEX_TIMEOUT  # 使用配置的超时时间
        )
        duration = time.time() - start_time
        logger.info(f"Codex execution completed in {duration:.1f}s")
        
        if proc.returncode != 0:
            logger.error(f"Codex CLI failed with exit code {proc.returncode}")
            logger.error(f"Stderr: {proc.stderr}")
            return {
                "error": "codex_cli_failed",
                "exit_code": proc.returncode,
                "stderr": proc.stderr[-2000:],
            }

        # Read the output from the file
        if os.path.exists(output_path):
            with open(output_path, "r") as f:
                file_content = f.read().strip()
            
            if not file_content:
                logger.warning("Codex output file was empty")
                return {
                    "error": "codex_output_empty",
                    "raw_output": proc.stdout
                }
                
            try:
                parsed = json.loads(file_content)
                return parsed
            except json.JSONDecodeError:
                logger.warning("Codex output file content was not valid JSON")
                return {
                    "error": "codex_output_not_json",
                    "file_content": file_content,
                    "raw_output": proc.stdout,
                }
        else:
            logger.error("Codex output file not found")
            return {
                "error": "codex_output_file_missing",
                "raw_output": proc.stdout
            }

    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        logger.error(f"Codex execution timed out after {duration:.1f}s (limit: {CODEX_TIMEOUT}s)")
        return {
            "error": "timeout",
            "message": f"Codex execution timed out ({CODEX_TIMEOUT}s / 30 minutes). The problem may be too complex. Consider breaking it into smaller questions."
        }
    except FileNotFoundError:
        logger.error("Codex CLI not found")
        return {
            "error": "codex_cli_not_found",
            "message": "Codex CLI not found. Please install @openai/codex or set CODEX_CLI_CMD.",
        }
    finally:
        # Cleanup temp files
        if os.path.exists(schema_path):
            os.unlink(schema_path)
        if os.path.exists(output_path):
            os.unlink(output_path)

if __name__ == "__main__":
    port = int(os.getenv("PORT", "53001"))
    run_server(port, "/analyze", handle_analyze)
