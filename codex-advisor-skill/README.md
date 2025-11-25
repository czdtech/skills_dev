# Codex Advisor Skill

独立的 Claude Code Skill，专注于在关键设计决策点调用 Codex 进行苏格拉底式评审。

## 目录结构
- `SKILL.md`：Skill 元数据与使用说明
- `bridges/`：Python HTTP 服务，负责与 Codex CLI 交互
- `scripts/`：辅助脚本（启动/停止 bridge、手动触发）
- `docs/`：协议与输入输出契约
- `ecosystem.config.js`：pm2 配置（仅包含 codex-bridge）

## 启动 bridge
```bash
python3 scripts/wrapper_service.py start   # 启动 codex-bridge
python3 scripts/wrapper_service.py status  # 查看状态
python3 scripts/wrapper_service.py stop    # 停止服务
```

## 测试调用
```bash
python3 scripts/wrapper_codex.py "选择数据库" --context "现有系统..."
```

## Configuration

The behavior of the Codex Bridge can be configured via environment variables in `ecosystem.config.js`.

### Timeout Configuration

- **Default timeout**: 30 minutes (1800 seconds)
- Codex advisor tasks typically involve deep reasoning and may take longer than execution tasks
- Customizable via `CODEX_TIMEOUT` environment variable

Example `ecosystem.config.js`:
```javascript
module.exports = {
  apps : [{
    name: "codex-bridge",
    script: "bridges/codex_bridge.py",
    interpreter: "python3",
    env: {
      PORT: 3001,
      // OPTIONAL: Timeout in seconds (default: 1800 = 30 minutes)
      CODEX_TIMEOUT: "1800",
      // OPTIONAL: Custom Codex CLI command
      CODEX_CLI_CMD: "codex exec --skip-git-repo-check --sandbox read-only"
    }
  }]
}
```

### Input Validation

- **Problem**: Required, maximum 100,000 characters
- **Context**: Optional, maximum 200,000 characters
- Empty or excessively long inputs will be rejected with clear error messages

## 依赖
- Python 3.10+
- Codex CLI 已安装并可在 PATH 中调用（或设置 `CODEX_CLI_CMD`）
- Node.js + pm2（用于管理 bridge）
