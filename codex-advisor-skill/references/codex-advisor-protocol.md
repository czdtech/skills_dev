# Codex 顾问 Skill 协议（草案）

本协议定义 **codex-advisor Skill** 的职责边界、触发条件以及输入 / 输出格式，用于指导：

- Claude Code 何时、如何调用 Codex 作为「苏格拉底式技术顾问」
- Bridge 进程如何把请求转化为 Codex CLI 调用

本文件只做「契约设计」，不涉及具体实现代码。

---

## 1. 角色与职责

Codex 在本工作室中的定位：

- 角色：技术顾问（Socratic Advisor）
- 目标：帮助 Claude Code **求真求实求是**，而不是替代它做决定或写代码
- 职责：
  - 提出澄清问题，识别需求中的模糊与冲突
  - 检查 Claude Code 方案中的隐含假设，指出不合理或危险之处
  - 提供一到多种替代方案，并分析各自的优缺点
  - 在必要时给出倾向性推荐与信心水平
- 明确不做：
  - 不直接修改仓库代码
  - 不直接执行命令或脚本
  - 不绕过 Claude Code 和 任务管理流程 单独重构任务结构

---

## 2. 触发条件

Claude Code 只有在满足以下之一时才应调用 codex-advisor：

1. 任务影响多个模块 / 子系统，存在明显架构或边界问题
2. 任务涉及性能 / 安全 / 数据一致性等高风险领域
3. 方案需要在两种以上设计之间做权衡（例如同步 vs 异步、单体 vs 微服务）
4. 用户显式要求「需要讨论方案 / 想听专家意见」

对于单文件小改、明显 bugfix 这类简单任务，可以不调用 codex-advisor，直接规划 + 执行。

---

## 3. 调用模式与轮数限制

为了避免无尽讨论，本协议设计为「最多两轮」：

- **第 1 轮：初次评审**
  - 输入：问题 + 背景 + Claude Code 的候选方案
  - 输出：澄清问题 + 假设检查 + 初步替代方案 + 风险点

- **第 2 轮：信息补全后的最终权衡**（可选）
  - 输入：补充信息 + 重点问题
  - 输出：权衡分析 + 推荐方案 + 信心等级

Claude Code 必须在第 2 轮结束后做出决策并向前推进；如仍有重大不确定，应记录为 任务管理流程 上的新任务，而不是继续与 Codex 反复往返。

---

## 4. 输入契约（Claude Code → codex-advisor Skill）

codex-advisor Skill 的输入建议采用结构化 JSON（具体序列化形式由桥接层决定），逻辑字段如下：

```jsonc
{
  "problem": "string",          // 当前要解决的核心问题（1-3 句）
  "context": "string",          // 与决策直接相关的背景：技术栈、约束、现有结构。
  "candidate_plans": [           // Claude Code 拟定的 1~2 个候选方案
    {
      "name": "PlanA",
      "description": "string",  // 方案描述
      "assumptions": ["..."],   // 自己意识到的关键假设
      "suspicions": ["..."]     // 自己觉得不踏实的点
    }
  ],
  "questions_for_codex": [       // 希望 Codex 聚焦回答的问题
    "我们是否选对了拆分边界？",
    "哪种方案对未来演进更安全？"
  ],
  "non_goals": ["..."],         // 本次不讨论的内容，避免跑题
  "phase": "initial|final"      // 调用阶段：初次评审 or 补充信息后的最终权衡
}
```

备注：

- `candidate_plans` 至少应包含一个方案，避免把“完全空白”的问题扔给 Codex
- `context` 应尽量包含：
  - 关键文件/模块名称
  - 当前架构/数据流的简版描述
  - 重要非功能需求（性能、可用性、合规等）

---

## 5. 输出契约（codex-advisor Skill → Claude Code）

Skill 返回的结果也应是结构化 JSON，便于 Claude Code 和 任务管理流程 进一步处理：

```jsonc
{
  "clarifying_questions": ["..."],  // Codex 认为仍需澄清的问题（数量有限）
  "assumption_check": [             // 对每条关键假设的评价
    {
      "text": "我们假设 X 服务在 Y 时间窗口内可以下线重启",
      "status": "plausible|risky|invalid",
      "comment": "..."
    }
  ],
  "alternatives": [                 // 替代方案（至少 1 个）
    {
      "name": "AltPlan1",
      "description": "string",
      "pros": ["..."],
      "cons": ["..."],
      "applicable_when": "string" // 适用前提
    }
  ],
  "tradeoffs": [                    // 按维度对方案进行权衡
    {
      "dimension": "maintainability|risk|performance|consistency|complexity",
      "notes": "string"           // 不要求打分，文字说明即可
    }
  ],
  "recommendation": {               // Codex 的推荐意见
    "preferred_plan": "PlanA|PlanB|AltPlan1|none",
    "reason": "string",           // 为什么这样推荐
    "confidence": "low|medium|high"
  },
  "followup_suggestions": ["..."], // 建议后续可以补充的分析或验证
  "raw_text": "string"             // Codex 的自然语言总结（便于人读）
}
```

约束：

- `clarifying_questions` 数量应有限（例如 ≤ 5），避免无休止提问
- 如 `phase = "final"`，Codex 应少提新问题，多做收益/风险权衡
- `recommendation.preferred_plan` 可以是 `none`，但必须说明原因

---

## 6. Bridge 与 pm2 的接口位置

在具体实现中，codex-advisor Skill 不直接调用 Codex CLI，而是：

1. 将上述输入契约序列化为 JSON
2. 通过本地协议（例如 HTTP POST 到 `http://127.0.0.1:PORT/analyze`）发送给 `codex-bridge` 进程
3. 等待 `codex-bridge` 返回符合输出契约的 JSON

`codex-bridge` 进程由 pm2 管理：

- pm2 负责启动 / 重启 / 日志
- bridge 内部负责：
  - 将请求转换为 Codex CLI 调用
  - 控制超时与重试
  - 解析 Codex 输出为结构化 JSON

这样 Claude Code 只与 codex-advisor Skill 打交道，不感知 Codex CLI 的细节与稳定性问题。

---

## 7. 错误与 Fallback 策略

codex-advisor Skill 需要对几类错误做区分：

1. **输入错误**（必填字段缺失 / 格式不对）
   - 返回统一的错误结构，提醒 Claude Code 修正调用格式

2. **桥接层错误**（bridge 未响应 / pm2 进程异常）
   - 返回错误类型为 `bridge_failure`
   - Claude Code 可以据此触发 `CODEX_FALLBACK`，自己进行简化分析

3. **Codex 自身错误**（模型返回异常 / 超出预算）
   - 返回错误类型为 `codex_failure` 并附带原始信息摘要
   - Claude Code 可以选择：
     - 降级为只用自己的方案 + 任务管理流程
     - 或提示用户当前无法获取 Codex 顾问意见

所有错误都不应让 Claude Code 卡死在等待状态；最多一次重试，之后必须返回明确的错误信息。

---

## 8. 与 任务管理流程 的衔接

Codex 的输出并不直接变成任务，而是由 Claude Code 进行二次消化：

1. Claude Code 读取 `recommendation` 和 `tradeoffs`，选择最终方案
2. 根据 `assumption_check` 和 `alternatives`，提炼出：
   - 明确要做的任务（交给 Droid）
   - 暂时搁置的风险或后续分析（写成 任务管理流程 上的后续任务）
3. 使用 任务管理流程 工具更新任务图，使 Codex 的意见被“固化”为可执行或可跟踪的条目

这样可以保证：

- Codex 始终停留在“方案与风险”的层面
- 由 Claude Code 决定如何将这些建议转化为实际任务

