# Droid Executor Skill

独立的 Claude Code Skill，用于执行已规划的编码任务，包含 bridge 服务与辅助脚本。

## 目录结构
- `SKILL.md`：Skill 描述与执行合同指引
- `bridges/`：Python HTTP 服务，封装与 Droid CLI 的通信
- `scripts/`：辅助脚本（pm2 管理、HTTP 调用）
- `docs/`：Droid 协议与输入/输出契约
- `ecosystem.config.js`：pm2 配置文件

## 启动 bridge
```bash
python3 scripts/wrapper_service.py start   # 启动 droid-bridge
python3 scripts/wrapper_service.py status  # 查看状态
python3 scripts/wrapper_service.py stop    # 停止服务
```

## 运行任务
```bash
python3 scripts/wrapper_droid.py "实现登录" --instructions "修改 src/auth/..."
```

## Configuration

The behavior of the Droid Bridge can be configured via environment variables in `ecosystem.config.js`.

### Important: Autonomy Level
By default, Droid requires user confirmation for file modifications. To enable fully automated execution (required for this skill to function as an API), you **must** include `--auto high` (or `--auto medium`) in the `DROID_CLI_CMD` environment variable.

Example `ecosystem.config.js`:
```javascript
module.exports = {
  apps : [{
    name: "droid-bridge",
    script: "bridges/droid_bridge.py",
    interpreter: "python3",
    env: {
      PORT: 3002,
      // CRITICAL: Must include --auto high for unattended execution
      DROID_CLI_CMD: "droid exec --output-format json --auto high",
      // OPTIONAL: Timeout in seconds (default: 600 = 10 minutes)
      DROID_TIMEOUT: "600"
    }
  }]
}
```

### Timeout Configuration
The default timeout is **10 minutes (600 seconds)**. You can customize it via the `DROID_TIMEOUT` environment variable:

- For simple tasks: `DROID_TIMEOUT=300` (5 minutes)
- For complex refactoring: `DROID_TIMEOUT=900` (15 minutes)
- Default (recommended): `DROID_TIMEOUT=600` (10 minutes)

The timeout prevents the system from hanging on overly complex or stuck tasks.

## Dependencies

- `droid` CLI tool installed and in PATH
- Python 3.10+
- Node.js & pm2 (for service management)
