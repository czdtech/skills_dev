# Multi-Agent MCP 拆分迁移指南

## 概述

原 `multi-agent-mcp` 已拆分为两个独立的 MCP 服务器：

1. **codex-advisor-mcp** - 技术设计咨询
2. **droid-executor-mcp** - 自动化编码执行

这种拆分带来了以下优势：

- ✅ **独立部署**：可以只启用需要的服务
- ✅ **职责单一**：每个服务专注于自己的功能
- ✅ **架构对齐**：与对应的 Skill 版本保持一致
- ✅ **易于维护**：更清晰的代码组织和依赖管理
- ✅ **灵活配置**：分别配置超时、CLI 命令等参数

## 架构对比

### 原架构（multi-agent-mcp）

```
multi-agent-mcp/
├── mcp_server.py           # 包含两个工具
├── bridges/
│   ├── codex_bridge.py     # Codex Bridge
│   ├── droid_bridge.py     # Droid Bridge
│   └── server_lib.py
└── ecosystem.config.js     # 管理两个 bridge
```

### 新架构

```
codex-advisor-mcp/          # 独立的 Codex MCP
├── mcp_server.py           # 只包含 ask_codex_advisor
├── bridges/
│   ├── codex_bridge.py
│   └── server_lib.py
└── ecosystem.config.js     # 只管理 codex-bridge

droid-executor-mcp/         # 独立的 Droid MCP
├── mcp_server.py           # 只包含 execute_droid_task
├── bridges/
│   ├── droid_bridge.py
│   └── server_lib.py
└── ecosystem.config.js     # 只管理 droid-bridge
```

## 迁移步骤

### 1. 卸载旧的 MCP 服务器

```bash
# 查看当前配置
claude mcp list

# 如果已安装 multi-agent-studio，先删除
claude mcp remove multi-agent-studio
```

### 2. 安装新的 MCP 服务器

#### 安装 Codex Advisor MCP

```bash
cd /home/jiang/work/for_claude/skills_dev/codex-advisor-mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 注册到 Claude Code
claude mcp add --transport stdio codex-advisor \
  -- $(pwd)/.venv/bin/python $(pwd)/mcp_server.py
```

#### 安装 Droid Executor MCP

```bash
cd /home/jiang/work/for_claude/skills_dev/droid-executor-mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 注册到 Claude Code
claude mcp add --transport stdio droid-executor \
  -- $(pwd)/.venv/bin/python $(pwd)/mcp_server.py
```

### 3. 验证安装

```bash
claude mcp list
```

应显示两个新的服务器：
- `codex-advisor`
- `droid-executor`

### 4. 测试功能

在 Claude Code 中测试：

```
# 测试 Codex Advisor
请使用 Codex Advisor 分析：选择 PostgreSQL 还是 MongoDB？

# 测试 Droid Executor
使用 Droid 创建一个简单的 Hello World Python 脚本
```

## API 变更

### 工具名称

| 原工具名 | 新工具名 | 所属服务器 |
|---------|---------|-----------|
| `ask_codex_advisor` | `ask_codex_advisor` | codex-advisor |
| `execute_droid_task` | `execute_droid_task` | droid-executor |

**工具签名保持不变**，无需修改调用代码。

### 增强的参数

两个工具都添加了更详细的参数说明和示例。

#### ask_codex_advisor 的新参数

- `questions_for_codex`: 希望 Codex 回答的具体问题
- `non_goals`: 明确排除的目标
- `phase`: 对话阶段

#### execute_droid_task 的新参数

- `constraints`: 约束条件列表
- `acceptance_criteria`: 验收标准列表

### 错误处理改进

新版本提供了更详细的错误信息和建议：

```python
# 超时错误示例
{
    "error": "timeout",
    "message": "Codex 分析超时。问题可能过于复杂，建议分解为更小的问题。"
}

# 连接错误示例
{
    "status": "error",
    "summary": "无法连接到 Droid Bridge: Connection refused",
    "issues": [{
        "type": "connection_error",
        "description": "Connection refused",
        "suggested_action": "确认 Droid Bridge 服务正在运行（端口 53002）"
    }]
}
```

## 配置差异

### 环境变量

每个 MCP 服务器现在有独立的配置：

#### codex-advisor-mcp/ecosystem.config.js

```javascript
{
  CODEX_CLI_CMD: "...",
  CODEX_TIMEOUT: "1800",  // 30 分钟
  PORT: 53001
}
```

#### droid-executor-mcp/ecosystem.config.js

```javascript
{
  DROID_CLI_CMD: "droid exec --auto low -o json",
  DROID_TIMEOUT: "600",  // 10 分钟
  PORT: 53002
}
```

### 端口保持不变

- Codex Bridge: 53001
- Droid Bridge: 53002

如有端口冲突，可在各自的 `ecosystem.config.js` 中修改，并更新 `mcp_server.py` 中的 `*_BRIDGE_URL`。

## 常见问题

### Q: 可以只安装其中一个 MCP 服务器吗？

**A**: 可以！这正是拆分的主要优势之一。如果只需要技术咨询，只安装 `codex-advisor-mcp` 即可。

### Q: 两个服务器会冲突吗？

**A**: 不会。它们使用不同的端口（53001 和 53002），各自管理独立的 PM2 进程。

### Q: bridge 服务需要手动启动吗？

**A**: 不需要。MCP 服务器启动时会自动通过 PM2 启动 bridge，停止时自动停止。

### Q: 可以同时运行旧版和新版吗？

**A**: 不建议。端口会冲突（都使用 53001 和 53002）。迁移前应先停止旧版的 bridge：

```bash
cd /home/jiang/work/for_claude/skills_dev/multi-agent-mcp
npx pm2 stop ecosystem.config.js
npx pm2 delete ecosystem.config.js
```

### Q: 如果出现 "bridge 无法连接" 错误？

**A**: 
1. 检查 PM2 状态：`npx pm2 status`
2. 查看日志：`npx pm2 logs codex-bridge` 或 `npx pm2 logs droid-bridge`
3. 手动重启：`npx pm2 restart all`

### Q: 性能有提升吗？

**A**: 功能性能一致（底层 bridge 代码未变），但拆分后各服务器独立运行，资源隔离更好。如果只使用一个服务，另一个不会占用资源。

## 回滚方案

如需回滚到旧版：

```bash
# 1. 删除新服务器
claude mcp remove codex-advisor
claude mcp remove droid-executor

# 2. 重新安装旧版
cd /home/jiang/work/for_claude/skills_dev/multi-agent-mcp
source .venv/bin/activate
claude mcp add --transport stdio multi-agent-studio \
  -- $(pwd)/.venv/bin/python $(pwd)/mcp_server.py
```

## 与 Skill 版本的关系

| MCP 版本 | 对应 Skill | 用途 |
|---------|-----------|------|
| codex-advisor-mcp | codex-advisor-skill | 在任何 MCP 客户端使用 |
| droid-executor-mcp | droid-executor-skill | 在任何 MCP 客户端使用 |

**建议**：
- 在 **Claude Code** 中：优先使用 **Skill** 版本（集成更深）
- 在 **Claude Desktop** 或其他客户端：使用 **MCP** 版本

## 技术细节

### 代码同步

两个 MCP 服务器的 bridge 代码与对应 Skill 保持同步：

```bash
# codex-advisor-mcp/bridges/ 同步自 codex-advisor-skill/bridges/
cp codex-advisor-skill/bridges/*.py codex-advisor-mcp/bridges/

# droid-executor-mcp/bridges/ 同步自 droid-executor-skill/bridges/
cp droid-executor-skill/bridges/*.py droid-executor-mcp/bridges/
```

### PM2 进程命名

- 旧版：`codex-bridge` 和 `droid-bridge`（由 multi-agent-mcp 管理）
- 新版：
  - `codex-bridge`（由 codex-advisor-mcp 管理）
  - `droid-bridge`（由 droid-executor-mcp 管理）

名称相同但由不同的 MCP 服务器管理，避免同时运行。

## 下一步

1. ✅ 完成迁移
2. 阅读各服务器的 README.md 了解详细用法
3. 根据需要调整 `ecosystem.config.js` 中的配置
4. 在实际项目中测试功能
5. 将常用工作流文档化

## 参考文档

- [codex-advisor-mcp/README.md](../codex-advisor-mcp/README.md)
- [droid-executor-mcp/README.md](../droid-executor-mcp/README.md)
- [codex-advisor-skill/SKILL.md](../codex-advisor-skill/SKILL.md)
- [droid-executor-skill/SKILL.md](../droid-executor-skill/SKILL.md)
