# 🤖 Taskmaster Autopilot TDD 测试指南

**官方文档**: https://docs.task-master.dev/tdd-workflow/quickstart  
**测试日期**: 2025-11-24  
**测试状态**: ⚠️ **未测试** - 需要特殊前置条件

---

## 📊 测试状态总览

| 功能 | CLI测试 | MCP测试 | Autopilot测试 |
|------|---------|---------|--------------|
| **基础命令** | ✅ | ⚠️ | - |
| **AI功能** | ✅ | ⚠️ | - |
| **TDD工作流** | - | - | ❌ 未测试 |

---

## 🎯 Autopilot TDD 是什么？

### 核心概念

**Autopilot TDD** 是Taskmaster的高级功能，提供**自动化的TDD循环**：

```
RED → GREEN → COMMIT → 下一个子任务
 ↑                            ↓
 └────────────────────────────┘
```

### 角色分工

**Taskmaster (工作流引擎)**:
- 管理TDD状态机（RED/GREEN/COMMIT）
- 验证测试结果
- 自动创建Git commits
- 跟踪进度

**AI Agent (Claude Code)**:
- 编写测试代码（RED phase）
- 实现功能代码（GREEN phase）
- 运行测试并报告结果

---

## 🔧 前置条件检查

### 必须满足的条件

#### 1. ✅ Taskmaster已初始化
```bash
# 已满足
ls .taskmaster/config.json  # ✅ 存在
ls .taskmaster/tasks/tasks.json  # ✅ 存在
```

#### 2. ✅ 任务已创建并包含子任务
```bash
# 已满足 - 任务1已扩展
task-master show 1  # ✅ 有5个子任务
```

#### 3. ⚠️ Git仓库状态
```bash
# 当前状态检查
git status

# 要求：
- ❌ 工作树必须干净（no uncommitted changes）
- ❌ 当前有大量未提交的文件
```

**当前Git状态**: 🔴 **不满足** - 有未提交的变更

#### 4. ⚠️ 测试框架配置
```bash
# 需要确认：
- 项目是否安装了测试框架（vitest/jest/mocha）？
- package.json中是否配置了test脚本？
- 是否有测试目录？
```

**当前状态**: ⚠️ **待确认**

---

## 📋 Autopilot 可用命令

### 命令列表

根据`task-master autopilot --help`的输出：

```bash
task-master autopilot start <taskId>      # 开始TDD工作流
task-master autopilot resume              # 恢复工作流
task-master autopilot next                # 获取下一步行动
task-master autopilot complete            # 完成当前阶段
task-master autopilot commit              # 创建commit
task-master autopilot status              # 查看状态
task-master autopilot abort               # 中止工作流
```

### 选项

```bash
--json                  # JSON格式输出
-v, --verbose           # 详细输出
-p, --project-root      # 指定项目根目录
```

---

## 🚀 完整TDD工作流程

### 阶段1: 启动工作流

```bash
# 为任务1启动TDD工作流
task-master autopilot start 1

# 预期输出：
# ✓ Workflow started for task 1
# ✓ Created branch: task-1
# ✓ Current phase: RED
# ✓ Subtask 1/5: 初始化 Vite + TypeScript + React 项目
# → Next action: Write a failing test
```

**Taskmaster做什么**:
1. 创建Git分支（task-1）
2. 初始化工作流状态
3. 设置当前阶段为RED
4. 指向第一个子任务

---

### 阶段2: RED Phase（编写失败的测试）

#### Step 1: 查看下一步操作
```bash
task-master autopilot next --json

# 输出：
{
  "action": "generate_test",
  "currentSubtask": {
    "id": 1,
    "title": "初始化 Vite + TypeScript + React 项目"
  },
  "phase": "RED"
}
```

#### Step 2: AI编写测试
```typescript
// tests/setup.test.ts
import { describe, it, expect } from 'vitest';
import { existsSync } from 'fs';

describe('Project Setup', () => {
  it('should have vite config', () => {
    expect(existsSync('vite.config.ts')).toBe(true);
  });
  
  it('should have tsconfig', () => {
    expect(existsSync('tsconfig.json')).toBe(true);
  });
});
```

#### Step 3: 运行测试（应该失败）
```bash
npm test

# 预期：测试失败
# ✗ 2 tests failed
```

#### Step 4: 报告RED完成
```bash
task-master autopilot complete --results '{
  "total": 2,
  "passed": 0,
  "failed": 2,
  "skipped": 0
}'

# 预期输出：
# ✓ RED phase complete
# ✓ Test validation: PASSED (tests failed as expected)
# ✓ Current phase: GREEN
# → Next action: Implement code to pass tests
```

**Taskmaster验证**:
- ✅ 测试必须失败（failed > 0）
- ✅ 如果测试通过，会报错并要求重写

---

### 阶段3: GREEN Phase（实现功能）

#### Step 1: 查看要求
```bash
task-master autopilot next

# 输出：
# Current phase: GREEN
# Action: implement_feature
# → Implement code to make tests pass
```

#### Step 2: AI实现代码
```bash
# 实际操作
npm create vite@latest . -- --template react-ts
npm install
```

#### Step 3: 运行测试（应该通过）
```bash
npm test

# 预期：测试通过
# ✓ 2 tests passed
```

#### Step 4: 报告GREEN完成
```bash
task-master autopilot complete --results '{
  "total": 2,
  "passed": 2,
  "failed": 0,
  "skipped": 0
}'

# 预期输出：
# ✓ GREEN phase complete
# ✓ Test validation: PASSED (all tests passed)
# ✓ Current phase: COMMIT
# → Next action: Commit changes
```

**Taskmaster验证**:
- ✅ 所有测试必须通过（failed == 0）
- ✅ 如果有失败测试，会报错并要求继续实现

---

### 阶段4: COMMIT Phase（保存进度）

```bash
task-master autopilot commit

# 预期输出：
# ✓ Created commit: abc1234
# ✓ Message: feat: 初始化 Vite + TypeScript + React 项目 (Task 1.1)
# ✓ Advanced to subtask 2/5: 配置开发工具链
# ✓ Current phase: RED
# → Next action: Write a failing test
```

**Taskmaster做什么**:
1. 自动生成commit消息
2. 创建Git commit（包含任务元数据）
3. 移动到下一个子任务
4. 重置阶段为RED

**Commit消息格式**:
```
feat: <子任务标题> (Task <taskId>.<subtaskId>)

Implemented by: taskmaster-autopilot
Task: <taskId>
Subtask: <subtaskId>
Phase: GREEN → COMMIT
```

---

### 循环：重复RED-GREEN-COMMIT

对每个子任务重复上述过程：

```
子任务1: RED → GREEN → COMMIT ✓
子任务2: RED → GREEN → COMMIT
子任务3: RED → GREEN → COMMIT
子任务4: RED → GREEN → COMMIT
子任务5: RED → GREEN → COMMIT
```

---

### 完成工作流

```bash
# 所有子任务完成后
task-master autopilot status

# 输出：
# ✓ All subtasks completed (5/5)
# ✓ Total commits: 5
# ✓ Branch: task-1
# → Next: Merge to main or create PR
```

---

## 🧪 测试准备步骤

### Step 1: 清理Git状态

```bash
# 提交或丢弃当前更改
git add -A
git commit -m "初始提交"

# 或者
git stash

# 验证干净状态
git status
# 应该显示: working tree clean
```

### Step 2: 创建测试项目

**方式A: 使用现有任务**
```bash
# 已有的任务1（项目初始化）可以用于测试
task-master show 1
```

**方式B: 创建新的测试任务**
```bash
# 创建一个简单的测试PRD
cat > .taskmaster/docs/autopilot_test_prd.txt << 'EOF'
# Simple Calculator Project

## Features
1. Add two numbers
2. Subtract two numbers
3. Multiply two numbers

## Requirements
- Use TypeScript
- Write tests with Vitest
- Follow TDD
EOF

# 解析PRD
task-master parse-prd .taskmaster/docs/autopilot_test_prd.txt --num-tasks=1

# 扩展任务
task-master expand --id=<new-task-id>
```

### Step 3: 配置测试框架

```bash
# 安装Vitest
npm install -D vitest

# 配置package.json
cat > package.json << 'EOF'
{
  "name": "autopilot-test",
  "scripts": {
    "test": "vitest run",
    "test:watch": "vitest"
  },
  "devDependencies": {
    "vitest": "^1.0.0"
  }
}
EOF

# 创建测试目录
mkdir -p tests
```

### Step 4: 验证前置条件

```bash
# ✅ 检查Git状态
git status | grep "working tree clean"

# ✅ 检查测试命令
npm test --version

# ✅ 检查任务
task-master list

# ✅ 检查子任务
task-master show <task-id>
```

---

## 🎯 完整测试流程

### 测试场景：计算器项目TDD

```bash
# 1. 准备环境
git add -A && git commit -m "准备Autopilot测试"
npm install -D vitest
mkdir -p tests src

# 2. 启动Autopilot
task-master autopilot start <task-id>

# 3. RED Phase - 编写测试
echo '
import { describe, it, expect } from "vitest";
import { add } from "../src/calculator";

describe("Calculator", () => {
  it("should add two numbers", () => {
    expect(add(2, 3)).toBe(5);
  });
});
' > tests/calculator.test.ts

npm test  # 应该失败

task-master autopilot complete --results '{
  "total": 1, "passed": 0, "failed": 1, "skipped": 0
}'

# 4. GREEN Phase - 实现功能
echo '
export function add(a: number, b: number): number {
  return a + b;
}
' > src/calculator.ts

npm test  # 应该通过

task-master autopilot complete --results '{
  "total": 1, "passed": 1, "failed": 0, "skipped": 0
}'

# 5. COMMIT Phase
task-master autopilot commit

# 6. 查看状态
task-master autopilot status
git log --oneline
```

---

## 📊 预期测试结果

### 成功标志

#### Autopilot启动
```
✅ 创建Git分支
✅ 初始化工作流状态
✅ 设置当前阶段为RED
✅ 指向第一个子任务
```

#### RED Phase验证
```
✅ 接受失败的测试结果
✅ 转换到GREEN阶段
❌ 拒绝通过的测试（验证严格性）
```

#### GREEN Phase验证
```
✅ 接受通过的测试结果
✅ 转换到COMMIT阶段
❌ 拒绝失败的测试（验证严格性）
```

#### COMMIT Phase
```
✅ 自动生成commit消息
✅ 创建Git commit
✅ 移动到下一个子任务
✅ 重置为RED阶段
```

#### 使用Claude Code
```
✅ 所有AI操作免费（$0.00）
✅ 高质量代码生成
✅ 准确的测试编写
```

---

## 🔍 关键测试点

### 1. 状态机验证

**测试点**: Autopilot严格执行状态转换

```
RED → GREEN ✅  (只能在测试失败后)
GREEN → COMMIT ✅  (只能在测试通过后)
COMMIT → RED ✅  (自动重置为下一循环)
```

**错误场景**:
```
RED → COMMIT ❌  (跳过GREEN)
GREEN → RED ❌  (倒退)
```

### 2. 测试结果验证

**RED阶段验证**:
```bash
# 正确：测试失败
--results '{"total":1,"passed":0,"failed":1,"skipped":0}' ✅

# 错误：测试通过
--results '{"total":1,"passed":1,"failed":0,"skipped":0}' ❌
# 应该报错: "RED phase requires failing tests"
```

**GREEN阶段验证**:
```bash
# 正确：测试通过
--results '{"total":1,"passed":1,"failed":0,"skipped":0}' ✅

# 错误：测试失败
--results '{"total":1,"passed":0,"failed":1,"skipped":0}' ❌
# 应该报错: "GREEN phase requires passing tests"
```

### 3. Git集成验证

**测试点**:
```bash
# Commit消息格式
git log -1 --pretty=%B
# 应该包含: feat: <title> (Task X.Y)

# Commit元数据
git log -1 --pretty=%B | grep "Task:"
git log -1 --pretty=%B | grep "Subtask:"

# 分支管理
git branch | grep "task-"
```

### 4. 进度跟踪验证

```bash
# 子任务计数
task-master autopilot status | grep "1/5"  # 第一个子任务
# 完成后
task-master autopilot status | grep "2/5"  # 第二个子任务
```

---

## 💡 Autopilot vs 手动CLI

### CLI模式（已测试）
```bash
# 完全手动
task-master expand --id=1
# 手动编写测试
# 手动实现代码
# 手动运行测试
# 手动提交Git
task-master set-status --id=1 --status=done
```

### Autopilot模式（待测试）
```bash
# 半自动化
task-master autopilot start 1
# AI编写测试
# AI实现代码
# Autopilot验证测试结果
# Autopilot自动commit
# Autopilot自动推进到下一个子任务
```

---

## 🎯 MCP集成（理论）

### MCP中使用Autopilot

根据官方文档，Autopilot也可以通过MCP使用：

```
"Start TDD workflow for task 1"
"What's the next action in autopilot?"
"Complete the RED phase with these test results"
"Commit the current changes"
```

**对应CLI**:
```bash
task-master autopilot start 1
task-master autopilot next
task-master autopilot complete --results '...'
task-master autopilot commit
```

---

## ⚠️ 当前阻塞因素

### 为什么还没测试Autopilot？

#### 1. Git状态不满足
```
要求: working tree clean
当前: 大量未暂存和未提交的文件
```

**解决**: 先提交或暂存当前工作

#### 2. 测试框架未确认
```
要求: npm test 可运行
当前: 未验证
```

**解决**: 安装Vitest并配置

#### 3. 需要合适的测试任务
```
要求: 适合TDD的任务
当前: 现有任务偏向配置类
```

**解决**: 创建简单的功能任务（如计算器）

---

## 🏁 测试准备清单

### 最小可测试环境

- [ ] **Git仓库干净**
  ```bash
  git status | grep "working tree clean"
  ```

- [ ] **测试框架安装**
  ```bash
  npm install -D vitest
  npm test  # 能运行
  ```

- [ ] **任务已创建**
  ```bash
  task-master list
  task-master show <id>  # 有子任务
  ```

- [ ] **Claude Code配置**
  ```bash
  cat .taskmaster/config.json | grep "claude-code"
  ```

### 完整测试环境

- [ ] **测试项目初始化**
  ```bash
  mkdir -p autopilot-test/{src,tests}
  cd autopilot-test
  npm init -y
  npm install -D vitest
  ```

- [ ] **Git仓库初始化**
  ```bash
  git init
  git add .
  git commit -m "Initial commit"
  ```

- [ ] **Taskmaster配置**
  ```bash
  task-master init
  # 配置.taskmaster/config.json使用claude-code
  ```

- [ ] **创建测试任务**
  ```bash
  # 编写简单的PRD
  task-master parse-prd test_prd.txt
  task-master expand --id=<id>
  ```

---

## 📚 相关文档

### 官方文档
- **Autopilot快速开始**: https://docs.task-master.dev/tdd-workflow/quickstart
- **AI Agent集成**: https://docs.task-master.dev/tdd-workflow/ai-agent-integration
- **MCP集成**: https://docs.task-master.dev/capabilities/mcp

### 本地测试报告
- **CLI测试**: `.taskmaster/reports/CLAUDE_CODE_INTEGRATION_TEST.md`
- **MCP指南**: `.taskmaster/reports/MCP_TEST_GUIDE.md`
- **完整总结**: `.taskmaster/reports/COMPLETE_TEST_SUMMARY.md`

---

## 🎯 推荐测试流程

### 快速验证（15分钟）

```bash
# 1. 清理环境 (2分钟)
git add -A && git commit -m "保存当前工作"

# 2. 创建测试项目 (5分钟)
mkdir -p autopilot-demo && cd autopilot-demo
npm init -y
npm install -D vitest
mkdir -p src tests

# 3. 配置Taskmaster (3分钟)
task-master init
# 修改config.json使用claude-code provider

# 4. 创建简单任务 (3分钟)
echo "# Calculator
Add two numbers" > prd.txt
task-master parse-prd prd.txt --num-tasks=1

# 5. 运行Autopilot (2分钟)
task-master autopilot start 1
```

### 完整测试（1小时）

1. **环境准备** (15分钟)
   - 清理Git状态
   - 安装测试框架
   - 创建测试项目

2. **第一个完整循环** (30分钟)
   - 启动Autopilot
   - RED: 编写测试
   - GREEN: 实现功能
   - COMMIT: 提交代码

3. **验证与文档** (15分钟)
   - 检查Git历史
   - 验证分支
   - 记录问题
   - 更新测试报告

---

## 💬 总结

**Autopilot TDD是什么？**
- 🤖 自动化的TDD工作流引擎
- 🔄 管理RED-GREEN-COMMIT循环
- ✅ 严格验证测试结果
- 📝 自动生成Git commits

**为什么还没测试？**
- ⚠️ Git仓库不干净
- ⚠️ 需要测试框架配置  
- ⚠️ 需要合适的测试任务

**如何测试？**
1. 清理Git状态
2. 安装测试框架
3. 创建简单任务
4. 运行完整TDD循环

**预期价值？**
- ✅ 严格的TDD纪律
- ✅ 自动化commit管理
- ✅ 清晰的进度跟踪
- ✅ 配合Claude Code免费使用

---

**测试状态**: ❌ **未测试**  
**阻塞因素**: Git状态、测试框架  
**优先级**: 🟡 **中** - 需要特殊准备

**建议**: 先完成CLI和MCP的基础测试，再准备Autopilot测试环境
