"""Codex Advisor MCP Server - Socratic technical review powered by Codex CLI"""
from mcp.server.fastmcp import FastMCP
from .codex_client import call_codex

mcp = FastMCP("codex-advisor")


@mcp.tool()
def ask_codex_advisor(
    problem: str,
    context: str = "",
    candidate_plans: list[dict] | None = None,
    focus_areas: list[str] | None = None,
    questions_for_codex: list[str] | None = None,
    non_goals: list[str] | None = None,
    phase: str = "initial",
    session_id: str | None = None,
    resume_last: bool = False,
) -> dict:
    """
    向 Codex Advisor 咨询技术问题并获得建议。支持多轮会话。

    Codex Advisor 是一个高级技术设计顾问,能够:
    - 分析技术问题和设计决策
    - 评估多个候选方案的优缺点
    - 进行假设验证
    - 提供替代方案
    - 给出权衡分析和推荐

    **会话管理**:
    - 首次调用会创建新会话,返回 session_id
    - 后续调用传入 session_id 可恢复会话上下文
    - 或设置 resume_last=True 自动恢复最近会话

    Args:
        problem: 需要分析的技术问题或设计决策(必填)
        context: 问题的背景上下文信息
        candidate_plans: 候选方案列表,每个方案包含 name, description, assumptions, suspicions 字段
        focus_areas: 需要重点关注的领域(如 "security", "performance", "scalability")
        questions_for_codex: 希望 Codex 回答的具体问题
        non_goals: 明确排除的目标或方向
        phase: 对话阶段("initial", "refinement", "final")
        session_id: 会话 ID,用于恢复之前的对话上下文
        resume_last: 是否恢复最近的会话(当 session_id 未提供时生效)

    Returns:
        苏格拉底式评审结果,包含以下字段:
        - socratic_questions: 引导性问题(挑战假设、引发深度思考)
        - assumption_challenges: 隐藏假设分析(assumption, why_problematic, what_if_wrong)
        - contradictions_revealed: 揭示的矛盾(conflict, tension_between, question_to_resolve)
        - unexplored_paths: 未探索的路径(path, why_worth_exploring, key_question)
        - deeper_inquiry: 深度追问(question, what_it_reveals)
        - guided_insights: 引导性洞察(observation, implication)- 非直接推荐
        - synthesis: 综合总结(key_tensions, critical_unknowns, next_thinking_steps)
        - session_id: 会话 ID(用于后续调用恢复上下文)
    """
    return call_codex({
        "problem": problem,
        "context": context,
        "candidate_plans": candidate_plans,
        "focus_areas": focus_areas,
        "questions_for_codex": questions_for_codex,
        "non_goals": non_goals,
        "phase": phase,
        "session_id": session_id,
        "resume_last": resume_last,
    })


def main():
    mcp.run()


if __name__ == "__main__":
    main()
