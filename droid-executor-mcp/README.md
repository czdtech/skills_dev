# Droid Executor MCP

基于 **MCP (Model Context Protocol)** 的 Droid Executor 服务器，为 Claude Code、Claude Desktop 等 MCP 客户端提供自动化编码执行能力。

## 功能特性

- 🤖 **自动编码**：委托 Droid 自动完成编码任务
- 📝 **文件修改**：自动编辑、创建和删除文件
- ⚡ **命令执行**：运行构建、测试和其他命令
- 📊 **执行报告**：详细的文件变更和命令执行日志
- 🔍 **问题检测**：自动识别执行中的问题

## 架构

```
droid-executor-mcp/
├── mcp_server.py           # FastMCP 服务器
├── bridges/                # Bridge 服务
│   ├── droid_bridge.py     # Droid CLI 封装
│   └── server_lib.py       # HTTP 服务器库
├── ecosystem.config.js     # PM2 配置
└── README.md
```

**通信流程**：
```
MCP 客户端 → mcp_server.py → HTTP → droid_bridge.py → Droid CLI → 执行
```

## 前置要求

1. **Python 3.10+**
2. **Node.js & npm**（用于 Droid CLI 和 PM2）
3. **Droid CLI**：根据官方文档安装
4. **PM2**：`npm install -g pm2`（或使用 npx）

## 安装配置

### 1. 创建虚拟环境并安装依赖

```bash
cd droid-executor-mcp
python3 -m venv .venv
source .venv/bin/activate
pip install mcp httpx
```

### 2. 配置 Droid CLI

确保 `droid` 命令可用：

```bash
droid --version
```

**重要**：Droid 默认需要用户确认文件修改。要使其作为 API 自动执行，必须在 `ecosystem.config.js` 中设置 `--auto` 参数：

```javascript
DROID_CLI_CMD: "droid exec --auto low -o json"
```

自动化级别：
- `--auto low`：仅自动执行读取和低风险操作
- `--auto medium`：允许中等风险的文件修改
- `--auto high`：允许所有操作（谨慎使用）

### 3. 注册到 Claude Code

```bash
claude mcp add --transport stdio droid-executor \
  -- /home/jiang/work/for_claude/skills_dev/droid-executor-mcp/.venv/bin/python \
     /home/jiang/work/for_claude/skills_dev/droid-executor-mcp/mcp_server.py
```

### 4. 验证安装

```bash
claude mcp list
```

应显示 `droid-executor` 服务器。

## 使用方法

### MCP 工具：`execute_droid_task`

委托编码任务给 Droid Executor 执行。

#### 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `objective` | string | ✅ | 任务的主要目标 |
| `instructions` | string | ❌ | 详细的执行指令 |
| `context` | dict | ❌ | 上下文信息 |
| `constraints` | list[str] | ❌ | 约束条件 |
| `acceptance_criteria` | list[str] | ❌ | 验收标准 |

##### `context` 字段

```json
{
  "files_of_interest": ["src/main.py", "tests/test_main.py"],
  "repo_root": "/path/to/project",
  "summary": "背景摘要"
}
```

#### 返回值

```json
{
  "status": "success",  // 或 "failed", "timeout", "error"
  "summary": "执行摘要",
  "files_changed": [
    {
      "path": "src/main.py",
      "change_type": "modified",  // 或 "created", "deleted"
      "highlights": ["添加了 process_data 函数"]
    }
  ],
  "commands_run": [
    {
      "command": "pytest",
      "exit_code": 0,
      "stdout_excerpt": "所有测试通过",
      "stderr_excerpt": ""
    }
  ],
  "tests": {
    "passed": true,
    "details": "10 passed"
  },
  "logs": ["执行日志1", "执行日志2"],
  "issues": [
    {
      "type": "warning",
      "description": "发现的问题",
      "suggested_action": "建议的解决方案"
    }
  ]
}
```

#### 示例

在 Claude Code 中：

```
使用 Droid 实现一个 Fibonacci 数列生成器：
- 在 src/math_utils.py 中创建 fibonacci(n) 函数
- 添加相应的单元测试
- 确保测试通过
```

或使用更结构化的方式：

```python
await execute_droid_task(
    objective="实现 Fibonacci 数列生成器",
    instructions="""
    1. 在 src/math_utils.py 中创建 fibonacci(n) 函数
    2. 使用迭代法实现，避免递归
    3. 添加输入验证（n >= 0）
    """,
    context={
        "files_of_interest": ["src/math_utils.py", "tests/test_math.py"],
        "repo_root": "/home/user/project"
    },
    constraints=["不使用递归", "保持现有代码风格"],
    acceptance_criteria=["单元测试通过", "代码覆盖率 > 90%"]
)
```

## 配置选项

### 环境变量（在 `ecosystem.config.js` 中配置）

- **`DROID_CLI_CMD`**：Droid CLI 命令（**必须包含 `--auto` 参数**）
- **`DROID_TIMEOUT`**：超时时间（秒，默认：600 = 10分钟）
- **`DROID_BRIDGE_URL`**：Bridge 地址（默认：http://localhost:553002）

### 输入限制

- **Objective**：最大 50,000 字符
- **Instructions**：最大 100,000 字符

超出限制会返回验证错误。

### 推荐超时设置

- 简单任务（如创建单个文件）：5 分钟（300s）
- 中等任务（如重构模块）：10 分钟（600s，默认）
- 复杂任务（如大规模重构）：15 分钟（900s）

## 手动管理 Bridge

如需手动控制 bridge 服务（通常不需要，MCP 服务器会自动管理）：

```bash
# 启动
npx pm2 start ecosystem.config.js

# 查看状态
npx pm2 status

# 查看日志
npx pm2 logs droid-bridge

# 停止
npx pm2 stop ecosystem.config.js

# 重启
npx pm2 restart ecosystem.config.js
```

## 故障排查

### MCP 服务器无法启动

1. 检查虚拟环境：`which python`
2. 确认依赖已安装：`pip list | grep mcp`
3. 查看详细日志：`claude mcp list --debug`

### Droid Bridge 无法连接

1. 检查 bridge 状态：`npx pm2 status`
2. 查看 bridge 日志：`npx pm2 logs droid-bridge`
3. 确认端口未被占用：`lsof -i :553002`
4. 测试 bridge：
   ```bash
   curl http://localhost:553002/execute -X POST \
     -H "Content-Type: application/json" \
     -d '{"objective": "test"}'
   ```

### Droid 不执行文件修改

**问题**：Droid 返回成功但没有实际修改文件。

**原因**：`DROID_CLI_CMD` 未设置 `--auto` 参数。

**解决**：在 `ecosystem.config.js` 中添加 `--auto low`（或更高级别）：

```javascript
DROID_CLI_CMD: "droid exec --auto low -o json"
```

然后重启 bridge：

```bash
npx pm2 restart droid-bridge
```

### 执行超时

**问题**：复杂任务经常超时。

**解决**：
1. 增加超时时间：修改 `ecosystem.config.js` 中的 `DROID_TIMEOUT`
2. 拆分任务：将大任务分解为多个小任务
3. 优化指令：提供更具体的文件路径和清晰的步骤

## 安全注意事项

⚠️ **谨慎使用 `--auto high`**：该模式允许 Droid 执行任何操作，包括删除文件和运行系统命令。

建议：
- 开发环境：使用 `--auto medium`
- 生产环境：使用 `--auto low` 或完全禁用自动执行
- 始终在版本控制系统（Git）中工作，便于回滚

## 开发指南

### 修改 MCP 工具

编辑 `mcp_server.py`，在 `@mcp.tool()` 装饰的函数中修改逻辑。

### 修改 Bridge 逻辑

编辑 `bridges/droid_bridge.py`，然后重启 bridge：

```bash
npx pm2 restart droid-bridge
```

### 添加新的输出规范化

在 `droid_bridge.py` 中修改 `_normalize_success_output()` 函数，以适配不同版本的 Droid CLI 输出格式。

## 相关项目

- **droid-executor-skill**：对应的 Claude Code Skill 版本
- **codex-advisor-mcp**：配套的技术顾问 MCP 服务器
- **multi-agent-mcp**：原始的双代理 MCP 服务器（已拆分）

## License

MIT
