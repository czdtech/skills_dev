# 🏗️ Taskmaster Autopilot 工作原理详解

**基于官方文档**: https://docs.task-master.dev/tdd-workflow/ai-agent-integration

---

## 🎯 你的三个核心问题

### Q1: 在Claude Code中用Claude Code的能力去写代码？
**答案**: ✅ **是的**，但不仅限于Claude Code

### Q2: 能单独进行配置？
**答案**: ✅ **可以**，通过`.taskmaster/config.json`配置AI provider

### Q3: 能在Claude Code中指定Codex或Droid写代码？
**答案**: ⚠️ **理论上可以**，但需要自定义集成

---

## 🏗️ Autopilot架构

### 官方架构图

```
┌─────────────────────────────────────────────┐
│         AI Agent                            │
│  (Claude Code, Custom Agent, etc.)          │
│                                             │
│  职责:                                       │
│  • 读取子任务要求                            │
│  • 编写测试代码 (RED)                        │
│  • 编写实现代码 (GREEN)                      │
│  • 运行测试                                  │
│  • 报告结果                                  │
└─────────────┬───────────────────────────────┘
              │
              │ 使用 CLI 或 MCP
              │
┌─────────────▼───────────────────────────────┐
│      Taskmaster Interface                   │
│   ┌──────────────┐  ┌──────────────┐        │
│   │ CLI Commands │  │  MCP Tools   │        │
│   └──────┬───────┘  └──────┬───────┘        │
└──────────┼──────────────────┼────────────────┘
           │                  │
┌──────────▼──────────────────▼────────────────┐
│    WorkflowOrchestrator (核心引擎)          │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │  State Machine: RED → GREEN → COMMIT   │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  职责:                                        │
│  • 管理TDD状态机                              │
│  • 验证测试结果 (RED必须失败, GREEN必须通过)   │
│  • 创建Git commits                           │
│  • 跟踪进度                                   │
│  • 持久化状态                                 │
└──────────────────────────────────────────────┘
           │
           │ 保存状态到
           ▼
┌──────────────────────────────────────────────┐
│   .taskmaster/workflow-state.json            │
└──────────────────────────────────────────────┘
```

---

## 🔑 关键点：AI Agent是可替换的

### Autopilot的设计理念

**Taskmaster Autopilot ≠ 固定的AI**

它是一个**框架**，任何AI Agent都可以接入：

```
┌─────────────────────────────────────────┐
│  可用的 AI Agents (可选其一或多个)       │
├─────────────────────────────────────────┤
│  • Claude Code (默认推荐)               │
│  • Anthropic API                        │
│  • OpenAI API                           │
│  • 自定义 Agent (如你的Codex/Droid)     │
└─────────────────────────────────────────┘
          │
          │ 通过配置选择
          ▼
┌─────────────────────────────────────────┐
│    .taskmaster/config.json              │
│                                         │
│    "models": {                          │
│      "main": {                          │
│        "provider": "claude-code"  ← 配置 │
│      }                                  │
│    }                                    │
└─────────────────────────────────────────┘
```

---

## 📋 工作流程详解

### 完整的TDD循环

#### 阶段0: 用户启动
```
用户 → "Start autopilot for task 1"
     ↓
Taskmaster Autopilot:
  • 创建Git分支 (task-1)
  • 加载子任务列表
  • 设置状态为 RED
  • 准备完毕
```

---

#### 阶段1: RED Phase（AI编写测试）

**Autopilot** → **AI Agent**:
```json
{
  "action": "generate_test",
  "subtask": {
    "id": "1.1",
    "title": "实现加法功能",
    "description": "创建add函数，接受两个数字参数"
  },
  "phase": "RED",
  "instruction": "写一个会失败的测试"
}
```

**AI Agent** (Claude Code) **执行**:
```typescript
// 1. 理解需求
// 2. 创建测试文件
// tests/calculator.test.ts
import { describe, it, expect } from 'vitest';
import { add } from '../src/calculator';

describe('Calculator', () => {
  it('should add two numbers', () => {
    expect(add(2, 3)).toBe(5);
  });
});

// 3. 运行测试
// npm test
// ❌ FAILED: add is not defined

// 4. 报告结果给Taskmaster
```

**AI Agent** → **Autopilot**:
```bash
task-master autopilot complete --results '{
  "total": 1,
  "passed": 0,
  "failed": 1,
  "skipped": 0
}'
```

**Autopilot验证**:
```
✓ RED phase 验证通过 (测试确实失败了)
✓ 转换状态: RED → GREEN
→ 下一步: 实现功能
```

---

#### 阶段2: GREEN Phase（AI编写代码）

**Autopilot** → **AI Agent**:
```json
{
  "action": "implement_feature",
  "phase": "GREEN",
  "instruction": "实现代码让测试通过",
  "test_output": "add is not defined"
}
```

**AI Agent** (Claude Code) **执行**:
```typescript
// 1. 分析测试失败原因
// 2. 创建实现文件
// src/calculator.ts
export function add(a: number, b: number): number {
  return a + b;
}

// 3. 运行测试
// npm test
// ✓ PASSED: 1 test passed

// 4. 报告结果
```

**AI Agent** → **Autopilot**:
```bash
task-master autopilot complete --results '{
  "total": 1,
  "passed": 1,
  "failed": 0,
  "skipped": 0
}'
```

**Autopilot验证**:
```
✓ GREEN phase 验证通过 (所有测试通过)
✓ 转换状态: GREEN → COMMIT
→ 下一步: 提交代码
```

---

#### 阶段3: COMMIT Phase（Autopilot自动提交）

**Autopilot自动执行**:
```bash
# 1. 生成commit消息
git commit -m "feat: implement add function (Task 1.1)"

# 2. 创建commit（包含元数据）
```

**Commit内容**:
```
feat: implement add function (Task 1.1)

Implemented by: taskmaster-autopilot
Task: 1
Subtask: 1
Phase: GREEN → COMMIT
Test coverage: 1 test passing
```

**Autopilot后续**:
```
✓ Commit 创建成功
✓ 移动到下一个子任务 (1.2)
✓ 重置状态: COMMIT → RED
→ 循环继续...
```

---

## 🎨 AI Provider配置

### 方式1: 使用Claude Code（当前配置）

**配置文件**: `.taskmaster/config.json`
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

**工作方式**:
```
用户在Claude Code中 → "Start autopilot for task 1"
                      ↓
Claude Code (AI) ←─── Autopilot发出指令: "Write a test"
                      ↓
Claude Code写测试 ──→ Autopilot验证
                      ↓
Claude Code写代码 ──→ Autopilot验证
                      ↓
                   Autopilot commit
```

**优势**:
- ✅ 完全免费
- ✅ 集成在IDE中
- ✅ 自然语言交互

---

### 方式2: 使用Anthropic API

**配置**:
```json
{
  "models": {
    "main": {
      "provider": "anthropic",
      "modelId": "claude-3-7-sonnet-20250219"
    }
  }
}
```

**需要**: `.env`中配置`ANTHROPIC_API_KEY`

---

### 方式3: 自定义Agent（理论上支持）

**你提到的Codex/Droid集成**:

理论上可以，但需要：

#### 选项A: 通过MCP集成
```
Claude Code (对话界面)
    ↓
调用 Taskmaster MCP Tools
    ↓
Taskmaster Autopilot
    ↓
Claude Code内部调用Codex/Droid
    ↓
返回结果给Autopilot
```

#### 选项B: 自定义Provider
```json
{
  "models": {
    "main": {
      "provider": "custom",
      "endpoint": "http://localhost:8000/codex"
    }
  }
}
```

**但这需要**:
1. Codex/Droid实现Taskmaster的AI Provider接口
2. 或者通过代理层转换

---

## 🔍 当前架构中的可能实现

### 基于你的`.claude/CLAUDE.md`

你提到：
> **层 3: Autopilot TDD 工作流（阶段 6 可选模式）**
> 作为 Droid 的替代方案

这说明在**你的架构**中：

```
┌─────────────────────────────────────┐
│      阶段6: 实现与执行              │
├─────────────────────────────────────┤
│                                     │
│  执行模式 A: Droid Executor         │
│    • 直接执行命令                    │
│    • 不需要TDD                       │
│                                     │
│  执行模式 B: Autopilot TDD          │
│    • 严格TDD流程                     │
│    • 自动验证                        │
│                                     │
│  选择标准:                           │
│  • TDD适用? → Autopilot             │
│  • 快速执行? → Droid                │
│                                     │
└─────────────────────────────────────┘
```

### 可能的集成方式

**方式1: Autopilot使用Claude Code内置能力**
```
用户 → Claude Code (你)
       ↓
     "Start autopilot for task 1"
       ↓
     Autopilot启动
       ↓
     你 (Claude Code) 自己:
       • 写测试
       • 写代码
       • 报告结果
```

**方式2: Autopilot委托给Droid/Codex（需要自定义）**
```
用户 → Claude Code
       ↓
     "Start autopilot for task 1"
       ↓
     Autopilot启动
       ↓
     Claude Code调用:
       • Codex MCP → 获取建议
       • Droid MCP → 执行写文件
       ↓
     报告结果给Autopilot
```

**但这需要修改Autopilot的工作流程**

---

## 💡 实际使用建议

### 当前推荐方式（基于已有配置）

**使用Claude Code作为AI Agent**:

```
1. 配置已完成:
   .taskmaster/config.json → provider: claude-code ✅

2. 在Claude Code中启动:
   "Start autopilot for task 1"
   
3. Claude Code (我) 自己执行:
   • RED: 写测试
   • GREEN: 写代码  
   • 报告给Autopilot

4. Autopilot管理:
   • 验证测试结果
   • 创建commits
   • 推进流程
```

### 与Codex/Droid的关系

**它们是不同的工具**:

| 工具 | 作用 | 使用时机 |
|------|------|---------|
| **Autopilot** | TDD工作流引擎 | 需要严格TDD的功能 |
| **Codex** | 技术决策建议 | 架构设计阶段 |
| **Droid** | 命令执行器 | 快速执行非TDD任务 |

**它们可以配合，但不是直接集成**:

```
场景1: TDD开发新功能
→ 使用 Autopilot
→ AI: Claude Code自己

场景2: 快速实现配置
→ 使用 Droid
→ 不需要Autopilot

场景3: 架构决策
→ 咨询 Codex
→ 不涉及Autopilot
```

---

## 🎯 回答你的问题

### Q1: 在Claude Code中用Claude Code的能力去写代码？

✅ **是的！**

```
用户 → Claude Code
       ↓
     启动Autopilot
       ↓
     Claude Code (我) 自己:
       • 使用我的代码生成能力
       • 写测试和实现
       • 报告给Autopilot框架
       ↓
     Autopilot验证和管理流程
```

---

### Q2: 能单独进行配置？

✅ **可以！**

**配置位置**: `.taskmaster/config.json`

**可配置内容**:
```json
{
  "models": {
    "main": {
      "provider": "claude-code",  // 选择AI provider
      "modelId": "sonnet"         // 选择模型
    }
  }
}
```

**支持的providers**:
- `claude-code` (免费)
- `anthropic` (需API key)
- `openai` (需API key)
- `ollama` (本地)
- 等等...

---

### Q3: 能在Claude Code中指定Codex或Droid写代码？

⚠️ **理论可行，但需要自定义集成**

**官方Autopilot的设计**:
```
AI Agent (单一) ←→ Autopilot
```

**你想要的设计**:
```
Claude Code (协调者)
    ↓
Codex (建议) + Droid (执行)
    ↓
报告给 Autopilot
```

**实现方式**:

**方式A: Claude Code作为中间层**
```typescript
// 伪代码
async function handleAutopilotREDPhase(subtask) {
  // 1. 咨询Codex获取测试策略
  const advice = await codexMCP.getTestStrategy(subtask);
  
  // 2. 让Droid写测试文件
  await droidMCP.writeFile('tests/test.ts', testCode);
  
  // 3. 运行测试
  const results = await runTests();
  
  // 4. 报告给Autopilot
  await autopilot.complete({results});
}
```

**方式B: 修改Autopilot支持多Agent**
（需要修改Taskmaster源码，复杂度高）

---

## 🏁 总结

### Autopilot的真实工作方式

**Taskmaster Autopilot = 工作流框架**

它**不是**AI，它是**管理AI的框架**：

```
┌─────────────────────────────────┐
│  Autopilot (框架)               │
│                                 │
│  • 不会写代码                    │
│  • 管理状态机                    │
│  • 验证测试结果                  │
│  • 创建commits                   │
│  • 跟踪进度                      │
└────────┬────────────────────────┘
         │ 委托给
         ▼
┌─────────────────────────────────┐
│  AI Agent (可替换)              │
│                                 │
│  • 写测试代码                    │
│  • 写实现代码                    │
│  • 运行测试                      │
│  • 报告结果                      │
│                                 │
│  可选:                           │
│  • Claude Code ✅ (当前)        │
│  • Anthropic API               │
│  • 自定义Agent                  │
└─────────────────────────────────┘
```

### 与你的架构的关系

**Autopilot** 和 **Droid** 是平行的执行模式：

```
你的项目架构:
  ├─ Codex: 技术决策
  ├─ Droid: 快速执行
  └─ Autopilot: 严格TDD (新加入)
```

它们各有用途，可以配合但不直接集成。

**建议**: 
- 功能开发 → Autopilot
- 配置任务 → Droid  
- 架构决策 → Codex

这样充分利用每个工具的优势！🚀
