# Codex Advisor MCP

基于 **MCP (Model Context Protocol)** 的 Codex Advisor 服务器，为 Claude Code、Claude Desktop 等 MCP 客户端提供高级技术设计咨询能力。

## 功能特性

- 🧠 **深度技术分析**：调用 Codex 进行苏格拉底式评审
- 🔍 **多方案评估**：分析候选方案的优缺点和权衡
- ✅ **假设验证**：检查技术假设的合理性
- 💡 **建议生成**：提供替代方案和改进建议
- 🎯 **聚焦分析**：支持针对特定领域的深入分析

## 架构

```
codex-advisor-mcp/
├── mcp_server.py           # FastMCP 服务器
├── bridges/                # Bridge 服务
│   ├── codex_bridge.py     # Codex CLI 封装
│   └── server_lib.py       # HTTP 服务器库
├── ecosystem.config.js     # PM2 配置
└── README.md
```

**通信流程**：
```
MCP 客户端 → mcp_server.py → HTTP → codex_bridge.py → Codex CLI → Codex API
```

## 前置要求

1. **Python 3.10+**
2. **Node.js & npm**（用于 Codex CLI 和 PM2）
3. **Codex CLI**：`npm install -g @openai/codex`
4. **PM2**：`npm install -g pm2`（或使用 npx）

## 安装配置

### 1. 创建虚拟环境并安装依赖

```bash
cd codex-advisor-mcp
python3 -m venv .venv
source .venv/bin/activate
pip install mcp httpx
```

### 2. 配置 Codex CLI

确保 `codex` 命令可用：

```bash
codex --version
```

如使用自定义路径，修改 `ecosystem.config.js` 中的 `CODEX_CLI_CMD`。

### 3. 注册到 Claude Code

```bash
claude mcp add --transport stdio codex-advisor \
  -- /home/jiang/work/for_claude/skills_dev/codex-advisor-mcp/.venv/bin/python \
     /home/jiang/work/for_claude/skills_dev/codex-advisor-mcp/mcp_server.py
```

### 4. 验证安装

```bash
claude mcp list
```

应显示 `codex-advisor` 服务器。

## 使用方法

### MCP 工具：`ask_codex_advisor`

向 Codex Advisor 咨询技术问题并获取建议。

#### 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `problem` | string | ✅ | 需要分析的技术问题或设计决策 |
| `context` | string | ❌ | 问题的背景上下文 |
| `candidate_plans` | list[dict] | ❌ | 候选方案列表 |
| `focus_areas` | list[str] | ❌ | 重点关注领域（如 security, performance） |
| `questions_for_codex` | list[str] | ❌ | 希望回答的具体问题 |
| `non_goals` | list[str] | ❌ | 明确排除的目标 |
| `phase` | string | ❌ | 对话阶段（initial/refinement/final） |

#### 返回值

```json
{
  "clarifying_questions": ["问题1", "问题2"],
  "assumption_check": [
    {
      "text": "某个假设",
      "status": "plausible",  // 或 "risky", "invalid"
      "comment": "评论"
    }
  ],
  "alternatives": [
    {
      "name": "方案名称",
      "description": "方案描述",
      "pros": ["优点1", "优点2"],
      "cons": ["缺点1", "缺点2"],
      "applicable_when": "适用场景"
    }
  ],
  "tradeoffs": [
    {
      "dimension": "维度",
      "notes": "权衡说明"
    }
  ],
  "recommendation": {
    "preferred_plan": "推荐方案",
    "reason": "推荐理由",
    "confidence": "high"  // 或 "medium", "low"
  },
  "followup_suggestions": ["建议1", "建议2"],
  "raw_text": "完整分析文本"
}
```

#### 示例

在 Claude Code 中：

```
请使用 Codex Advisor 分析：我应该选择 REST 还是 GraphQL 作为 API 设计？
背景是一个需要支持移动端和 Web 端的社交应用。
```

## 配置选项

### 环境变量（在 `ecosystem.config.js` 中配置）

- **`CODEX_CLI_CMD`**：Codex CLI 命令（默认：自动检测）
- **`CODEX_TIMEOUT`**：超时时间（秒，默认：1800 = 30分钟）
- **`CODEX_BRIDGE_URL`**：Bridge 地址（默认：http://localhost:553001）

### 输入限制

- **Problem**：最大 100,000 字符
- **Context**：最大 200,000 字符

超出限制会返回验证错误。

## 手动管理 Bridge

如需手动控制 bridge 服务（通常不需要，MCP 服务器会自动管理）：

```bash
# 启动
npx pm2 start ecosystem.config.js

# 查看状态
npx pm2 status

# 查看日志
npx pm2 logs codex-bridge

# 停止
npx pm2 stop ecosystem.config.js

# 重启
npx pm2 restart ecosystem.config.js
```

## 故障排查

### MCP 服务器无法启动

1. 检查虚拟环境是否激活：`which python`
2. 确认依赖已安装：`pip list | grep mcp`
3. 查看 Claude Code 日志：`claude mcp list --debug`

### Codex Bridge 无法连接

1. 检查 bridge 状态：`npx pm2 status`
2. 查看 bridge 日志：`npx pm2 logs codex-bridge`
3. 确认端口未被占用：`lsof -i :553001`
4. 测试 bridge：`curl http://localhost:553001/analyze -X POST -d '{"problem": "test"}'`

### Codex CLI 错误

1. 确认 Codex CLI 已安装：`codex --version`
2. 检查网络代理设置（bridge 会清除代理环境变量）
3. 查看 Codex CLI 文档：`codex --help`

## 开发指南

### 修改 MCP 工具

编辑 `mcp_server.py`，在 `@mcp.tool()` 装饰的函数中修改逻辑。

### 修改 Bridge 逻辑

编辑 `bridges/codex_bridge.py`，然后重启 bridge：

```bash
npx pm2 restart codex-bridge
```

### 调试 MCP 通信

MCP 服务器的日志默认输出到 stderr，可在 Claude Code 的错误信息中查看。

## 相关项目

- **codex-advisor-skill**：对应的 Claude Code Skill 版本
- **droid-executor-mcp**：配套的执行代理 MCP 服务器
- **multi-agent-mcp**：原始的双代理 MCP 服务器（已拆分）

## License

MIT
