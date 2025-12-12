"""DAG Scheduler - 任务队列 + Worker Pool 实现并行执行"""
import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import os

# 配置（支持环境变量）
MAX_WORKERS = int(os.getenv("DROID_MAX_WORKERS", "8"))
DAG_TIMEOUT = int(os.getenv("DROID_DAG_TIMEOUT", "3600"))  # 60 分钟整体超时


class TaskStatus(Enum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"


@dataclass
class Task:
    id: str
    objective: str
    instructions: str = ""
    depends_on: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    acceptance_criteria: list[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    result: dict[str, Any] = field(default_factory=dict)


class DAGScheduler:
    """DAG 调度器 - 管理任务队列和 Worker Pool"""

    def __init__(self, executor_fn, context: dict | None = None):
        self.executor_fn = executor_fn  # async callable
        self.context = context or {}
        self.tasks: dict[str, Task] = {}
        self.queue: asyncio.Queue[str] = asyncio.Queue()
        self.completed: set[str] = set()
        self.lock = asyncio.Lock()

    async def submit(self, task_defs: list[dict]) -> dict[str, Any]:
        """提交 DAG 任务并等待完成"""
        start_time = time.time()

        # 解析任务（检查重复 ID）
        seen_ids = set()
        for t in task_defs:
            tid = t.get("id")
            if not tid:
                return {"status": "failed", "error": "Task missing 'id' field", "results": {}, "skipped": [], "failed": []}
            if tid in seen_ids:
                return {"status": "failed", "error": f"Duplicate task id: '{tid}'", "results": {}, "skipped": [], "failed": []}
            seen_ids.add(tid)

            task = Task(
                id=tid,
                objective=t.get("objective", ""),
                instructions=t.get("instructions", ""),
                depends_on=t.get("depends_on", []),
                constraints=t.get("constraints", []),
                acceptance_criteria=t.get("acceptance_criteria", []),
            )
            self.tasks[task.id] = task

        # 验证依赖
        if err := self._validate_dag():
            return {"status": "failed", "error": err, "results": {}, "skipped": [], "failed": []}

        # 入队无依赖任务
        for task in self.tasks.values():
            if not task.depends_on:
                task.status = TaskStatus.QUEUED
                await self.queue.put(task.id)

        # 启动 Workers
        workers = [
            asyncio.create_task(self._worker(i))
            for i in range(min(MAX_WORKERS, len(self.tasks)))
        ]

        # 等待完成或超时
        try:
            await asyncio.wait_for(self._wait_all(), timeout=DAG_TIMEOUT)
        except asyncio.TimeoutError:
            for task in self.tasks.values():
                if task.status in (TaskStatus.PENDING, TaskStatus.QUEUED):
                    task.status = TaskStatus.TIMEOUT

        # 取消 Workers
        for w in workers:
            w.cancel()

        return self._build_result(time.time() - start_time)

    def _validate_dag(self) -> str | None:
        """验证 DAG 无环且依赖存在"""
        for task in self.tasks.values():
            for dep in task.depends_on:
                if dep not in self.tasks:
                    return f"Task '{task.id}' depends on unknown task '{dep}'"

        # 检测环
        visited, rec_stack = set(), set()

        def has_cycle(tid: str) -> bool:
            visited.add(tid)
            rec_stack.add(tid)
            for dep in self.tasks[tid].depends_on:
                if dep not in visited and has_cycle(dep):
                    return True
                if dep in rec_stack:
                    return True
            rec_stack.remove(tid)
            return False

        for tid in self.tasks:
            if tid not in visited and has_cycle(tid):
                return "DAG contains cycle"
        return None

    async def _worker(self, worker_id: int):
        """Worker 协程 - 从队列取任务执行"""
        while True:
            try:
                task_id = await self.queue.get()
                task = self.tasks[task_id]
                task.status = TaskStatus.RUNNING

                # 执行任务
                payload = {
                    "objective": task.objective,
                    "instructions": task.instructions,
                    "context": self.context,
                    "constraints": task.constraints,
                    "acceptance_criteria": task.acceptance_criteria,
                }
                result = await self.executor_fn(payload)
                task.result = result
                task.status = (
                    TaskStatus.SUCCESS if result.get("status") == "success"
                    else TaskStatus.FAILED
                )

                # 更新完成状态并释放依赖
                async with self.lock:
                    self.completed.add(task_id)
                    await self._release_dependents(task_id)

                self.queue.task_done()
            except asyncio.CancelledError:
                break

    async def _release_dependents(self, completed_id: str):
        """释放依赖已完成任务的后续任务"""
        completed_task = self.tasks[completed_id]

        for task in self.tasks.values():
            if task.status != TaskStatus.PENDING:
                continue
            if completed_id not in task.depends_on:
                continue

            # 检查是否所有依赖都完成
            all_deps_done = all(d in self.completed for d in task.depends_on)
            any_dep_failed = any(
                self.tasks[d].status in (TaskStatus.FAILED, TaskStatus.SKIPPED, TaskStatus.TIMEOUT)
                for d in task.depends_on
            )

            if any_dep_failed:
                task.status = TaskStatus.SKIPPED
                self.completed.add(task.id)
            elif all_deps_done:
                task.status = TaskStatus.QUEUED
                await self.queue.put(task.id)

    async def _wait_all(self):
        """等待所有任务完成"""
        while len(self.completed) < len(self.tasks):
            await asyncio.sleep(0.1)

    def _build_result(self, duration: float) -> dict[str, Any]:
        """构建返回结果"""
        results = {}
        skipped = []
        failed = []

        for task in self.tasks.values():
            results[task.id] = task.result or {"status": task.status.value}
            if task.status == TaskStatus.SKIPPED:
                skipped.append(task.id)
            elif task.status in (TaskStatus.FAILED, TaskStatus.TIMEOUT):
                failed.append(task.id)

        all_success = not skipped and not failed
        has_success = any(t.status == TaskStatus.SUCCESS for t in self.tasks.values())

        if all_success:
            status = "completed"
        elif has_success:
            status = "partial"
        else:
            status = "failed"

        return {
            "status": status,
            "duration_ms": int(duration * 1000),
            "results": results,
            "skipped": skipped,
            "failed": failed,
        }
