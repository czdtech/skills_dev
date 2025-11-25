# Droid 执行器 Skill 协议（草案）

本协议定义 **droid-executor Skill** 的职责边界、触发条件以及输入 / 输出格式，用于指导：

- Claude Code 如何将「已经过讨论的方案」拆解为可执行任务交给 Droid
- Bridge 进程如何将这些任务转化为 Droid / Factory CLI 调用

目标：让 Droid 成为稳定、可观测的「执行型程序员」，而不是重新做架构决策。

---

## 1. 角色与职责

Droid 在本工作室中的定位：

- 角色：执行型程序员（Implementation Executor）
- 目标：在既定方案和约束下，高质量地完成具体实现与命令执行
- 职责：
  - 按 Claude Code 给出的执行合同修改代码（新增 / 删除 / 重构）
  - 运行指定的测试、脚本或构建命令
  - 返回清晰的变更摘要、测试结果与关键日志
- 明确不做：
  - 不重新做架构决策或推翻已经与 Codex 商定的方案
  - 不在任务范围之外随意拓展改动
  - 不静默吞掉错误：所有失败必须显式回报

---

## 2. 触发条件

Claude Code 只有在下列条件同时满足时才应调用 droid-executor：

1. 上层方案已经确定（必要时经过 Codex 顾问评审）
2. 对当前子任务有清晰的**输入 / 输出**定义及验收标准
3. 任务的影响范围（文件 / 模块）基本明确

对于探索性很强、方案尚未定型的工作，应先与 Codex / 用户补充讨论，不宜直接调用 Droid。

---

## 3. 调用模式

推荐的调用方式是「一任务一调用」：

- Claude Code 按 任务管理流程 任务图选定一个子任务
- 将该子任务的执行合同打包成一次对 droid-executor Skill 的调用
- Droid 完成后返回结果，由 Claude Code 验收并更新 任务管理流程 状态

如某个子任务过大（例如「重构整个子系统」），应在调用前先进一步拆分为更细粒度的执行任务。

---

## 4. 输入契约（Claude Code → droid-executor Skill）

droid-executor Skill 的输入建议采用结构化 JSON，逻辑字段如下（示例字段名，实际序列化由桥接层决定）：

```jsonc
{
  "task_id": "string",             // 对应 任务管理流程 中的任务标识，可选但推荐
  "objective": "string",           // 本次执行的核心目标（1-2 句）
  "context": {
    "repo_root": "string",        // 仓库根目录路径
    "files_of_interest": ["src/...", "tests/..."] // 可能会涉及的文件或目录
  },
  "instructions": "string",        // 具体要做什么，Claude Code 写成清晰的执行说明
  "constraints": [                  // 需要严格遵守的约束
    "不要修改公共 API 的签名",
    "保持现有日志格式不变"
  ],
  "acceptance_criteria": [          // 验收标准（可由 Codex/Claude Code 定义）
    "npm test 全部通过",
    "新加的函数都有单元测试"
  ],
  "execution_mode": "code|command|mixed", // 以改代码为主、以跑命令为主，或两者都有
  "suggested_commands": [           // 可选：推荐执行的命令序列
    "npm test",
    "npm run lint"
  ],
  "max_runtime_seconds": 600,       // 本次任务允许的最大执行时间
  "notes_for_human": "string"      // 可选：给人类阅读的补充说明
}
```

说明：

- `instructions` 应避免含糊表述，如「优化一下」，而应尽量具体：
  - 例如：「将 src/utils/parser.ts 的 7 个回调函数改为 async/await，保持导出接口不变」
- `acceptance_criteria` 是 Claude Code 验收时的依据，应尽量具体可验证。

---

## 5. 输出契约（droid-executor Skill → Claude Code）

Skill 返回的结果也应是结构化 JSON，便于 Claude Code 与 任务管理流程 使用：

```jsonc
{
  "status": "success|partial|failed", // 本次执行整体结果
  "summary": "string",                // 对本次执行的简要总结
  "files_changed": [                   // 修改过的文件列表
    {
      "path": "src/utils/parser.ts",
      "change_type": "modified|added|deleted",
      "highlights": ["重构 parseFile 为 async/await"]
    }
  ],
  "commands_run": [                    // 实际执行的命令
    {
      "command": "npm test",
      "exit_code": 0,
      "stdout_excerpt": "...",
      "stderr_excerpt": "..."
    }
  ],
  "tests": {                           // 重点测试结果（可选）
    "passed": true,
    "details": "24 tests passed"
  },
  "logs": ["..."],                    // 关键日志片段（适当截断）
  "issues": [                          // 发现的问题或阻塞因素
    {
      "type": "test_failure|env_issue|unclear_requirement|conflict",
      "description": "string",
      "suggested_action": "string"
    }
  ]
}
```

约束：

- `status = partial` 时，应至少包含一条 `issues`，说明未完成的部分和原因
- 即使 `status = failed`，也应尽量返回已执行的命令和日志，便于 Claude Code 调试

---

## 6. Bridge 与 pm2 的接口位置

与 Codex 顾问类似，droid-executor Skill 不直接调用 Droid / Factory CLI，而是：

1. 将输入契约序列化为 JSON
2. 通过本地协议（例如 HTTP POST 到 `http://127.0.0.1:PORT/execute`）发送给 `droid-bridge` 进程
3. 等待 `droid-bridge` 返回符合输出契约的 JSON

`droid-bridge` 进程由 pm2 管理：

- pm2 负责：启动 / 重启 / 日志 / 资源占用监控
- bridge 内部负责：
  - 将任务转化为具体的 `droid` / `factory` CLI 调用（例如 `droid exec "..."`）
  - 控制执行超时与重试策略
  - 收集命令输出、整理为结构化 JSON

这样 Claude Code 只与 droid-executor Skill 交互，不直面 CLI 的稳定性问题。

---

## 7. 错误与 Fallback 策略

droid-executor Skill 需要对不同错误做区分：

1. **输入错误**（缺少字段 / 不合法约束）
   - 返回统一错误结构，提示 Claude Code 修正调用内容

2. **桥接层错误**（bridge 不响应 / pm2 进程异常）
   - 返回错误类型为 `bridge_failure`
   - Claude Code 可据此触发 `DROID_FALLBACK`：
     - 由 Claude Code 自己执行部分或全部实现
     - 或暂时只更新 任务管理流程，将任务标记为「阻塞」

3. **执行错误**（命令失败 / 测试未通过 / 冲突）
   - 返回 `status = partial|failed`，并在 `issues` 中描述：
     - 是环境问题（缺依赖、配置错误）？
     - 是需求问题（验收标准互相矛盾）？
     - 还是实现问题（测试红、语法错误）？

Skill 不负责自动重试多次长任务；重试策略由 bridge 层控制，Skill 只报告最终结果。

---

## 8. 与 Codex / 任务管理流程 的衔接

### 与 Codex 的关系

- Droid 不参与架构决策，对已定方案如有疑问，应通过 `issues` 向 Claude Code 反馈
- Claude Code 如发现 Droid 无法在既定方案下完成任务，可重新请 Codex 顾问评估方案本身，而不是要求 Droid「想办法凑合」

### 与 任务管理流程 的关系

- 每次调用 droid-executor 通常对应 任务管理流程 上的一个具体任务
- Claude Code 根据返回的 `status` 和 `issues`：
  - 将任务标记为完成 / 部分完成 / 阻塞
  - 对于 `issues` 中的重要项，必要时拆分出新的任务（例如「补充缺失的测试环境配置」）

通过这三者的协同，可以让「设计（Codex）→ 任务（任务管理流程）→ 实现（Droid）」形成闭环，而 Claude Code 始终是唯一对人类负责的中控。
