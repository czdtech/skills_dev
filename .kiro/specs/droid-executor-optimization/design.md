# Design Document

## Overview

本设计文档描述了将 droid-executor-skill 和 droid-executor-mcp 优化为符合各自标准的技术方案。优化工作参照已完成的 codex-advisor-skill 和 codex-advisor-mcp 实现。

### 目标

1. **droid-executor-skill**: 完全符合 Claude Code Skills 规范
2. **droid-executor-mcp**: 与 codex-advisor-mcp 保持一致的实现模式

### 参考实现

| 组件 | 参考项目 | 目标项目 |
|------|----------|----------|
| Skill | codex-advisor-skill | droid-executor-skill |
| MCP | codex-advisor-mcp | droid-executor-mcp |

## Architecture

### 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Code / MCP Client                  │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│   droid-executor-skill  │     │   droid-executor-mcp    │
│   (Skills 规范)          │     │   (MCP 协议)            │
├─────────────────────────┤     ├─────────────────────────┤
│ SKILL.md                │     │ mcp_server.py           │
│ wrapper_droid.py        │     │ (FastMCP)               │
│ ecosystem.config.cjs    │     │ ecosystem.config.cjs    │
└───────────┬─────────────┘     └───────────┬─────────────┘
            │                               │
            ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│ scripts/bridge/         │     │ bridges/                │
│   droid_bridge.py       │     │   droid_bridge.py       │
│   server_lib.py         │     │   server_lib.py         │
└───────────┬─────────────┘     └───────────┬─────────────┘
            │                               │
            └───────────────┬───────────────┘
                            ▼
                  ┌─────────────────┐
                  │   Droid CLI     │
                  │   (Factory)     │
                  └─────────────────┘
```

### 目录结构对比

**droid-executor-skill (目标结构):**
```
droid-executor-skill/
├── SKILL.md                    # 技能入口文件
├── LICENSE.txt                 # Apache 2.0 许可证
├── ecosystem.config.cjs        # PM2 配置
├── scripts/
│   ├── wrapper_droid.py        # 命令行封装
│   └── bridge/
│       ├── droid_bridge.py     # HTTP Bridge 服务
│       └── server_lib.py       # 服务器库
└── references/
    └── droid-executor-protocol.md  # 协议文档
```

**droid-executor-mcp (目标结构):**
```
droid-executor-mcp/
├── mcp_server.py               # MCP 服务器入口
├── ecosystem.config.cjs        # PM2 配置
├── requirements.txt            # Python 依赖
├── setup.sh                    # 安装脚本
├── README.md                   # 项目说明
├── .gitignore
└── bridges/
    ├── droid_bridge.py         # HTTP Bridge 服务
    └── server_lib.py           # 服务器库
```

## Components and Interfaces

### 1. SKILL.md (Skill 项目)

**接口定义:**
```yaml
---
name: droid-executor
description: Execute predefined coding tasks after architecture decisions. Use when tasks have clear objectives and acceptance criteria.
license: Complete terms in LICENSE.txt
---
```

**职责:**
- 定义技能的元数据
- 提供使用指南和示例
- 符合 Agent Skills Spec 规范

### 2. wrapper_droid.py (Skill 项目)

**接口:**
```bash
python scripts/wrapper_droid.py "objective" \
  --instructions "detailed instructions" \
  --context '{"repo_root": "/path", "files_of_interest": ["file1.py"]}'
```

**职责:**
- 提供命令行接口
- 自动管理 Bridge 服务生命周期
- 使用 socket 端口检测 Bridge 状态

**关键实现 (参照 codex-advisor-skill):**
```python
def is_port_open(port, timeout=1):
    """Check if port is open (bridge is running)."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    except:
        return False

def ensure_bridge():
    """Start bridge if not running."""
    if is_port_open(BRIDGE_PORT):
        return True
    
    subprocess.run(
        ["npx", "pm2", "start", "ecosystem.config.cjs"],
        cwd=ROOT_DIR,
        capture_output=True
    )
    # Wait for bridge to be ready
    for i in range(30):
        if is_port_open(BRIDGE_PORT):
            return True
        time.sleep(1)
    return False
```

### 3. ecosystem.config.cjs

**Skill 版本:**
```javascript
module.exports = {
  apps: [{
    name: "droid-bridge",
    script: "./scripts/bridge/droid_bridge.py",
    interpreter: "python3",
    env: {
      PORT: 53002,
      DROID_TIMEOUT: "600"
    }
  }]
};
```

**MCP 版本:**
```javascript
module.exports = {
  apps: [{
    name: "droid-bridge",
    script: "./bridges/droid_bridge.py",
    interpreter: "python3",
    env: {
      PORT: 53002,
      DROID_TIMEOUT: "600"
    }
  }]
};
```

### 4. droid_bridge.py

**HTTP 接口:**
- Endpoint: `POST /execute`
- Port: 53002
- Timeout: 600 秒 (10 分钟)

**输入 Schema:**
```json
{
  "objective": "string (required)",
  "instructions": "string",
  "context": {
    "repo_root": "string",
    "files_of_interest": ["string"]
  },
  "constraints": ["string"],
  "acceptance_criteria": ["string"]
}
```

**输出 Schema:**
```json
{
  "status": "success|partial|failed|timeout|error",
  "summary": "string",
  "files_changed": [{"path": "string", "change_type": "string", "highlights": []}],
  "commands_run": [{"command": "string", "exit_code": "number", "stdout_excerpt": "string"}],
  "tests": {"passed": "boolean", "details": "string"},
  "logs": ["string"],
  "issues": [{"type": "string", "description": "string", "suggested_action": "string"}]
}
```

### 5. mcp_server.py (MCP 项目)

**MCP Tool 定义:**
```python
@mcp.tool()
async def execute_droid_task(
    objective: str,
    instructions: str = "",
    context: dict | None = None,
    constraints: list[str] | None = None,
    acceptance_criteria: list[str] | None = None,
) -> dict:
    """Execute coding task via Droid CLI."""
```

**生命周期管理:**
- 启动时自动启动 Bridge
- 关闭时自动停止 Bridge
- 使用 atexit 注册清理钩子

## Data Models

### ExecutionRequest

```python
@dataclass
class ExecutionRequest:
    objective: str              # 任务目标 (必填, ≤50000 字符)
    instructions: str = ""      # 详细指令 (≤100000 字符)
    context: dict = None        # 上下文信息
    constraints: list = None    # 约束条件
    acceptance_criteria: list = None  # 验收标准
```

### ExecutionResult

```python
@dataclass
class ExecutionResult:
    status: str                 # success|partial|failed|timeout|error
    summary: str                # 执行摘要
    files_changed: list         # 修改的文件
    commands_run: list          # 执行的命令
    tests: dict                 # 测试结果
    logs: list                  # 日志
    issues: list                # 问题列表
```



## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

Based on the prework analysis, most acceptance criteria are structural/configuration verifications best tested as examples. The following properties are suitable for property-based testing:

### Property 1: Socket Port Detection Accuracy

*For any* TCP port state (open or closed), the `is_port_open` function should correctly detect whether a service is listening on that port.

**Validates: Requirements 4.1**

### Property 2: Input Validation Completeness

*For any* invalid input to the bridge (empty objective, objective exceeding 50000 characters, instructions exceeding 100000 characters), the bridge should reject the request with an appropriate error response.

**Validates: Requirements 8.3**

## Error Handling

### Bridge Errors

| Error Type | Condition | Response |
|------------|-----------|----------|
| `validation_error` | Empty objective or exceeds length limits | Return error with description |
| `timeout` | Execution exceeds DROID_TIMEOUT | Return timeout status with suggestion |
| `env_issue` | Droid CLI not found | Return failed status with installation hint |
| `unknown` | Unexpected exception | Return failed status with error message |

### Wrapper Errors

| Error Type | Condition | Action |
|------------|-----------|--------|
| Bridge not starting | PM2 fails to start bridge | Print warning, continue execution attempt |
| Connection error | Cannot connect to bridge | Print error, exit with code 1 |
| Timeout | Bridge request times out | Print error, exit with code 1 |

### MCP Server Errors

| Error Type | Condition | Response |
|------------|-----------|----------|
| `timeout` | Bridge request times out | Return timeout status dict |
| `bridge_error` | HTTP error from bridge | Return error status with details |
| `connection_error` | Cannot connect to bridge | Return error status with message |

## Testing Strategy

### Unit Tests

由于本项目主要是配置和结构优化，单元测试主要验证：

1. **目录结构验证**: 检查文件和目录是否存在于正确位置
2. **配置文件验证**: 检查 ecosystem.config.cjs 内容是否正确
3. **SKILL.md 验证**: 检查 frontmatter 字段是否完整

### Property-Based Tests

使用 Python 的 `hypothesis` 库进行属性测试：

1. **Property 1 测试**: 生成随机端口号，验证 `is_port_open` 函数行为
2. **Property 2 测试**: 生成各种无效输入，验证 bridge 的输入验证

**测试配置:**
- 每个属性测试运行至少 100 次迭代
- 使用 `@settings(max_examples=100)` 配置

**测试标注格式:**
```python
# **Feature: droid-executor-optimization, Property 1: Socket Port Detection Accuracy**
# **Validates: Requirements 4.1**
@given(port=st.integers(min_value=1, max_value=65535))
def test_port_detection_accuracy(port):
    ...
```

### Integration Tests

1. **Bridge 启动测试**: 验证 PM2 能正确启动 bridge
2. **端到端测试**: 验证 wrapper → bridge → CLI 的完整流程

## File Changes Summary

### droid-executor-skill

| 操作 | 文件/目录 | 说明 |
|------|-----------|------|
| 移动 | `bridges/` → `scripts/bridge/` | 符合 Skills 规范 |
| 移动 | `docs/` → `references/` | 符合 Skills 规范 |
| 创建 | `LICENSE.txt` | Apache 2.0 许可证 |
| 更新 | `SKILL.md` | 添加 license 字段 |
| 重命名 | `ecosystem.config.js` → `ecosystem.config.cjs` | Node.js 兼容 |
| 更新 | `scripts/wrapper_droid.py` | 添加 socket 端口检测 |
| 删除 | `BUG_REPORT.md` 等非标准文件 | 清理 |
| 删除 | `README.md` | SKILL.md 已包含说明 |
| 删除 | `.factory/` | 清理 |

### droid-executor-mcp

| 操作 | 文件/目录 | 说明 |
|------|-----------|------|
| 重命名 | `ecosystem.config.js` → `ecosystem.config.cjs` | Node.js 兼容 |
| 更新 | `mcp_server.py` | 引用 .cjs 配置文件 |
| 更新 | `bridges/droid_bridge.py` | 清理 debug 代码 |
| 删除 | `fibonacci.py`, `hello_world.py` | 清理测试文件 |
| 删除 | `.factory/` | 清理 |
| 删除 | `tests/` | 清理测试目录 |
