# Taskmaster 配置快速参考

## 你的核心问题答案 ✅

### 1️⃣ 必须配置API密钥才可以使用CLI或MCP吗？

**❌ 不一定！**

```
基础CLI功能（无需API密钥）:
✅ task-master list
✅ task-master next  
✅ task-master show
✅ task-master set-status
✅ 所有手动管理功能

AI增强功能（需要配置）:
⚠️ task-master parse-prd
⚠️ task-master expand
⚠️ task-master analyze-complexity
⚠️ task-master add-task --prompt="..."
```

---

### 2️⃣ 如何启用AI功能但不用API密钥？

**🌟 方案A: 使用Claude Code（推荐）**

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

**要求**: 
- Claude Code CLI已安装并认证
- 可选: `npm install @anthropic-ai/claude-code`
- ✅ 免费使用所有AI功能！

**🔧 方案B: 使用Ollama本地模型**

```json
// .taskmaster/config.json
{
  "models": {
    "main": {
      "provider": "ollama",
      "modelId": "llama3"
    }
  }
}
```

**要求**:
- 本地运行Ollama服务
- ✅ 完全免费

**其他本地方案**:
- Gemini CLI (使用OAuth认证)
- Grok CLI (使用CLI配置)

---

### 3️⃣ 如何配置API密钥？

**方式1: 项目级.env文件（CLI使用）**

```bash
# 创建.env文件
echo "ANTHROPIC_API_KEY=sk-ant-xxx" > .env
echo "PERPLEXITY_API_KEY=pplx-xxx" >> .env  # 可选

# 使用
task-master parse-prd docs/prd.txt
```

**方式2: MCP配置（IDE集成）**

```json
// ~/.cursor/mcp.json （Cursor）
// ~/.codeium/windsurf/mcp_config.json （Windsurf）
// <project>/.vscode/mcp.json （VS Code）
{
  "mcpServers": {  // VS Code使用"servers"
    "task-master-ai": {
      "command": "npx",
      "args": ["-y", "task-master-ai"],
      "env": {
        "TASK_MASTER_TOOLS": "standard",  // 可选优化
        "ANTHROPIC_API_KEY": "sk-ant-xxx"
      }
    }
  }
}
```

**重要**: 配置后需重启IDE！

---

### 4️⃣ 配置完API密钥所有功能就可用了吗？

**✅ 是的！只要配置了至少一个AI Provider**

**最小配置**:
```bash
# 方式1: 使用Claude Code（推荐）
# 无需API密钥，只需配置config.json

# 方式2: 使用API密钥
ANTHROPIC_API_KEY=sk-ant-xxx  # 仅需这一个
```

**增强配置**:
```bash
ANTHROPIC_API_KEY=sk-ant-xxx      # 主功能
PERPLEXITY_API_KEY=pplx-xxx       # 深度research功能
```

---

### 5️⃣ 不同IDE的适配情况

| IDE/编辑器 | MCP路径 | 配置格式 | 特殊要求 |
|-----------|---------|---------|---------|
| **Cursor** | `~/.cursor/mcp.json` | `mcpServers` | 需在设置中启用 |
| **Windsurf** | `~/.codeium/windsurf/mcp_config.json` | `mcpServers` | - |
| **VS Code** | `<project>/.vscode/mcp.json` | `servers` | 需`type: stdio` |
| **Claude Code** | CLI配置 | - | 原生支持，无需密钥 |
| **Amazon Q** | `~/.aws/amazonq/mcp.json` | `mcpServers` | - |

**VS Code特殊格式示例**:
```json
{
  "servers": {  // 注意不是mcpServers
    "task-master-ai": {
      "command": "npx",
      "args": ["-y", "task-master-ai"],
      "env": { ... },
      "type": "stdio"  // VS Code需要此字段
    }
  }
}
```

---

## 🚀 快速开始指南

### 场景1: 我有Claude Code（最简单）

```bash
# 1. 编辑配置
vi .taskmaster/config.json

# 2. 设置provider为claude-code
{
  "models": {
    "main": { "provider": "claude-code", "modelId": "sonnet" }
  }
}

# 3. 直接使用
task-master parse-prd docs/prd.txt

# ✅ 完成！无需API密钥
```

---

### 场景2: 我有Anthropic API密钥

```bash
# 1. 创建.env
echo "ANTHROPIC_API_KEY=sk-ant-xxx" > .env

# 2. 使用（config.json默认已配置anthropic）
task-master parse-prd docs/prd.txt

# ✅ 完成！
```

---

### 场景3: 我想在Cursor中使用

```bash
# 1. 编辑MCP配置
vi ~/.cursor/mcp.json

# 2. 添加配置
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

# 3. 重启Cursor

# 4. 打开Cursor设置 (Ctrl+Shift+J)
#    -> MCP标签 -> 启用task-master-ai

# 5. 在聊天中使用
"Initialize taskmaster in my project"

# ✅ 完成！
```

---

## MCP工具优化（可选）

### TASK_MASTER_TOOLS环境变量

减少token占用，优化性能：

```json
{
  "env": {
    "TASK_MASTER_TOOLS": "standard",  // 推荐
    "ANTHROPIC_API_KEY": "xxx"
  }
}
```

**可选值**:
- `"all"` - 36工具，~21K tokens（默认）
- `"standard"` - 15工具，~8K tokens（推荐）
- `"core"` - 7工具，~3K tokens（精简）
- `"lean"` - 5工具，~2K tokens（最小）
- `"get_tasks,next_task,..."` - 自定义

**Core工具集**: `get_tasks`, `next_task`, `get_task`, `set_task_status`, `update_subtask`, `parse_prd`, `expand_task`

---

## 🔍 验证配置是否成功

### CLI验证:
```bash
# 测试AI功能
task-master parse-prd docs/prd.txt --num-tasks=3

# 成功标志：无"API key not set"错误
```

### MCP验证:
```bash
# 1. 查看IDE的MCP设置
# 应显示工具数量（不是"0 tools enabled"）

# 2. 在聊天中测试
"Show me available taskmaster tools"
"What's the next task?"
```

---

## ⚠️ 故障排除

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| "0 tools enabled" | API密钥未配置或IDE未重启 | 1. 检查密钥<br>2. 重启IDE |
| "API key not set" | 环境变量未加载 | 1. 检查.env位置<br>2. 检查mcp.json语法 |
| Claude Code不工作 | CLI未认证 | 运行`claude`进行认证 |

---

## 📊 配置决策树

```
开始
  ↓
需要AI功能？
  ├─ 否 → 使用基础CLI（list/next/show等）
  └─ 是 ↓
  
有Claude Code？
  ├─ 是 → 配置claude-code provider ✅ 最佳方案
  └─ 否 ↓
  
有API密钥？
  ├─ 是 → 配置.env或mcp.json ✅
  └─ 否 ↓
  
使用本地模型？
  ├─ 是 → 配置Ollama/Gemini CLI ✅
  └─ 否 → 只用基础功能 ⚠️
```

---

## 🎯 推荐方案总结

| 方案 | 成本 | 功能 | 配置难度 | 推荐度 |
|------|------|------|---------|--------|
| **Claude Code** | 免费 | 完整 | ⭐ | ⭐⭐⭐⭐⭐ |
| **Anthropic API** | 付费 | 完整 | ⭐ | ⭐⭐⭐⭐ |
| **Ollama** | 免费 | 取决模型 | ⭐⭐ | ⭐⭐⭐ |
| **手动模式** | 免费 | 基础 | - | ⭐⭐ |

---

## 📚 相关文档

- **完整配置指南**: `API_CONFIGURATION_GUIDE.md`
- **快速参考**: `QUICK_REFERENCE.md`
- **能力测试报告**: `TASKMASTER_CAPABILITY_TEST_SUMMARY.md`
- **官方文档**: https://docs.task-master.dev
- **GitHub仓库**: https://github.com/eyaltoledano/claude-task-master
