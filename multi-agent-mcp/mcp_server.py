import asyncio
import httpx
import os
import subprocess
import sys
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("Multi-Agent Studio")

import atexit

# Lifecycle Management
def startup():
    """Start PM2 services when MCP server starts."""
    try:
        print("Starting Multi-Agent Studio services...", file=sys.stderr)
        subprocess.run(["npx", "pm2", "start", "ecosystem.config.js"], check=True, cwd=os.path.dirname(os.path.abspath(__file__)))
    except subprocess.CalledProcessError as e:
        print(f"Failed to start services: {e}", file=sys.stderr)

def shutdown():
    """Stop PM2 services when MCP server stops."""
    try:
        print("Stopping Multi-Agent Studio services...", file=sys.stderr)
        subprocess.run(["npx", "pm2", "stop", "ecosystem.config.js"], check=True, cwd=os.path.dirname(os.path.abspath(__file__)))
    except subprocess.CalledProcessError as e:
        print(f"Failed to stop services: {e}", file=sys.stderr)

# Register shutdown hook
atexit.register(shutdown)

# Run startup immediately
startup()

# Configuration
CODEX_BRIDGE_URL = os.getenv("CODEX_BRIDGE_URL", "http://localhost:53001")
DROID_BRIDGE_URL = os.getenv("DROID_BRIDGE_URL", "http://localhost:53002")

@mcp.tool()
async def ask_codex_advisor(
    problem: str,
    context: str = "",
    candidate_plans: list[dict] | None = None,
    focus_areas: list[str] | None = None,
) -> dict:
    """
    Ask Codex Advisor to analyze a technical problem and provide recommendations.
    
    Args:
        problem: The technical problem or decision to analyze.
        context: Background context for the problem.
        candidate_plans: List of potential solutions (optional).
        focus_areas: Specific areas to focus the analysis on (e.g., "security", "performance").
    """
    payload = {
        "problem": problem,
        "context": context,
        "candidate_plans": candidate_plans or [],
        "focus_areas": focus_areas or []
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{CODEX_BRIDGE_URL}/analyze",
                json=payload,
                timeout=120.0,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "error": "codex_bridge_error",
                "message": str(e),
            }


@mcp.tool()
async def execute_droid_task(
    objective: str,
    instructions: str = "",
    context: dict | None = None,
) -> dict:
    """
    Delegate a coding task to Droid Executor.
    
    Args:
        objective: The main goal of the task.
        instructions: Detailed instructions for execution.
        context: Context dictionary (e.g., {"files_of_interest": [...]}).
    """
    payload = {
        "objective": objective,
        "instructions": instructions,
        "context": context or {}
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{DROID_BRIDGE_URL}/execute",
                json=payload,
                timeout=300.0,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "error": "droid_bridge_error",
                "message": str(e),
            }


if __name__ == "__main__":
    mcp.run()
