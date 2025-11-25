#!/usr/bin/env python3
import asyncio
import httpx
import os
import subprocess
import sys
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("Droid Executor")

import atexit

# Configuration
DROID_BRIDGE_URL = os.getenv("DROID_BRIDGE_URL", "http://localhost:53002")

# Lifecycle Management
def startup():
    """Start Droid Bridge when MCP server starts."""
    try:
        print("Starting Droid Executor bridge service...", file=sys.stderr)
        subprocess.run(
            ["npx", "pm2", "start", "ecosystem.config.js"],
            check=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        print("Droid Executor bridge started successfully.", file=sys.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Failed to start Droid bridge: {e}", file=sys.stderr)

def shutdown():
    """Stop Droid Bridge when MCP server stops."""
    try:
        print("Stopping Droid Executor bridge service...", file=sys.stderr)
        subprocess.run(
            ["npx", "pm2", "stop", "ecosystem.config.js"],
            check=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        print("Droid Executor bridge stopped successfully.", file=sys.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Failed to stop Droid bridge: {e}", file=sys.stderr)

# Register shutdown hook
atexit.register(shutdown)

# Run startup immediately
startup()


@mcp.tool()
async def execute_droid_task(
    objective: str,
    instructions: str = "",
    context: dict | None = None,
    constraints: list[str] | None = None,
    acceptance_criteria: list[str] | None = None,
) -> dict:
    """
    委托编码任务给 Droid Executor 执行。
    
    Droid Executor 是一个专注于实现的编码代理，能够：
    - 自动编辑代码文件
    - 执行命令和测试
    - 提供执行摘要和日志
    - 检测并报告问题
    
    Args:
        objective: 任务的主要目标（必填）
        instructions: 详细的执行指令
        context: 上下文信息字典，可包含：
            - files_of_interest: 相关文件列表
            - repo_root: 仓库根目录
            - summary: 背景摘要
        constraints: 约束条件列表（如 "不修改测试文件", "保持向后兼容"）
        acceptance_criteria: 验收标准列表（如 "所有测试通过", "代码符合规范"）
    
    Returns:
        执行结果字典，包含：
        - status: 执行状态（"success", "failed", "timeout", "error"）
        - summary: 执行摘要
        - files_changed: 修改的文件列表（path, change_type, highlights）
        - commands_run: 执行的命令列表（command, exit_code, stdout_excerpt, stderr_excerpt）
        - tests: 测试结果（passed, details）
        - logs: 执行日志
        - issues: 发现的问题列表（type, description, suggested_action）
    
    Example:
        result = await execute_droid_task(
            objective="实现用户注册功能",
            instructions="在 src/auth/register.py 中添加 register_user 函数",
            context={
                "files_of_interest": ["src/auth/register.py", "tests/test_auth.py"],
                "repo_root": "/path/to/project"
            },
            constraints=["保持现有 API 兼容"],
            acceptance_criteria=["单元测试通过", "代码覆盖率>80%"]
        )
    """
    payload = {
        "objective": objective,
        "instructions": instructions,
        "context": context or {},
        "constraints": constraints or [],
        "acceptance_criteria": acceptance_criteria or [],
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{DROID_BRIDGE_URL}/execute",
                json=payload,
                timeout=650.0,  # 略长于 bridge 的 600s 超时
            )
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException:
            return {
                "status": "timeout",
                "summary": "Droid 执行超时。任务可能过于复杂，建议拆分为更小的子任务。",
                "files_changed": [],
                "commands_run": [],
                "tests": {},
                "logs": [],
                "issues": [{
                    "type": "timeout",
                    "description": "执行超过 10 分钟限制",
                    "suggested_action": "将任务分解为多个较小的子任务"
                }]
            }
        except httpx.HTTPStatusError as e:
            return {
                "status": "error",
                "summary": f"Droid Bridge 返回错误: {e.response.status_code}",
                "files_changed": [],
                "commands_run": [],
                "tests": {},
                "logs": [e.response.text[:500]],
                "issues": [{
                    "type": "bridge_error",
                    "description": f"HTTP {e.response.status_code}",
                    "suggested_action": "检查 Droid Bridge 服务状态"
                }]
            }
        except Exception as e:
            return {
                "status": "error",
                "summary": f"无法连接到 Droid Bridge: {str(e)}",
                "files_changed": [],
                "commands_run": [],
                "tests": {},
                "logs": [],
                "issues": [{
                    "type": "connection_error",
                    "description": str(e),
                    "suggested_action": "确认 Droid Bridge 服务正在运行（端口 3002）"
                }]
            }


if __name__ == "__main__":
    mcp.run()
