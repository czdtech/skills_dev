#!/usr/bin/env python3
import json
import os
import subprocess
import tempfile
from typing import Any, Dict, List

from server_lib import run_server, logger

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
            "key_risks": {
                "type": "array",
                "items": {"type": "string"},
            },
            "recommendation": {"type": "string"},
            "recommendation_confidence": {
                "type": "string",
                "enum": ["low", "medium", "high"],
            },
            "notes": {"type": "string"},
        },
        "required": [
            "clarifying_questions",
            "key_risks",
            "recommendation",
            "recommendation_confidence",
            "notes",
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
    
    prompt = build_prompt(payload)
    schema_path = write_schema_file()
    
    # Create a temp file for the output
    output_fd, output_path = tempfile.mkstemp(suffix=".json")
    os.close(output_fd)
    
    # Construct command: output to the temp file
    cmd = get_codex_cmd_base() + ["--output-schema", schema_path, "-o", output_path]

    try:
        logger.info(f"Running command: {' '.join(cmd)}")
        proc = subprocess.run(
            cmd + [prompt],
            text=True,
            capture_output=True,
            check=False,
        )
        
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
    run_server(3001, "/analyze", handle_analyze)
