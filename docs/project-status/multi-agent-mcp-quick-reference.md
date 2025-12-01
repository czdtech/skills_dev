# Multi-Agent MCP 快速参考

## 📦 项目总览

| 项目 | 类型 | 端口 | 主要功能 | 使用场景 |
|------|------|------|---------|----------|
| `codex-advisor-skill` | Skill | 53001 | 技术设计咨询 | Claude Code |
| `codex-advisor-mcp` | MCP | 53001 | 技术设计咨询 | 任何 MCP 客户端 |
| `droid-executor-skill` | Skill | 53002 | 自动化编码 | Claude Code |
| `droid-executor-mcp` | MCP | 53002 | 自动化编码 | 任何 MCP 客户端 |

## ⚡ 快速安装

```bash
# Codex Advisor MCP
cd codex-advisor-mcp && ./setup.sh

# Droid Executor MCP
cd droid-executor-mcp && ./setup.sh

# 注册到 Claude Code
claude mcp add --transport stdio codex-advisor \
  -- $(pwd)/codex-advisor-mcp/.venv/bin/python \
     $(pwd)/codex-advisor-mcp/mcp_server.py

claude mcp add --transport stdio droid-executor \
  -- $(pwd)/droid-executor-mcp/.venv/bin/python \
     $(pwd)/droid-executor-mcp/mcp_server.py
```

## 🔧 常用命令

### MCP 管理
```bash
# 查看已安装的 MCP 服务器
claude mcp list

# 删除 MCP 服务器
claude mcp remove codex-advisor
claude mcp remove droid-executor
```

### Bridge 管理
```bash
# 查看 PM2 状态
npx pm2 status

# 查看日志
npx pm2 logs codex-bridge
npx pm2 logs droid-bridge

# 重启 bridge
npx pm2 restart codex-bridge
npx pm2 restart droid-bridge

# 停止所有
npx pm2 stop all
```

## 💬 使用示例

### Codex Advisor
```
请使用 Codex Advisor 分析：
我应该选择 PostgreSQL 还是 MongoDB 作为数据库？
这是一个社交应用，需要支持 10 万用户。
```

### Droid Executor
```
使用 Droid 实现以下功能：
在 src/utils.py 中创建一个 fibonacci(n) 函数，
使用迭代法实现，并添加单元测试。
```

## 🛠️ 工具参数

### ask_codex_advisor

```python
ask_codex_advisor(
    problem: str,              # 必填：技术问题或设计决策
    context: str = "",         # 可选：背景信息
    candidate_plans: list[dict] | None = None,  # 可选：候选方案
    focus_areas: list[str] | None = None,       # 可选：关注领域
    questions_for_codex: list[str] | None = None,  # 可选：具体问题
    non_goals: list[str] | None = None,         # 可选：排除目标
    phase: str = "initial"     # 可选：对话阶段
) -> dict
```

### execute_droid_task

```python
execute_droid_task(
    objective: str,            # 必填：任务目标
    instructions: str = "",    # 可选：详细指令
    context: dict | None = None,  # 可选：上下文信息
    constraints: list[str] | None = None,      # 可选：约束条件
    acceptance_criteria: list[str] | None = None  # 可选：验收标准
) -> dict
```

## 📊 配置参数

### Codex Advisor
| 参数 | 默认值 | 说明 |
|------|--------|------|
| `CODEX_BRIDGE_URL` | http://localhost:553001 | Bridge 地址 |
| `CODEX_TIMEOUT` | 1800s (30分钟) | 超时时间 |
| `CODEX_CLI_CMD` | `codex exec --skip-git-repo-check --sandbox read-only` | CLI 命令 |

### Droid Executor
| 参数 | 默认值 | 说明 |
|------|--------|------|
| `DROID_BRIDGE_URL` | http://localhost:553002 | Bridge 地址 |
| `DROID_TIMEOUT` | 600s (10分钟) | 超时时间 |
| `DROID_CLI_CMD` | `droid exec --auto low -o json` | CLI 命令（**必须含 --auto**） |

## 🐛 故障排查

### MCP 无法连接
```bash
# 1. 检查 bridge 状态
npx pm2 status

# 2. 查看日志
npx pm2 logs

# 3. 重启 bridge
npx pm2 restart all

# 4. 测试 bridge
curl http://localhost:553001/analyze -X POST -d '{"problem":"test"}'
curl http://localhost:553002/execute -X POST -d '{"objective":"test"}'
```

### Droid 不执行文件修改
**原因**：未设置 `--auto` 参数

**解决**：编辑 `droid-executor-mcp/ecosystem.config.js`：
```javascript
DROID_CLI_CMD: "droid exec --auto low -o json"
```

然后重启：
```bash
npx pm2 restart droid-bridge
```

### 端口冲突
**原因**：同时运行了 Skill 版本和 MCP 版本

**解决**：
```bash
# 停止所有 PM2 进程
npx pm2 stop all
npx pm2 delete all

# 只启动需要的版本
cd codex-advisor-mcp
npx pm2 start ecosystem.config.js
```

## 📁 文件位置

### 配置文件
- `ecosystem.config.js` - PM2 配置（CLI 命令、超时等）
- `mcp_server.py` - MCP 服务器（工具定义）
- `bridges/*.py` - Bridge 实现

### 日志文件
- PM2 日志：`~/.pm2/logs/`
- MCP 日志：stderr（由 Claude Code 显示）

### 虚拟环境
- `.venv/` - Python 虚拟环境（不提交到 Git）

## 📚 文档链接

- [Codex Advisor MCP README](../codex-advisor-mcp/README.md)
- [Droid Executor MCP README](../droid-executor-mcp/README.md)
- [迁移指南](./multi-agent-mcp-migration-guide.md)
- [架构对齐分析](./multi-agent-architecture-alignment.md)
- [拆分总结](./multi-agent-mcp-split-summary.md)

## 🔄 同步 Bridge 代码

```bash
# 从 Skill 同步到 MCP
cp codex-advisor-skill/bridges/*.py codex-advisor-mcp/bridges/
cp droid-executor-skill/bridges/*.py droid-executor-mcp/bridges/

# 重启 bridge
npx pm2 restart all
```

## 💡 最佳实践

1. ✅ **使用虚拟环境**：每个 MCP 独立安装依赖
2. ✅ **版本控制 CLI 路径**：在 `ecosystem.config.js` 中明确指定
3. ✅ **监控日志**：定期检查 PM2 日志排查问题
4. ✅ **测试后部署**：先在开发环境测试再用于生产
5. ✅ **备份配置**：`ecosystem.config.js` 包含重要配置

## ⚠️ 注意事项

- 🚫 不能同时运行 Skill 和 MCP 版本（端口冲突）
- ⚠️ Droid **必须**设置 `--auto` 参数才能自动执行
- ⚠️ 修改 `ecosystem.config.js` 后需重启 bridge
- 💾 定期备份 `ecosystem.config.js`（包含 CLI 路径等重要配置）
- 🔒 谨慎使用 `--auto high`（允许危险操作）

## 🎯 选择指南

### 使用 Skill 版本（如果）
- ✅ 只在 Claude Code 中使用
- ✅ 需要辅助脚本（wrapper_service.py, wrapper_codex.py 等）
- ✅ 需要深度集成 Claude Code 功能

### 使用 MCP 版本（如果）
- ✅ 需要在多个客户端使用（Claude Desktop, VS Code, 等）
- ✅ 希望自动管理 bridge 生命周期
- ✅ 希望统一的 MCP 接口

### 可以并存（但不同时运行）
- 开发环境：Skill 版本
- Claude Desktop：MCP 版本
- 通过切换 PM2 配置避免端口冲突

---

**快速帮助**：如有问题，先查看各项目的 README.md，或参考故障排查章节。
