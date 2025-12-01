# 项目合规性报告

> **最后更新**: 2025-11-28

## 项目状态总览

| 项目 | 类型 | 端口 | 标准 | 状态 |
|------|------|------|------|------|
| codex-advisor-skill | Skill | 53001 | Claude Code Skills 规范 | ✅ 符合 |
| codex-advisor-mcp | MCP | 53001 | MCP 项目惯例 | ✅ 符合 |
| droid-executor-skill | Skill | 53002 | Claude Code Skills 规范 | ✅ 符合 |
| droid-executor-mcp | MCP | 53002 | MCP 项目惯例 | ✅ 符合 |

---

## Skill 项目结构

```
{skill-name}/
├── SKILL.md                    # 技能入口 (name, description, license)
├── LICENSE.txt                 # Apache 2.0 许可证
├── ecosystem.config.cjs        # PM2 配置
├── scripts/
│   ├── wrapper_{name}.py       # 命令行封装
│   └── bridge/
│       ├── {name}_bridge.py    # HTTP Bridge 服务
│       └── server_lib.py       # 服务器库
└── references/
    └── {name}-protocol.md      # 协议文档
```

## MCP 项目结构

```
{name}-mcp/
├── mcp_server.py               # MCP 服务器入口
├── ecosystem.config.cjs        # PM2 配置
├── requirements.txt            # Python 依赖
├── setup.sh                    # 安装脚本
├── README.md                   # 项目说明
└── bridges/
    ├── {name}_bridge.py        # HTTP Bridge 服务
    └── server_lib.py           # 服务器库
```

---

## 测试结果

### droid-executor 测试

| 测试类型 | 数量 | 状态 |
|---------|------|------|
| Property-Based Tests | 8 | ✅ 通过 |
| Scenario Tests | 15 | ✅ 通过 |
| Real Execution Tests | 9 | ✅ 通过 |
| MCP Tests | 11 | ✅ 通过 |

### 运行测试

```bash
# Property-Based Tests
droid-executor-skill/.venv/bin/pytest droid-executor-skill/scripts/tests/ -v

# Real Execution Tests (需要 Droid CLI)
droid-executor-skill/.venv/bin/python tests/test_droid_real_execution.py

# MCP Tests
droid-executor-skill/.venv/bin/python tests/test_mcp_server.py

# 快速验证
bash tests/quick_verify.sh
```

---

## 快速启动

```bash
# 启动 Codex Advisor Bridge
cd codex-advisor-skill && npx pm2 start ecosystem.config.cjs

# 启动 Droid Executor Bridge
cd droid-executor-skill && npx pm2 start ecosystem.config.cjs

# 查看状态
npx pm2 list
```
