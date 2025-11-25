#!/usr/bin/env python3
import asyncio
import httpx
import os
import subprocess
import sys
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("Codex Advisor")

import atexit

# Configuration
CODEX_BRIDGE_URL = os.getenv("CODEX_BRIDGE_URL", "http://localhost:53001")

# Lifecycle Management
def startup():
    """Start Codex Bridge when MCP server starts."""
    try:
        print("Starting Codex Advisor bridge service...", file=sys.stderr)
        subprocess.run(
            ["npx", "pm2", "start", "ecosystem.config.js"],
            check=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        print("Codex Advisor bridge started successfully.", file=sys.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Failed to start Codex bridge: {e}", file=sys.stderr)

def shutdown():
    """Stop Codex Bridge when MCP server stops."""
    try:
        print("Stopping Codex Advisor bridge service...", file=sys.stderr)
        subprocess.run(
            ["npx", "pm2", "stop", "ecosystem.config.js"],
            check=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        print("Codex Advisor bridge stopped successfully.", file=sys.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Failed to stop Codex bridge: {e}", file=sys.stderr)

# Register shutdown hook
atexit.register(shutdown)

# Run startup immediately
startup()


@mcp.tool()
async def ask_codex_advisor(
    problem: str,
    context: str = "",
    candidate_plans: list[dict] | None = None,
    focus_areas: list[str] | None = None,
    questions_for_codex: list[str] | None = None,
    non_goals: list[str] | None = None,
    phase: str = "initial",
) -> dict:
    """
    向 Codex Advisor 咨询技术问题并获得建议。
    
    Codex Advisor 是一个高级技术设计顾问，能够：
    - 分析技术问题和设计决策
    - 评估多个候选方案的优缺点
    - 进行假设验证
    - 提供替代方案
    - 给出权衡分析和推荐
    
    Args:
        problem: 需要分析的技术问题或设计决策（必填）
        context: 问题的背景上下文信息
        candidate_plans: 候选方案列表，每个方案包含 name, description, assumptions, suspicions 字段
        focus_areas: 需要重点关注的领域（如 "security", "performance", "scalability"）
        questions_for_codex: 希望 Codex 回答的具体问题
        non_goals: 明确排除的目标或方向
        phase: 对话阶段（"initial", "refinement", "final"）
    
    Returns:
        包含以下字段的分析结果：
        - clarifying_questions: 澄清性问题列表
        - assumption_check: 假设验证结果（status: plausible/risky/invalid）
        - alternatives: 替代方案列表
        - tradeoffs: 权衡分析
        - recommendation: 推荐方案（preferred_plan, reason, confidence）
        - followup_suggestions: 后续建议
        - raw_text: 原始分析文本
    
    Example:
        result = await ask_codex_advisor(
            problem="选择用户认证方案",
            context="一个需要支持10万用户的SaaS应用",
            candidate_plans=[
                {
                    "name": "JWT",
                    "description": "使用 JSON Web Tokens",
                    "assumptions": ["无状态架构", "短有效期"],
                    "suspicions": ["token 刷新复杂度"]
                }
            ],
            focus_areas=["security", "scalability"]
        )
    """
    payload = {
        "problem": problem,
        "context": context,
        "candidate_plans": candidate_plans or [],
        "focus_areas": focus_areas or [],
        "questions_for_codex": questions_for_codex or [],
        "non_goals": non_goals or [],
        "phase": phase,
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{CODEX_BRIDGE_URL}/analyze",
                json=payload,
                timeout=1850.0,  # 略长于 bridge 的 1800s 超时
            )
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException:
            return {
                "error": "timeout",
                "message": "Codex 分析超时。问题可能过于复杂，建议分解为更小的问题。",
            }
        except httpx.HTTPStatusError as e:
            return {
                "error": "bridge_error",
                "message": f"Codex Bridge 返回错误: {e.response.status_code}",
                "details": e.response.text[:500],
            }
        except Exception as e:
            return {
                "error": "connection_error",
                "message": f"无法连接到 Codex Bridge: {str(e)}",
            }


if __name__ == "__main__":
    mcp.run()
