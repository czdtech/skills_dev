# Multi-Agent 架构对齐分析

## 项目概览

本文档分析了三种形式的 Multi-Agent 实现：Skill 版本、MCP 版本，以及它们之间的架构对齐关系。

## 项目矩阵

| 项目名称 | 类型 | 主要接口 | 目标环境 | Bridge 管理 |
|---------|------|---------|---------|------------|
| `codex-advisor-skill` | Skill | SKILL.md | Claude Code | PM2 (独立) |
| `droid-executor-skill` | Skill | SKILL.md | Claude Code | PM2 (独立) |
| `codex-advisor-mcp` | MCP Server | FastMCP | 任何 MCP 客户端 | PM2 (自动) |
| `droid-executor-mcp` | MCP Server | FastMCP | 任何 MCP 客户端 | PM2 (自动) |
| `multi-agent-mcp` | MCP Server (已拆分) | FastMCP | 任何 MCP 客户端 | PM2 (自动) |

## 架构对齐

### Codex Advisor 对齐

```
codex-advisor-skill/          codex-advisor-mcp/
├── SKILL.md                  ├── mcp_server.py (FastMCP 工具)
├── bridges/                  ├── bridges/
│   ├── codex_bridge.py   ←——————→   ├── codex_bridge.py (相同)
│   └── server_lib.py     ←——————→   └── server_lib.py (相同)
├── ecosystem.config.js   ←——————→ ecosystem.config.js (相同)
├── scripts/                  ├── requirements.txt
└── docs/                     └── README.md
```

**对齐点**：
- ✅ **Bridge 代码完全相同**：都调用 Codex CLI，解析 JSON Schema 输出
- ✅ **PM2 配置一致**：相同的端口（53001）、超时（1800s）、环境变量
- ✅ **输入/输出契约**：相同的 payload 结构和返回格式
- ✅ **错误处理逻辑**：相同的验证、超时、CLI 错误处理

**差异点**：
- ❌ **前端接口**：Skill 使用 SKILL.md 定义，MCP 使用 `@mcp.tool()` 装饰器
- ❌ **生命周期管理**：Skill 需要手动启动 bridge，MCP 自动管理
- ❌ **辅助工具**：Skill 有 `scripts/` 目录用于测试和管理

### Droid Executor 对齐

```
droid-executor-skill/         droid-executor-mcp/
├── SKILL.md                  ├── mcp_server.py (FastMCP 工具)
├── bridges/                  ├── bridges/
│   ├── droid_bridge.py   ←——————→   ├── droid_bridge.py (相同)
│   └── server_lib.py     ←——————→   └── server_lib.py (相同)
├── ecosystem.config.js   ←——————→ ecosystem.config.js (相同)
├── scripts/                  ├── requirements.txt
└── docs/                     └── README.md
```

**对齐点**：
- ✅ **Bridge 代码完全相同**：都调用 Droid CLI，规范化 JSON 输出
- ✅ **PM2 配置一致**：相同的端口（53002）、超时（600s）、`--auto` 参数
- ✅ **输入/输出契约**：相同的 payload 结构和返回格式
- ✅ **输出规范化**：相同的 `_normalize_success_output()` 逻辑

**差异点**：
- ❌ **前端接口**：Skill 使用 SKILL.md 定义，MCP 使用 `@mcp.tool()` 装饰器
- ❌ **生命周期管理**：Skill 需要手动启动 bridge，MCP 自动管理
- ❌ **辅助工具**：Skill 有 `scripts/` 目录用于测试和管理

## 代码共享策略

### 方案 A：符号链接（当前推荐）

保持独立副本，需要时手动同步：

```bash
# 从 Skill 同步到 MCP
cp codex-advisor-skill/bridges/*.py codex-advisor-mcp/bridges/
cp droid-executor-skill/bridges/*.py droid-executor-mcp/bridges/
```

**优点**：独立部署，不依赖其他项目
**缺点**：需要手动同步更新

### 方案 B：共享 Bridge 库

创建 `shared-bridges/` 目录：

```
skills_dev/
├── shared-bridges/
│   ├── codex_bridge.py
│   ├── droid_bridge.py
│   └── server_lib.py
├── codex-advisor-skill/
│   └── bridges/ -> ../shared-bridges/  (symlink)
├── codex-advisor-mcp/
│   └── bridges/ -> ../shared-bridges/  (symlink)
└── ...
```

**优点**：单一可信源，自动同步
**缺点**：部署复杂，依赖关系强

### 当前选择：方案 A

理由：
1. **部署简单性**：每个项目都是自包含的
2. **版本独立性**：可以独立升级、测试
3. **容错性**：一个项目的问题不影响其他项目

## 接口对比

### Skill 接口（SKILL.md）

```markdown
## Invocation Examples

### Ask Codex Advisor
Use the Codex Advisor to analyze technical design decisions.

**Example Prompt:**
> Codex, should I use PostgreSQL or MongoDB for this project?

**Expected Behavior:**
Claude Code will call the bridge at `http://localhost:553001/analyze` with:
```json
{
  "problem": "Database selection: PostgreSQL vs MongoDB",
  "context": "...",
  "candidate_plans": [...]
}
```
```

### MCP 接口（FastMCP）

```python
@mcp.tool()
async def ask_codex_advisor(
    problem: str,
    context: str = "",
    candidate_plans: list[dict] | None = None,
    focus_areas: list[str] | None = None,
) -> dict:
    """
    向 Codex Advisor 咨询技术问题并获得建议。
    
    Args:
        problem: 需要分析的技术问题或设计决策（必填）
        context: 问题的背景上下文信息
        ...
    """
```

**共同点**：
- 相同的核心参数（problem, context, candidate_plans）
- 相同的返回结构
- 相同的底层调用（都通过 HTTP POST 到 bridge）

**差异点**：
- Skill：通过自然语言触发，Claude Code 解析意图
- MCP：通过显式的工具调用，参数明确

## 配置对比

### 超时配置

| 项目 | 环境变量 | 默认值 | 说明 |
|------|---------|--------|------|
| codex-advisor-skill | `CODEX_TIMEOUT` | 1800s (30分钟) | 深度分析任务 |
| codex-advisor-mcp | `CODEX_TIMEOUT` | 1800s (30分钟) | 相同 |
| droid-executor-skill | `DROID_TIMEOUT` | 600s (10分钟) | 执行任务 |
| droid-executor-mcp | `DROID_TIMEOUT` | 600s (10分钟) | 相同 |

### CLI 命令配置

| 项目 | 环境变量 | 默认命令 |
|------|---------|---------|
| codex-advisor-* | `CODEX_CLI_CMD` | `codex exec --skip-git-repo-check --sandbox read-only` |
| droid-executor-* | `DROID_CLI_CMD` | `droid exec --auto low -o json` |

### 端口分配

| Bridge | 端口 | 冲突检测 |
|--------|------|---------|
| codex-bridge | 53001 | 所有 codex 项目共享 |
| droid-bridge | 53002 | 所有 droid 项目共享 |

**重要**：不能同时运行：
- `codex-advisor-skill` 和 `codex-advisor-mcp`
- `droid-executor-skill` 和 `droid-executor-mcp`
- `multi-agent-mcp`（包含两者）

解决方案：
1. 使用不同的端口
2. 只启动需要的版本
3. 使用 PM2 进程管理避免重复启动

## 错误处理对比

所有项目使用相同的错误处理逻辑：

### 输入验证

```python
# Codex Advisor
if not problem:
    return {"error": "validation_error", "message": "Problem 不能为空"}
if len(problem) > 100000:
    return {"error": "validation_error", "message": "Problem 过长"}

# Droid Executor
if not objective:
    return {"status": "error", "summary": "Objective 不能为空"}
if len(objective) > 50000:
    return {"status": "error", "summary": "Objective 过长"}
```

### 超时处理

```python
# 相同的 subprocess.TimeoutExpired 捕获
except subprocess.TimeoutExpired:
    return {
        "error": "timeout",
        "message": f"执行超时（{TIMEOUT}秒）。建议拆分任务。"
    }
```

### CLI 错误

```python
# 相同的 returncode 检查
if proc.returncode != 0:
    return {
        "error": "cli_failed",
        "exit_code": proc.returncode,
        "stderr": proc.stderr[-2000:]
    }
```

## 测试与验证

### Skill 版本测试

```bash
# 启动 bridge
python3 scripts/wrapper_service.py start

# 手动调用
python3 scripts/wrapper_codex.py "问题" --context "背景"
python3 scripts/wrapper_droid.py "任务" --instructions "指令"

# 停止 bridge
python3 scripts/wrapper_service.py stop
```

### MCP 版本测试

```bash
# 自动启动（由 mcp_server.py 管理）
# 在 Claude Code 中直接使用工具
```

### 手动 Bridge 测试

```bash
# 两种版本都支持
curl http://localhost:553001/analyze -X POST \
  -H "Content-Type: application/json" \
  -d '{"problem": "test"}'

curl http://localhost:553002/execute -X POST \
  -H "Content-Type: application/json" \
  -d '{"objective": "test"}'
```

## 升级与同步

### 同步 Bridge 代码

```bash
#!/bin/bash
# sync_bridges.sh

# Codex Bridge
cp codex-advisor-skill/bridges/codex_bridge.py codex-advisor-mcp/bridges/
cp codex-advisor-skill/bridges/server_lib.py codex-advisor-mcp/bridges/

# Droid Bridge  
cp droid-executor-skill/bridges/droid_bridge.py droid-executor-mcp/bridges/
cp droid-executor-skill/bridges/server_lib.py droid-executor-mcp/bridges/

echo "Bridge 代码已同步"
```

### 验证同步

```bash
# 检查文件差异
diff codex-advisor-skill/bridges/codex_bridge.py codex-advisor-mcp/bridges/codex_bridge.py
diff droid-executor-skill/bridges/droid_bridge.py droid-executor-mcp/bridges/droid_bridge.py
```

### 升级策略

1. **在 Skill 版本中开发和测试新功能**（有 scripts/ 辅助）
2. **验证通过后同步到 MCP 版本**
3. **重启 MCP 服务器应用更改**

## 部署建议

### 开发环境

- **使用 Skill 版本**：在 Claude Code 中深度集成，便于调试
- **Bridge 共享**：所有版本使用相同的 bridge（端口 53001/53002）

### 生产环境

- **只部署 MCP 版本**：更灵活，支持多种客户端
- **独立 Bridge**：每个 MCP 服务器管理自己的 bridge

### 混合环境

- **Claude Code**：使用 Skill 版本
- **Claude Desktop/其他客户端**：使用 MCP 版本
- **Bridge 隔离**：使用不同端口避免冲突

## 未来改进

### 1. 统一配置管理

创建 `config.yaml`：

```yaml
bridges:
  codex:
    port: 53001
    timeout: 1800
    cli_cmd: "codex exec --skip-git-repo-check --sandbox read-only"
  droid:
    port: 53002
    timeout: 600
    cli_cmd: "droid exec --auto low -o json"
```

### 2. Bridge 版本化

```
bridges/
├── v1/
│   ├── codex_bridge.py
│   └── droid_bridge.py
└── v2/
    ├── codex_bridge.py (增强版)
    └── droid_bridge.py (增强版)
```

### 3. 健康检查端点

在 bridge 中添加 `/health` 端点：

```python
def do_GET(self):
    if self.path == "/health":
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "healthy"}).encode())
```

### 4. 监控与日志

集成结构化日志和监控：

```python
import structlog
logger = structlog.get_logger()

logger.info("bridge_started", port=53001, version="1.0.0")
logger.info("analysis_requested", problem_length=len(problem))
logger.info("analysis_completed", duration=duration)
```

## 总结

| 维度 | 对齐程度 | 说明 |
|------|---------|------|
| **Bridge 代码** | 100% | 完全相同 |
| **配置** | 100% | PM2、超时、CLI 命令一致 |
| **输入/输出契约** | 100% | 相同的 payload 和返回格式 |
| **错误处理** | 100% | 相同的验证和错误逻辑 |
| **前端接口** | 0% | Skill 用 SKILL.md，MCP 用 FastMCP |
| **生命周期管理** | 50% | 都用 PM2，但管理方式不同 |
| **辅助工具** | 0% | Skill 有 scripts/，MCP 无 |

**结论**：
- ✅ 核心逻辑（bridge）完全对齐
- ✅ 可以无缝切换使用（输入输出兼容）
- ✅ 配置可移植（相同的环境变量和端口）
- ⚠️ 部署方式有差异（自动 vs 手动）
- ⚠️ 不能同时运行（端口冲突）

这种对齐设计确保了：
1. **代码复用**：Bridge 逻辑单一可信源
2. **行为一致**：无论哪种接口，底层行为相同
3. **灵活性**：可根据场景选择合适的形式
4. **可维护性**：修改 Bridge 后所有版本都受益
