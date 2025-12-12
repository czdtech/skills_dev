# Droid Executor MCP

让 Claude Code 能够调用 Droid CLI 执行编码任务，支持 DAG 并行执行。

## 它能做什么

- 委托编码任务给 Droid 执行
- DAG 并行执行多个任务
- 自动处理任务依赖
- 失败传播（依赖任务自动跳过）

## 快速开始

### 1. 确保你有 Droid CLI

```bash
droid --version
```

### 2. 启用项目级 MCP

编辑 `~/.claude/settings.json`，加一行：

```json
{
  "enableAllProjectMcpServers": true
}
```

### 3. 配置 .mcp.json

在项目根目录创建或编辑 `.mcp.json`：

```json
{
  "mcpServers": {
    "droid-executor": {
      "command": "uvx",
      "args": ["--from", "/你的路径/droid-executor-mcp", "droid-executor"],
      "env": {
        "DROID_MODEL": "custom:MiniMax-M2-0"
      }
    }
  }
}
```

### 4. 重启 Claude Code

```bash
/exit
claude
```

搞定！输入 `/mcp` 应该能看到 droid-executor。

## 怎么用

### 单任务执行

直接跟 Claude 说：

> "用 droid-executor 帮我实现这个功能"

### DAG 并行执行

> "用 execute_dag 并行执行 lint、typecheck，然后运行测试"

## 可选配置

在 `.mcp.json` 的 `env` 里可以调整：

| 变量 | 说明 | 默认 |
|------|------|------|
| `DROID_MODEL` | 用哪个模型 | CLI 默认 |
| `DROID_TIMEOUT` | 单任务超时秒数 | 1800 (30分钟) |
| `DROID_ENABLED_TOOLS` | 启用的工具集 | LS,Read,Glob,Grep,Edit,Create,Execute |
| `DROID_AUTO_LEVEL` | 自动化级别 | high |
| `DROID_REASONING_EFFORT` | 推理深度 | CLI 默认 |
| `DROID_MAX_WORKERS` | DAG 最大并发数 | 8 |
| `DROID_DAG_TIMEOUT` | DAG 整体超时秒数 | 3600 (60分钟) |

完整配置示例：

```json
{
  "droid-executor": {
    "command": "uvx",
    "args": ["--from", "/你的路径/droid-executor-mcp", "droid-executor"],
    "env": {
      "DROID_MODEL": "custom:MiniMax-M2-0",
      "DROID_TIMEOUT": "1800",
      "DROID_ENABLED_TOOLS": "LS,Read,Glob,Grep,Edit,Create,Execute",
      "DROID_AUTO_LEVEL": "high",
      "DROID_MAX_WORKERS": "8",
      "DROID_DAG_TIMEOUT": "3600"
    }
  }
}
```

## 工具说明

### execute_droid_task

单任务执行，参数：
- `objective`: 任务目标（必填）
- `instructions`: 详细指令
- `context`: 上下文（repo_root, files_of_interest）
- `constraints`: 约束条件
- `acceptance_criteria`: 验收标准

### execute_dag

DAG 并行执行，参数：
- `tasks`: 任务列表，每个任务包含 id, objective, depends_on 等
- `context`: 共享上下文

示例：
```python
execute_dag(
    tasks=[
        {"id": "lint", "objective": "运行 lint"},
        {"id": "test", "objective": "运行测试", "depends_on": ["lint"]},
    ],
    context={"repo_root": "."}
)
```

## 遇到问题？

**看不到 droid-executor？**

检查 `~/.claude/settings.json` 里有没有 `"enableAllProjectMcpServers": true`，然后重启。

**uvx 报错？**

```bash
# 手动测试一下
uvx --from /你的路径/droid-executor-mcp droid-executor

# 还不行就清缓存
uv cache clean
```

**超时了？**

复杂任务需要时间，把 `DROID_TIMEOUT` 调大点。

## License

MIT
