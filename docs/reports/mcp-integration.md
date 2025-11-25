# MCP集成完整指南

> **目标**: 在不同IDE中配置Taskmaster MCP服务器  
> **最后更新**: 2025-11-24  
> **来源**: 合并 .taskmaster/reports 中的MCP相关文档

---

## 🎯 MCP是什么?

**Model Context Protocol (MCP)**: Anthropic开发的协议,让AI编辑器能够调用外部工具

**Taskmaster MCP Server**: 提供40+工具,让Claude Code在对话中直接管理任务

---

## 🔧 支持的IDE/编辑器

| IDE | 配置文件路径 | 配置格式 |
|-----|------------|---------|
| **Cursor** | `~/.cursor/mcp.json` | `mcpServers` |
| **Windsurf** | `~/.codeium/windsurf/mcp_config.json` | `mcpServers` |
| **VS Code** | `.vscode/mcp.json` | `servers` +`type` |
| **Claude Code** | CLI配置或`~/.claude/mcp.json` | 原生支持 |
| **Amazon Q** | `~/.aws/amazonq/mcp.json` | `mcpServers` |

---

## 📋 配置方法

### 1. Cursor配置

**路径**: `~/.cursor/mcp.json`

```json
{
  "mcpServers": {
    "task-master-ai": {
      "command": "npx",
      "args": ["-y", "task-master-ai"],
      "env": {
        "TASK_MASTER_TOOLS": "standard",
        "ANTHROPIC_API_KEY": "sk-ant-xxx"
      }
    }
  }
}
```

**激活步骤**:
1. 添加配置
2. 重启Cursor
3. 打开设置 (Ctrl+Shift+J)
4. 点击MCP标签
5. 启用`task-master-ai`开关

---

### 2. Windsurf配置

**路径**: `~/.codeium/windsurf/mcp_config.json`

配置格式同Cursor,使用`mcpServers`键

---

### 3. VS Code配置

**路径**: `.vscode/mcp.json` (项目级)

```json
{
  "servers": {  // 注意: VS Code使用"servers"
    "task-master-ai": {
      "command": "npx",
      "args": ["-y", "task-master-ai"],
      "env": {
        "ANTHROPIC_API_KEY": "sk-ant-xxx"
      },
      "type": "stdio"  // VS Code需要type字段
    }
  }
}
```

---

### 4. Claude Code配置(推荐)

**方法1: CLI添加**
```bash
claude mcp add task-master-ai --scope user \
  --env TASK_MASTER_TOOLS="standard" \
  -- npx -y task-master-ai@latest
```

**方法2: 配置使用本地provider(无需API密钥)**
```json
// .taskmaster/config.json
{
  "models": {
    "main": {
      "provider": "claude-code",
      "modelId": "sonnet"
    }
  }
}
```

---

## 🎨 工具加载优化

### TASK_MASTER_TOOLS环境变量

| 模式 | 工具数 | Token占用 | 适用场景 |
|------|-------|-----------|---------|
| `all` | 36 | ~21,000 | 完整功能(默认) |
| `standard` | 15 | ~8,000 | 推荐日常使用 |
| `core` | 7 | ~3,000 | 精简模式 |
| `lean` | 5 | ~2,000 | 最小化 |

**推荐**: 使用`standard`模式平衡功能与性能

---

## ✅ 验证配置

### 检查MCP设置

**成功标志**:
- ✅ MCP设置显示工具数量(非"0 tools enabled")
- ✅ CLI命令正常执行
- ✅ 无"API key not set"错误

### 测试命令

```bash
# 查看MCP配置
cat ~/.cursor/mcp.json

# 在IDE聊天中运行
"Show me the available taskmaster tools"
"Initialize taskmaster-ai in my project"
```

---

## ⚠️ 常见问题

### 问题1: "0 tools enabled"

**原因**: API密钥未正确配置或IDE未重启

**解决**:
1. 检查API密钥格式
2. 重启IDE
3. 检查MCP配置文件语法

---

### 问题2: "Required API key is not set"

**原因**: 环境变量未加载

**解决**:
- CLI: 检查`.env`文件在项目根目录
- MCP: 检查`mcp.json`中的`env`配置
- 系统环境变量: 重启terminal/IDE

---

### 问题3: "server name not found"

**原因**: 服务器名称不匹配或未启动

**解决**:
1. 检查配置中的服务器名称一致
2. 重启IDE加载配置
3. 检查`npx`命令可用性

---

## 🚀 使用示例

### 在IDE对话中使用

```
你: "Initialize taskmaster-ai in my project"
→ Claude调用initialize_project工具

你: "Can you parse my PRD at docs/requirements.md?"
→ Claude调用parse_prd工具

你: "What's the next task I should work on?"
→ Claude调用next_task工具

你: "Mark tasks 1,2,3 as done"
→ Claude调用set_task_status工具
```

---

## 📊 可用MCP工具(standard模式)

**核心工具**:
- `get_tasks` - 获取任务列表
- `next_task` - 获取下一个任务
- `get_task` - 获取任务详情
- `set_task_status` - 更新任务状态
- `update_subtask` - 更新子任务

**AI增强工具**:
- `parse_prd` - 解析PRD文档
- `expand_task` - 扩展任务为子任务
- `analyze_project_complexity` - 分析项目复杂度
- `add_task` - 智能添加任务

**管理工具**:
- `initialize_project` - 初始化项目
- `add_subtask` - 添加子任务
- `remove_task` - 删除任务

---

## 🎯 最佳实践

### 1. 选择合适的工具模式

- **新用户**: `standard` - 平衡功能与性能
- **大型项目**: `core` - 减少70% token占用
- **完整功能**: `all` - 无限制

### 2. API密钥管理

- 项目级: 使用`.env`文件(gitignore)
- 全局级: 配置在MCP文件中
- 推荐: 使用Claude Code provider(无需API密钥)

### 3. 工作流集成

- MCP模式适合: 对话式任务管理
- CLI模式适合: 批量处理和自动化
- 两者结合: 获得最佳体验

---

## 📝 总结

| 问题 | 答案 |
|------|------|
| MCP需要API密钥吗? | 取决于配置的provider |
| 支持哪些IDE? | Cursor/Windsurf/VS Code/Claude Code/Q Developer等 |
| 最佳配置方案? | Claude Code(免费)或Anthropic API(稳定) |
| 如何优化性能? | 使用`standard`工具模式 |

---

**相关文档**:
- [API配置指南](./configuration.md)
- [Taskmaster完整集成](../integration/taskmaster-integration.md)
- [Taskmaster能力测试](./taskmaster-tests.md)
