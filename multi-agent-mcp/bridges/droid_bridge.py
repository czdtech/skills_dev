#!/usr/bin/env python3
import json
import os
import subprocess
from typing import Any, Dict, List

from server_lib import run_server, logger


def get_droid_cmd_base() -> List[str]:
    """构造 Droid CLI 基础命令.

    优先读取环境变量 DROID_CLI_CMD，例如：
      DROID_CLI_CMD="droid exec --auto low -o json"

    如未配置，则默认启用：
      - 非交互执行：droid exec
      - JSON 输出：-o json
      - 允许安全文件改动：--auto low
    """
    env_cmd = os.getenv("DROID_CLI_CMD")
    if env_cmd:
        return env_cmd.split()
    # 默认允许低风险文件改动，方便在本仓库内真正落地实现
    return ["droid", "exec", "--auto", "low", "-o", "json"]

def build_prompt(payload: Dict[str, Any]) -> str:
    """Constructs natural language prompt for Droid."""
    objective = payload.get("objective") or payload.get("task_id") or "Execute the described task."
    instructions = payload.get("instructions") or ""
    ctx = payload.get("context") or {}
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
        "and acceptance criteria. Return a concise JSON summary of what you did."
    )

    return "\n".join(parts)

def handle_execute(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handles the execution request."""
    logger.info("Received execution request")
    
    prompt = build_prompt(payload)

    # 构造 Droid CLI 命令：
    # - 默认使用 get_droid_cmd_base()，支持通过 DROID_CLI_CMD 覆盖
    # - 例如：DROID_CLI_CMD="droid exec --auto medium -o json"
    cmd = get_droid_cmd_base() + [prompt]
    
    repo_root = "."
    ctx = payload.get("context") or {}
    repo_root = ctx.get("repo_root") or repo_root

    logger.info(f"Running command: {' '.join(cmd)} in {repo_root}")
    
    try:
        # Run the command
        proc = subprocess.run(
            cmd,
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False
        )
        
        if proc.returncode != 0:
            logger.error(f"Droid CLI failed: {proc.stderr}")
            return {
                "status": "error",
                "error": f"Droid CLI failed with code {proc.returncode}",
                "details": proc.stderr
            }
            
        # Parse JSON output if possible
        try:
            output_data = json.loads(proc.stdout)
            return {
                "status": "success",
                "data": output_data
            }
        except json.JSONDecodeError:
            # Fallback to raw text if not JSON
            logger.warning("Could not parse Droid output as JSON, returning raw text")
            return {
                "status": "success",
                "data": {
                    "raw_output": proc.stdout
                }
            }

    except FileNotFoundError:
        logger.error("Droid CLI not found")
        return {
            "status": "error",
            "error": "droid_cli_not_found",
            "message": "Droid/Factory CLI not found. Please install droid or set DROID_CLI_CMD.",
        }
    except Exception as e:
        logger.error(f"Error executing Droid: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

if __name__ == "__main__":
    run_server(3002, "/execute", handle_execute)
