# Claude Code 系统提示词对比分析

**对比日期**: 2025-11-21  
**对比对象**:
- **文章提示词**: Linus Torvalds 角色 + 严格工作流
- **当前提示词**: Multi-Agent Studio 多角色协作

---

## 📋 整体对比

| 维度 | 文章提示词 | 当前提示词 | 评价 |
|------|-----------|-----------|------|
| **角色定位** | Linus Torvalds（独立大神）| 首席架构师 + 中控 | 更符合协作场景 |
| **工作模式** | 强制 Codex 执行所有代码任务 | 多角色协作，按需调用 | 更灵活 |
| **Codex 使用** | 100% 强制（所有代码任务）| 仅复杂/高风险时使用 | 更高效 |
| **Droid 角色** | ❌ 无（仅 Codex）| ✅ 专门的执行型程序员 | **关键差异** |
| **Taskmaster** | ❌ 无 | ✅ 任务管理器 | 更系统化 |
| **语言风格** | Linus 独特风格（直接、批判）| 专业技术协作 | 各有特色 |
| **工作流复杂度** | ⭐⭐⭐⭐⭐ 非常详细 | ⭐⭐⭐ 适中 | 文章更详尽 |

---

## 🎭 核心差异 #1：角色定位

### 文章提示词：Linus Torvalds

```markdown
You are Linus Torvalds. Obey the following priority stack...

1. Role + Safety: stay in character, enforce KISS/YAGNI/never break userspace, 
   think in English, respond to the user in Chinese, stay technical.
```

**特点**:
- 🎭 **强烈的角色扮演**: Linus 的工程哲学和风格
- 🔨 **严格的工程原则**: KISS/YAGNI/Never break userspace
- 🗣️ **特定沟通风格**: 批判性、直接、技术导向

**示例语气**:
> "这个设计**明显有问题**，违反了 YAGNI 原则..."
> "代码写得像**屎**，我们需要重构..."

---

### 当前提示词：首席架构师 / 中控

```markdown
- **Claude Code（你）**：首席架构师 / 中控  
  - 负责：理解需求、收集上下文、设计方案、拆分任务、验收结果、向人类汇报。  
  - 不在外部角色正常可用时独自完成全部实现。
```

**特点**:
- 👔 **专业协调者**: 中立、系统化、协作导向
- 🤝 **多角色协作**: 与 Codex/Droid/Taskmaster 协作
- 📊 **项目管理**: 任务拆分、验收、汇报

**示例语气**:
> "根据 Codex 的建议，我们采用方案 A..."
> "Droid 已完成任务，现在验收结果..."

---

## 🔑 核心差异 #2：Codex 使用策略

### 文章提示词：强制 100% 使用

```markdown
2. Workflow Contract: Claude Code performs intake, context gathering, planning, 
   and verification only; **every edit, or test must be executed via Codex skill** (`codex`). 
   Switch to direct execution only after Codex is unavailable or fails twice consecutively, 
   and log `CODEX_FALLBACK`.
```

**关键规则**:
- ⚠️ **强制调用**: 所有代码任务必须通过 Codex
- ⚠️ **禁止直接编码**: Claude Code 不能自己写代码
- 🔄 **失败才回退**: 连续失败 2 次才允许 Claude Code 接管

**工作流**:
```
任务 → 必须调用 Codex → 失败 → 重试 → 再失败 → 才允许 Claude Code 写代码
```

**优势**:
- ✅ 强制使用高级模型（Codex gpt-5）
- ✅ 避免 Claude Code 写低质量代码

**劣势**:
- ❌ 简单任务也要调用（效率低）
- ❌ 上下文消耗大
- ❌ 响应延迟长

---

### 当前提示词：按需灵活调用

```markdown
- **Codex（codex-advisor Skill）**：技术顾问  
  - 负责：对 Claude Code 拟定的方案进行苏格拉底式评审...  
  - 不直接修改代码或执行命令。

4. **架构方案设计与 Codex 评审**  
   - 当任务影响多个模块 / 涉及高风险 / 需要方案权衡时：  
     - 调用 codex-advisor Skill...
```

**关键规则**:
- ✅ **按需调用**: 仅复杂/高风险时使用
- ✅ **顾问角色**: Codex 不写代码，只提供建议
- 🎯 **明确触发条件**: 
  - 影响多个模块
  - 涉及高风险
  - 需要方案权衡
  - 用户明确要求

**工作流**:
```
简单任务 → Claude Code 或 Droid 直接处理
复杂任务 → Codex 评审 → Claude Code 决策 → Droid 执行
```

**优势**:
- ✅ 效率更高（简单任务不浪费）
- ✅ 上下文消耗低
- ✅ 响应速度快
- ✅ 各角色职责清晰

---

## 💎 核心差异 #3：Droid 的角色

### 文章提示词：无 Droid 角色

**执行方式**:
```markdown
every edit, or test must be executed via Codex skill (`codex`).
```

- 所有代码任务都通过 Codex
- Codex 既是顾问又是执行者
- 用的是 Codex CLI 的 `workspace-write` 模式

**问题**:
- ❌ 角色混淆（顾问 vs 执行者）
- ❌ Codex 可能过度思考简单任务
- ❌ 上下文浪费在执行层面

---

### 当前提示词：Droid 专职执行

```markdown
- **Droid（droid-executor Skill）**：执行型程序员  
  - 负责：在方案已定的前提下，根据执行合同修改代码、运行测试与命令...  
  - 不重新设计架构，也不擅自扩大改动范围。

6. **实现与执行（Droid 为主）**  
   - 优先通过 droid-executor Skill 调用 Droid 完成具体修改与命令执行。
```

**关键设计**:
- ✅ **清晰分工**: 
  - Codex = 想（顾问）
  - Droid = 做（执行）
- ✅ **专注执行**: Droid 不做架构决策
- ✅ **效率优化**: 执行任务用专门工具（Droid CLI）

**优势**:
- ✅ 各司其职，避免角色混淆
- ✅ Codex 专注深度推理
- ✅ Droid 专注快速执行
- ✅ 上下文使用更高效

---

## 📊 工作流对比

### 文章提示词工作流

```
1. Intake & Reality Check (分析)
2. Context Gathering (分析，5-8 工具调用)
3. Exploration & Decomposition (分析，复杂任务)
4. Planning (分析，≥3 步)
5. Execution (执行) → **所有任务调用 Codex**
6. Verification (分析)
7. Handoff (总结)
```

**特点**:
- ⭐⭐⭐⭐⭐ **极度详细**: 每个阶段都有严格定义
- 🔒 **强制流程**: 必须遵守顺序
- 📏 **量化指标**: 5-8 工具调用、≥3 步计划、≥90% 测试覆盖

---

### 当前提示词工作流

```
1. 接单与现实检验
2. 代码与上下文探索
3. 澄清问题与补全需求
4. 架构方案设计与 Codex 评审 (按需)
5. 任务拆分与排程 (Taskmaster)
6. 实现与执行 (Droid 为主)
7. 质量检查与总结
```

**特点**:
- ⭐⭐⭐ **适度详细**: 平衡灵活性和规范性
- 🤝 **多角色协作**: 每个阶段可能涉及不同角色
- 📋 **任务管理集成**: Taskmaster 追踪进度

---

## 🎯 具体差异详解

### 1. 上下文收集

#### 文章提示词

```markdown
<context_gathering>
Budget: 5–8 tool calls first pass (plan mode: 8–12 for broader discovery); 
justify overruns.

Deep Analysis Delegation:
- Trigger: When understanding complex function logic, design patterns, 
  architecture decisions, or call chains is required.
- Action: Invoke `codex` skill to perform the analysis.
```

**强调**:
- 📊 **量化预算**: 5-8 次工具调用
- 🔍 **深度分析触发**: 复杂逻辑 → 调用 Codex
- ⚠️ **超预算需解释**: 强制控制
- 🚫 **Claude Code 禁止深入**: 只能浅层探索

---

#### 当前提示词

```markdown
2. **代码与上下文探索**  
   - 使用 `rg`/`fd`/阅读关键文件，构建对相关模块的理解。  
   - 涉及复杂调用链、性能、安全等问题时，在后续阶段考虑调用 Codex 顾问。
```

**强调**:
- 🔧 **工具导向**: rg/fd 优先
- 🤔 **后续决策**: 不是立即调用 Codex
- ✅ **Claude Code 可深入**: 允许自主探索

**差异**:
- 文章：严格限制 Claude Code 的探索深度
- 当前：信任 Claude Code 的判断能力

---

### 2. 执行阶段

#### 文章提示词

```markdown
5. Execution (execution mode): 
   stop reasoning, delegate to Codex skill sequentially. 
   Invoke `codex` skill for each step, tag each call with the plan step. 
   On failure: capture stderr/stdout, decide retry vs fallback, keep log aligned.
```

**关键点**:
- 🛑 **停止推理**: Claude Code 进入"执行模式"
- 🤖 **完全委托**: 每一步都调用 Codex
- 📝 **标记步骤**: 关联计划步骤
- 🔁 **失败处理**: 重试或回退

**示例调用**:
```shell
# 步骤 1
codex exec "Refactor callbacks to async/await in parser.ts"

# 步骤 2
codex exec "Add unit tests for parser functions"

# 步骤 3
codex exec "Run npm test"
```

---

#### 当前提示词

```markdown
6. **实现与执行（Droid 为主）**  
   - 对每个准备执行的任务，写出清晰的执行合同...  
   - 优先通过 droid-executor Skill 调用 Droid 完成具体修改与命令执行。  
   - Claude Code 对 Droid 的结果做验收...
```

**关键点**:
- 📋 **执行合同**: 明确 objective/instructions/constraints
- ⚡ **Droid 优先**: 用专门的执行工具
- ✅ **验收机制**: Claude Code 检查结果
- 🤔 **保持思考**: Claude Code 不进入"无脑模式"

**示例调用**:
```json
POST http://localhost:3002/execute
{
  "objective": "Refactor callbacks to async/await",
  "instructions": "...",
  "constraints": ["Keep API unchanged"],
  "acceptance_criteria": ["Tests pass"]
}
```

---

### 3. Codex 调用细节

#### 文章提示词

```markdown
- Default settings: gpt-5, full access, search enabled
- Capture errors, retry once if transient, document fallbacks.
```

**Codex 配置**:
- 模型: `gpt-5`
- 沙盒: `full access` (可修改代码)
- 搜索: 启用

**调用示例**:
```python
uv run ~/.claude/skills/codex/scripts/codex.py \
  "Refactor parser.ts to use async/await" \
  gpt-5-codex \
  ~/projects/my-app
```

---

#### 当前提示词

```markdown
- Codex：  
  - 仅在复杂/高风险/多方案权衡或用户明确要求时调用；  
  - 调用时必须提供至少一个候选方案和已知假设；  
  - 以 codex-advisor Skill 的 schema 输出为准，不要求 Codex 写代码。
```

**Codex 配置**:
- 模型: 依赖用户配置（默认）
- 沙盒: `read-only` (只分析，不写代码)
- 输出: JSON Schema 结构化输出

**调用示例**:
```json
POST http://localhost:3001/analyze
{
  "problem": "Choose state management approach",
  "candidate_plans": [
    {"name": "Redux", ...},
    {"name": "Zustand", ...}
  ],
  "focus_areas": ["complexity", "performance"]
}
```

---

## 🏆 优劣势对比

### 文章提示词

**优势**:
1. ✅ **强制使用高级模型**: 保证代码质量
2. ✅ **详细的流程规范**: 新手友好
3. ✅ **量化指标**: 5-8 工具调用、≥90% 测试覆盖
4. ✅ **Linus 风格**: 独特、有趣、工程哲学强

**劣势**:
1. ❌ **效率问题**: 简单任务也强制调用 Codex
2. ❌ **上下文浪费**: 每次执行都加载完整上下文
3. ❌ **响应延迟**: 调用外部工具增加延迟
4. ❌ **角色混淆**: Codex 既是顾问又是执行者
5. ❌ **单一工具**: 只有 Codex，缺少分工

---

### 当前提示词

**优势**:
1. ✅ **角色清晰**: Codex 想、Droid 做、Taskmaster 管
2. ✅ **按需调用**: 简单任务不浪费资源
3. ✅ **效率高**: 各角色专注自己的领域
4. ✅ **可扩展**: 易于添加新角色
5. ✅ **生产导向**: 适合实际项目

**劣势**:
1. ⚠️ **规范性弱**: 没有强制量化指标
2. ⚠️ **学习曲线**: 需要理解多角色协作
3. ⚠️ **依赖判断**: 依赖 Claude Code 的调用决策

---

## 💡 关键设计哲学差异

### 文章提示词：强制委托 + 严格流程

**核心理念**:
- 🤖 "Claude Code 只做分析，Codex 做所有执行"
- 📏 "严格遵守流程，量化每个阶段"
- 🔒 "强制使用高级工具，避免低质量输出"

**适合场景**:
- 不信任 Claude Code 的代码能力
- 需要强制使用 GPT-5 级别模型
- 团队需要严格规范

---

### 当前提示词：协作分工 + 灵活调用

**核心理念**:
- 🤝 "各司其职，按需协作"
- 🎯 "简单任务快速处理，复杂任务深度分析"
- ⚡ "效率和质量的平衡"

**适合场景**:
- 信任 Claude Code 的判断能力
- 需要高效处理多种任务
- 实际生产环境

---

## 🎯 实际使用对比

### 场景 1：简单 Bug 修复

**任务**: 修复一个空指针异常

#### 文章方案

```
1. Context Gathering (5-8 工具调用)
2. Exploration (因为是简单任务，可能跳过)
3. Planning (写 3 步计划)
4. Execution:
   codex exec "Fix null pointer in user.py line 42"
   等待 Codex 响应...
5. Verification
6. Handoff
```

**时间**: ~5-10 分钟  
**上下文消耗**: ~10-15K tokens

---

#### 当前方案

```
1. 快速探索 (rg 搜索相关代码)
2. 发现简单 bug
3. 调用 Droid:
   POST /execute {
     "objective": "Fix null pointer",
     "instructions": "Add null check at line 42"
   }
4. 验收
5. 完成
```

**时间**: ~2-3 分钟  
**上下文消耗**: ~5-8K tokens

**效率提升**: 50%+

---

### 场景 2：架构决策

**任务**: 选择状态管理方案（Redux vs Zustand）

#### 文章方案

```
1-3. 前期探索和规划
4. Execution:
   codex exec "Analyze state management options and implement the best one"
   # Codex 会分析并直接实现
5-6. 验收和总结
```

**问题**:
- ❌ Codex 既分析又实现（角色混淆）
- ❌ 如果分析有误，实现也会错
- ❌ 难以在实现前停下来讨论

---

#### 当前方案

```
1-3. 前期探索，Claude Code 起草 2 个方案
4. Codex 评审:
   POST /analyze {
     "problem": "Choose state management",
     "candidate_plans": [Redux, Zustand],
     "focus_areas": ["complexity", "learning_curve"]
   }
   → 返回结构化分析
5. Claude Code 与用户讨论，做决策
6. Droid 执行:
   POST /execute {
     "objective": "Implement Zustand state management",
     ...
   }
```

**优势**:
- ✅ 分析和实现分离
- ✅ 决策点可以暂停讨论
- ✅ 各角色聚焦专长

---

## 📊 总结对比表

| 维度 | 文章提示词 | 当前提示词 | 推荐 |
|------|-----------|-----------|------|
| **角色扮演** | Linus Torvalds | 首席架构师 | 看偏好 |
| **Codex 使用** | 100% 强制 | 按需调用 | **当前** |
| **工具角色** | Codex（全能）| Codex（顾问）+ Droid（执行）| **当前** |
| **任务管理** | 无 | Taskmaster | **当前** |
| **效率** | 中 | 高 | **当前** |
| **上下文消耗** | 高 | 低 | **当前** |
| **规范性** | 极强 | 适中 | 看需求 |
| **灵活性** | 低 | 高 | **当前** |
| **生产适用** | 中 | 高 | **当前** |

---

## 🎯 最终建议

### 保持当前提示词！

**原因**:
1. ✅ **角色分工更清晰**: Codex 顾问 + Droid 执行
2. ✅ **效率更高**: 按需调用，不浪费资源
3. ✅ **更适合生产**: 实际项目需要灵活性
4. ✅ **可扩展**: 已有 Taskmaster 集成

### 可借鉴文章的优点

1. **量化指标**（可选）:
   ```markdown
   - 上下文收集预算: 5-8 工具调用
   - 测试覆盖率要求: ≥90%
   ```

2. **深度分析委托**:
   ```markdown
   当分析复杂调用链时，可委托给 Codex
   ```

3. **Linus 风格**（如果喜欢）:
   ```markdown
   保持 KISS/YAGNI/Never break userspace 原则
   ```

---

**结论**: 你的提示词设计更符合多角色协作的生产环境，保持现状！✅

详细对比已保存！📄
