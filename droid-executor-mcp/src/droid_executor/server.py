"""Droid Executor MCP Server - Implementation-focused coding agent powered by Droid CLI"""
from mcp.server.fastmcp import FastMCP
from .droid_client import call_droid_async
from .scheduler import DAGScheduler

mcp = FastMCP("droid-executor")


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

    Droid Executor 是一个专注于实现的编码代理,能够:
    - 自动编辑代码文件
    - 执行命令和测试
    - 提供执行摘要和日志
    - 检测并报告问题

    Args:
        objective: 任务的主要目标(必填)
        instructions: 详细的执行指令
        context: 上下文信息字典,可包含:
            - files_of_interest: 相关文件列表
            - repo_root: 仓库根目录
            - summary: 背景摘要
        constraints: 约束条件列表(如 "不修改测试文件", "保持向后兼容")
        acceptance_criteria: 验收标准列表(如 "所有测试通过", "代码符合规范")

    Returns:
        执行结果字典,包含:
        - status: 执行状态("success", "failed", "timeout", "error")
        - summary: 执行摘要
        - files_changed: 修改的文件列表(path, change_type, highlights)
        - commands_run: 执行的命令列表(command, exit_code, stdout_excerpt, stderr_excerpt)
        - tests: 测试结果(passed, details)
        - logs: 执行日志
        - issues: 发现的问题列表(type, description, suggested_action)
    """
    return await call_droid_async({
        "objective": objective,
        "instructions": instructions,
        "context": context,
        "constraints": constraints,
        "acceptance_criteria": acceptance_criteria,
    })


@mcp.tool()
async def execute_dag(
    tasks: list[dict],
    context: dict | None = None,
) -> dict:
    """
    并行执行 DAG 任务图。

    支持任务依赖声明,自动拓扑排序,并行执行无依赖任务。
    最大并发数: 8, 单任务超时: 30分钟, 整体超时: 60分钟。

    Args:
        tasks: 任务列表,每个任务包含:
            - id: 任务唯一标识(必填)
            - objective: 任务目标(必填)
            - instructions: 详细指令(可选)
            - depends_on: 依赖的任务ID列表(可选,默认无依赖)
            - constraints: 约束条件列表(可选)
            - acceptance_criteria: 验收标准列表(可选)
        context: 共享上下文,应用于所有任务:
            - repo_root: 仓库根目录
            - files_of_interest: 相关文件列表

    Returns:
        执行结果字典:
        - status: 整体状态("completed", "partial", "failed", "timeout")
        - duration_ms: 总执行时间(毫秒)
        - results: {task_id: task_result} 映射
        - skipped: 因依赖失败而跳过的任务ID列表
        - failed: 执行失败的任务ID列表

    Example:
        result = execute_dag(
            tasks=[
                {"id": "lint", "objective": "运行 lint 检查"},
                {"id": "typecheck", "objective": "运行类型检查"},
                {"id": "test", "objective": "运行测试", "depends_on": ["lint", "typecheck"]},
                {"id": "build", "objective": "构建项目", "depends_on": ["test"]},
            ],
            context={"repo_root": "."}
        )
    """
    if not tasks:
        return {"status": "completed", "duration_ms": 0, "results": {}, "skipped": [], "failed": []}

    scheduler = DAGScheduler(call_droid_async, context or {})
    return await scheduler.submit(tasks)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
