# 🔑 Taskmaster API密钥与配置完全指南

**基于官方文档**: https://docs.task-master.dev  
**GitHub仓库**: https://github.com/eyaltoledano/claude-task-master

---

## 🎯 核心问题解答

### Q1: 必须配置API密钥才可以使用CLI或MCP吗？

**答案**: ❌ **不一定！取决于你的使用方式**

有三种使用模式：

#### 模式A: 纯手动模式（无需API密钥）✅
```bash
# 这些功能完全不需要API密钥
task-master list
task-master next
task-master show <id>
task-master set-status --id=1 --status=done
task-master add-dependency --id=2 --depends-on=1
task-master validate-dependencies
```

**可用功能**:
- ✅ 任务列表和查询
- ✅ 状态更新
- ✅ 依赖管理
- ✅ 标签管理
- ✅ 手动添加子任务
- ✅ 所有非AI功能

**不可用功能**:
- ❌ PRD解析(`parse-prd`)
- ❌ AI任务创建(`add-task`)
- ❌ 任务扩展(`expand`)
- ❌ 复杂度分析(`analyze-complexity`)

---

#### 模式B: CLI本地模式（使用Claude Code/本地LLM）✅

**重要发现**: 支持通过本地CLI配置，**无需API密钥**！

**支持的本地AI Provider**:

##### 1. Claude Code（推荐）🌟
```json
// .taskmaster/config.json
{
  "models": {
    "main": {
      "provider": "claude-code",
      "modelId": "sonnet",
      "maxTokens": 64000,
      "temperature": 0.2
    },
    "research": {
      "provider": "claude-code",
      "modelId": "opus",
      "maxTokens": 32000,
      "temperature": 0.1
    }
  }
}
```

**要求**:
- ✅ Claude Code CLI已安装并认证
- ✅ 可选安装: `npm install @anthropic-ai/claude-code`
- ❌ 不需要API密钥

**优点**:
- 🎉 完全免费（使用本地Claude实例）
- 🎉 所有AI功能可用
- 🎉 已在Claude Code中认证即可

---

##### 2. Ollama（本地开源模型）
```json
// .taskmaster/config.json
{
  "models": {
    "main": {
      "provider": "ollama",
      "modelId": "llama3",
      "maxTokens": 8000
    }
  },
  "global": {
    "ollamaBaseURL": "http://localhost:11434/api"
  }
}
```

**要求**:
- ✅ 本地运行Ollama服务
- ❌ 无需API密钥（除非远程Ollama需要认证）

---

##### 3. Gemini CLI
```json
{
  "models": {
    "main": {
      "provider": "gemini-cli",
      "modelId": "gemini-2.0-flash-exp"
    }
  }
}
```

**要求**:
- ✅ Gemini CLI已安装并通过OAuth认证
- ❌ 不需要API密钥（使用CLI OAuth配置）

---

##### 4. Grok CLI
```json
{
  "models": {
    "main": {
      "provider": "grok-cli",
      "modelId": "grok-4-latest"
    }
  }
}
```

**要求**:
- ✅ Grok CLI已安装并认证
- ❌ 不需要API密钥（使用CLI OAuth配置）

---

#### 模式C: 云端API模式（需要API密钥）
```bash
# AI驱动的高级功能
task-master parse-prd docs/prd.txt --num-tasks=20
task-master expand --id=1 --research
task-master analyze-complexity
```

**需要配置API密钥**

---

### Q2: 配置完API密钥所有功能就都可以使用了吗？

**答案**: ⚠️ **几乎所有，但有细微差别**

完整功能需要:
1. ✅ 至少一个AI Provider API密钥 **或** 本地CLI配置
2. ✅ 对应的AI Provider支持的功能

**最小配置** (推荐):
```bash
# 方式1: 使用Claude Code（无需API密钥）
# 只需配置.taskmaster/config.json使用claude-code provider

# 方式2: 使用API密钥
ANTHROPIC_API_KEY=sk-ant-xxx  # 必需：主功能
PERPLEXITY_API_KEY=pplx-xxx   # 可选：research功能
```

**功能对照**:

| 功能 | 无配置 | Claude Code | Anthropic API | Perplexity API |
|------|--------|-------------|---------------|----------------|
| 基础CLI | ✅ | ✅ | ✅ | ✅ |
| parse-prd | ❌ | ✅ | ✅ | ✅ |
| add-task | ❌ | ✅ | ✅ | ✅ |
| expand | ❌ | ✅ | ✅ | ✅ |
| analyze-complexity | ❌ | ✅ | ✅ | ✅ |
| research (深度) | ❌ | ⚠️ | ⚠️ | ✅ |

---

### Q3: 不同的IDE或CLI适配情况如何？

**答案**: ✅ **全面支持主流IDE和编辑器**

#### 支持的IDE/编辑器:

##### 1. Cursor 🎯
**MCP配置路径**: 
- macOS/Linux: `~/.cursor/mcp.json`
- Windows: `%USERPROFILE%\.cursor\mcp.json`
- 项目级: `<project>/.cursor/mcp.json`

**配置方式**:
```json
{
  "mcpServers": {
    "task-master-ai": {
      "command": "npx",
      "args": ["-y", "task-master-ai"],
      "env": {
        "TASK_MASTER_TOOLS": "standard",
        "ANTHROPIC_API_KEY": "your-key-here"
      }
    }
  }
}
```

**特殊步骤**:
1. 添加配置后打开Cursor设置 (Ctrl+Shift+J)
2. 点击左侧MCP标签
3. 启用`task-master-ai`开关

---

##### 2. Windsurf 🌊
**MCP配置路径**:
- macOS/Linux: `~/.codeium/windsurf/mcp_config.json`
- Windows: `%USERPROFILE%\.codeium\windsurf\mcp_config.json`

**配置格式**: 同Cursor (使用`mcpServers`)

---

##### 3. VS Code (Claude Dev/Continue等) 📝
**MCP配置路径**:
- 项目级: `<project>/.vscode/mcp.json`

**配置方式** (注意差异):
```json
{
  "servers": {  // 注意：VS Code使用"servers"而非"mcpServers"
    "task-master-ai": {
      "command": "npx",
      "args": ["-y", "task-master-ai"],
      "env": {
        "ANTHROPIC_API_KEY": "your-key-here"
      },
      "type": "stdio"  // VS Code需要type字段
    }
  }
}
```

---

##### 4. Claude Code 🤖
**最佳集成**: 原生支持，无需API密钥！

**安装方式**:
```bash
# 使用Claude Code CLI添加MCP服务器
claude mcp add task-master-ai --scope user \
  --env TASK_MASTER_TOOLS="standard" \
  -- npx -y task-master-ai@latest

# 或配置使用本地Claude Code provider
# 编辑.taskmaster/config.json使用claude-code provider
```

**配置.taskmaster/config.json**:
```json
{
  "models": {
    "main": {
      "provider": "claude-code",
      "modelId": "sonnet"
    }
  }
}
```

**在Claude Code聊天中使用**:
```
Initialize taskmaster-ai in my project
Can you parse my PRD at docs/prd.txt?
What's the next task I should work on?
```

---

##### 5. Amazon Q Developer 💼
**MCP配置路径**: `~/.aws/amazonq/mcp.json`
**配置格式**: 同Cursor (使用`mcpServers`)

---

##### 6. Lovable, Roo等其他AI编辑器 🎨
**通用MCP支持**: 查看各编辑器的MCP配置文档
**CLI模式**: 始终可用，使用`task-master`命令

---

## 📋 三种配置方法详解

### 方法1: 项目级.env文件（CLI使用）

**路径**: `<project>/.env`

**创建步骤**:
```bash
# 1. 复制示例文件
cp .env.example .env

# 2. 编辑.env文件
vim .env
```

**内容示例**:
```bash
# 必需：主AI Provider（任选其一）
ANTHROPIC_API_KEY=sk-ant-api03-xxx

# 可选：研究功能增强
PERPLEXITY_API_KEY=pplx-xxx

# 可选：其他Provider
OPENAI_API_KEY=sk-xxx
GOOGLE_API_KEY=AIza-xxx
XAI_API_KEY=xai-xxx
OPENROUTER_API_KEY=sk-or-xxx
MISTRAL_API_KEY=xxx
GROQ_API_KEY=gsk-xxx

# Azure OpenAI（需要两个配置）
AZURE_OPENAI_API_KEY=xxx
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/

# 可选：端点覆盖
OPENAI_BASE_URL=https://api.custom.com/v1
OLLAMA_BASE_URL=http://localhost:11434/api

# Google Vertex AI（需要GCP配置）
VERTEX_PROJECT_ID=your-gcp-project
VERTEX_LOCATION=us-central1
```

**优点**:
- ✅ 项目隔离
- ✅ 易于版本控制（添加到.gitignore）
- ✅ CLI直接读取

**使用**:
```bash
# .env会自动被CLI读取
task-master parse-prd docs/prd.txt
```

---

### 方法2: 系统环境变量

**设置方式**:
```bash
# macOS/Linux (.bashrc, .zshrc等)
export ANTHROPIC_API_KEY="sk-ant-xxx"
export PERPLEXITY_API_KEY="pplx-xxx"

# Windows (PowerShell)
$env:ANTHROPIC_API_KEY="sk-ant-xxx"

# Windows (CMD)
set ANTHROPIC_API_KEY=sk-ant-xxx
```

**优点**:
- ✅ 全局可用
- ✅ 所有项目共享

**缺点**:
- ⚠️ 不适合多账户/多项目
- ⚠️ 需要重启shell生效

---

### 方法3: MCP配置文件（IDE使用）

**用于**: MCP集成（Cursor、Windsurf、VS Code等）

**配置示例** (Cursor/Windsurf):
```json
{
  "mcpServers": {
    "task-master-ai": {
      "command": "npx",
      "args": ["-y", "task-master-ai"],
      "env": {
        // 工具加载配置（可选）
        "TASK_MASTER_TOOLS": "standard",
        
        // API密钥
        "ANTHROPIC_API_KEY": "sk-ant-xxx",
        "PERPLEXITY_API_KEY": "pplx-xxx",
        "OPENAI_API_KEY": "sk-xxx",
        "GOOGLE_API_KEY": "AIza-xxx",
        "XAI_API_KEY": "xai-xxx",
        "OPENROUTER_API_KEY": "sk-or-xxx",
        "MISTRAL_API_KEY": "xxx",
        "GROQ_API_KEY": "gsk-xxx",
        "AZURE_OPENAI_API_KEY": "xxx",
        "OLLAMA_API_KEY": "xxx",
        "GITHUB_API_KEY": "ghp-xxx"
      }
    }
  }
}
```

**VS Code特殊格式**:
```json
{
  "servers": {  // 注意这里
    "task-master-ai": {
      "command": "npx",
      "args": ["-y", "task-master-ai"],
      "env": { /* 同上 */ },
      "type": "stdio"  // VS Code需要
    }
  }
}
```

**优点**:
- ✅ IDE集成，聊天界面直接使用
- ✅ 无需手动输入命令

**重要提示**:
- 🔄 配置后需重启IDE
- 🔍 检查MCP设置中工具是否启用
- ⚠️ 如果显示"0 tools enabled"，检查API密钥

---

## 🎨 工具加载优化（MCP专用）

### TASK_MASTER_TOOLS环境变量

Taskmaster提供36个MCP工具，可选择性加载以优化性能：

```json
{
  "env": {
    "TASK_MASTER_TOOLS": "standard",  // 有4种模式
    "ANTHROPIC_API_KEY": "xxx"
  }
}
```

### 可用模式:

| 模式 | 工具数 | Token占用 | 适用场景 |
|------|--------|-----------|----------|
| `all` | 36 | ~21,000 | 完整功能（默认） |
| `standard` | 15 | ~8,000 | 推荐日常使用 |
| `core` | 7 | ~3,000 | 精简模式 |
| `lean` | 5 | ~2,000 | 最小化 |
| 自定义 | 任意 | 按需 | 逗号分隔工具名 |

### Core工具集（7个）:
```
get_tasks, next_task, get_task, set_task_status, 
update_subtask, parse_prd, expand_task
```

### Standard工具集（15个）:
```
Core工具 + 
initialize_project, analyze_project_complexity, 
expand_all, add_subtask, remove_task, generate, 
add_task, complexity_report
```

### 自定义示例:
```json
{
  "env": {
    "TASK_MASTER_TOOLS": "get_tasks,next_task,set_task_status",
    "ANTHROPIC_API_KEY": "xxx"
  }
}
```

### 推荐配置:
- **新用户**: `standard` - 平衡功能与性能
- **大型项目**: `core` - 减少70% token占用
- **完整功能**: `all` - 无限制（默认）

---

## 🚀 完整配置流程

### 场景1: 使用Claude Code（推荐，无需API密钥）

```bash
# 1. 确保Claude Code已安装并认证
claude --version
# 如果未认证，运行：
claude

# 2. （可选）安装SDK
npm install @anthropic-ai/claude-code

# 3. 配置Taskmaster使用Claude Code
cat > .taskmaster/config.json << 'EOF'
{
  "models": {
    "main": {
      "provider": "claude-code",
      "modelId": "sonnet",
      "maxTokens": 64000,
      "temperature": 0.2
    },
    "research": {
      "provider": "claude-code",
      "modelId": "opus",
      "maxTokens": 32000,
      "temperature": 0.1
    },
    "fallback": {
      "provider": "claude-code",
      "modelId": "sonnet",
      "maxTokens": 64000,
      "temperature": 0.2
    }
  }
}
EOF

# 4. 测试
task-master parse-prd docs/prd.txt --num-tasks=10

# ✅ 完成！所有AI功能可用，无需API密钥
```

---

### 场景2: 使用Anthropic API（需要API密钥）

```bash
# 1. 创建.env文件
cat > .env << 'EOF'
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
PERPLEXITY_API_KEY=pplx-your-key-here  # 可选，用于research
EOF

# 2. 配置.taskmaster/config.json（使用默认即可）
# 默认已配置使用Anthropic

# 3. 测试
task-master parse-prd docs/prd.txt

# ✅ 完成！
```

---

### 场景3: MCP集成（Cursor/Windsurf等）

```bash
# 1. 编辑MCP配置文件
vi ~/.cursor/mcp.json  # 或其他IDE路径

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

# 3. 重启IDE

# 4. 在IDE中打开MCP设置
# Cursor: Ctrl+Shift+J -> MCP -> 启用task-master-ai

# 5. 在聊天中测试
"Initialize taskmaster-ai in my project"
"Can you parse my PRD?"

# ✅ 完成！
```

---

## 🔍 验证配置

### 检查CLI配置:
```bash
# 查看当前配置
cat .taskmaster/config.json

# 测试AI功能
task-master parse-prd docs/prd.txt --num-tasks=3
```

### 检查MCP配置:
```bash
# 查看MCP配置文件
cat ~/.cursor/mcp.json

# 在IDE聊天中运行
"Show me the available taskmaster tools"
```

**成功标志**:
- ✅ MCP设置显示工具数量（非"0 tools enabled"）
- ✅ CLI命令正常执行
- ✅ 无"API key not set"错误

---

## ⚠️ 常见问题

### 问题1: "0 tools enabled" 在MCP设置中
**原因**: API密钥未正确配置或IDE未重启
**解决**:
1. 检查API密钥格式正确
2. 重启IDE
3. 检查MCP配置文件语法

### 问题2: "Required API key ... is not set"
**原因**: 环境变量未加载
**解决**:
- CLI: 检查`.env`文件在项目根目录
- MCP: 检查`mcp.json`中的`env`配置
- 系统环境变量: 重启terminal/IDE

### 问题3: Claude Code模式不工作
**原因**: Claude Code CLI未认证或SDK未安装
**解决**:
```bash
# 1. 认证Claude Code
claude

# 2. 安装SDK
npm install @anthropic-ai/claude-code

# 3. 检查配置
cat .taskmaster/config.json
```

---

## 📊 配置决策树

```
开始
  ↓
你有Claude Code吗？
  ├─ 是 → 使用claude-code provider（无需API密钥）✅
  └─ 否 ↓
  
你有Anthropic API密钥吗？
  ├─ 是 → 配置.env或mcp.json ✅
  └─ 否 ↓
  
你想使用本地模型吗？
  ├─ 是 → 配置Ollama/Gemini CLI/Grok CLI ✅
  └─ 否 → 只使用手动CLI功能（list/next/show等）⚠️
```

---

## 🎯 推荐配置方案

### 方案A: Claude Code用户（最佳）
```json
// .taskmaster/config.json
{
  "models": {
    "main": { "provider": "claude-code", "modelId": "sonnet" },
    "research": { "provider": "claude-code", "modelId": "opus" },
    "fallback": { "provider": "claude-code", "modelId": "sonnet" }
  }
}
```
- ✅ 免费
- ✅ 所有功能
- ✅ 无需API密钥

### 方案B: API密钥用户
```bash
# .env
ANTHROPIC_API_KEY=sk-ant-xxx  # 必需
PERPLEXITY_API_KEY=pplx-xxx   # 推荐
```
- ✅ 所有功能
- ⚠️ 有使用成本

### 方案C: 本地开源模型
```json
// .taskmaster/config.json
{
  "models": {
    "main": { "provider": "ollama", "modelId": "llama3" }
  }
}
```
- ✅ 免费
- ⚠️ 质量取决于模型

---

## 📝 总结

| 问题 | 答案 |
|------|------|
| 必须有API密钥吗？ | ❌ 否，可用Claude Code/Ollama等本地方案 |
| CLI需要API密钥吗？ | 部分需要，基础功能无需，AI功能需要 |
| MCP需要API密钥吗？ | 同CLI，取决于配置的provider |
| 配置API后全功能？ | ✅ 是，至少一个Provider即可 |
| 支持哪些IDE？ | ✅ Cursor、Windsurf、VS Code、Claude Code、Q Developer等 |
| 最佳配置方案？ | Claude Code（免费）或 Anthropic API（稳定） |

**官方文档**: https://docs.task-master.dev  
**配置示例**: https://github.com/eyaltoledano/claude-task-master/tree/main/docs/examples
