# Codex Advisor MCP

让 Claude Code 能够调用 Codex 进行苏格拉底式技术评审。

不给你答案，而是用问题引导你思考得更深。

## 它能做什么

- 挑战你的假设："你确定这个前提成立吗？"
- 揭示隐藏矛盾："这两个目标是否冲突？"
- 探索未知路径："有没有考虑过这个方向？"
- 持续深入讨论：支持多轮会话

## 快速开始

### 1. 确保你有 Codex CLI

```bash
codex --version
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
    "codex-advisor": {
      "command": "uvx",
      "args": ["--from", "/你的路径/codex-advisor-mcp", "codex-advisor"],
      "env": {
        "CODEX_MODEL": "o3"
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

搞定！输入 `/mcp` 应该能看到 codex-advisor。

## 怎么用

直接跟 Claude 说：

> "用 codex-advisor 帮我评审一下这个架构设计"

或者更具体：

> "请 codex advisor 分析微服务拆分方案，重点关注可扩展性"

它会返回一堆引导性问题和洞察，而不是直接告诉你"应该怎么做"。

### 多轮对话

第一次调用会返回 `session_id`，后续可以：

- 传入这个 ID 继续讨论
- 或者用 `resume_last: true` 自动接上

## 可选配置

在 `.mcp.json` 的 `env` 里可以调整：

| 变量 | 说明 | 默认 |
|------|------|------|
| `CODEX_MODEL` | 用哪个模型（o3, gpt-5.2 等） | CLI 默认 |
| `CODEX_TIMEOUT` | 超时秒数 | 1800 (30分钟) |
| `CODEX_SANDBOX` | 沙箱模式（read-only, workspace-write） | read-only |
| `CODEX_REASONING_EFFORT` | 思考深度（minimal, low, medium, high） | CLI 默认 |
| `CODEX_SKIP_GIT_CHECK` | 跳过 git 仓库检查 | true |

完整配置示例：

```json
{
  "codex-advisor": {
    "command": "uvx",
    "args": ["--from", "/你的路径/codex-advisor-mcp", "codex-advisor"],
    "env": {
      "CODEX_MODEL": "gpt-5.2",
      "CODEX_TIMEOUT": "1800",
      "CODEX_SANDBOX": "read-only",
      "CODEX_REASONING_EFFORT": "high",
      "CODEX_SKIP_GIT_CHECK": "true"
    }
  }
}

## 遇到问题？

**看不到 codex-advisor？**

检查 `~/.claude/settings.json` 里有没有 `"enableAllProjectMcpServers": true`，然后重启。

**uvx 报错？**

```bash
# 手动测试一下
uvx --from /你的路径/codex-advisor-mcp codex-advisor

# 还不行就清缓存
uv cache clean
```

**超时了？**

复杂问题确实需要时间，把 `CODEX_TIMEOUT` 调大点。

**返回了奇怪的 raw_output？**

这是 Codex CLI 输出异常，检查下 CLI 版本和网络。

## 设计理念

这是个"薄封装"——尽量简单，直接调 CLI，错误透明暴露。

适合：本地开发、个人使用

不适合：多人共享服务、批量自动化

## License

MIT
