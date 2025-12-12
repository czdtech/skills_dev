# Droid Executor DAG 并行改造计划

## 背景
droid-executor-mcp 原为串行执行，需改造支持 DAG 并行以提升效率。

## 需求确认
- 并发上限：8
- 隔离方案：全局并发池
- 单任务超时：30 分钟
- 整体 DAG 超时：60 分钟
- 范围：仅 droid-executor-mcp

## 架构设计
```
MCP Server (FastMCP)
    └── execute_dag()
            └── DAGScheduler (单例)
                    ├── TaskQueue (asyncio.Queue)
                    └── Worker Pool (8 workers)
                            └── call_droid_async()
```

## 文件变更

### 新增
- `src/droid_executor/scheduler.py` - DAGScheduler + Worker Pool

### 修改
- `src/droid_executor/droid_client.py` - 添加 async 版本
- `src/droid_executor/server.py` - 添加 execute_dag 工具

## API 设计

### execute_dag
```python
execute_dag(
    tasks=[
        {"id": "A", "objective": "任务A"},
        {"id": "B", "objective": "任务B"},
        {"id": "C", "objective": "任务C", "depends_on": ["A", "B"]},
    ],
    context={"repo_root": "."}
)
```

### 返回格式
```python
{
    "status": "completed",  # completed | partial | failed | timeout
    "duration_ms": 45000,
    "results": {"A": {...}, "B": {...}, "C": {...}},
    "skipped": [],
    "failed": [],
}
```

## 执行状态
- [x] 新增 scheduler.py
- [x] 修改 droid_client.py (async)
- [x] 修改 server.py (execute_dag)
- [ ] 测试验证
