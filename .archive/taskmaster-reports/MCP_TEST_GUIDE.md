# 🔌 Taskmaster MCP功能测试指南

**测试日期**: 2025-11-23  
**MCP服务器**: task-master-ai  
**配置文件**: `.mcp.json`

---

## 📋 测试状态

### CLI功能测试
✅ **已完成** - 详见 `CLAUDE_CODE_INTEGRATION_TEST.md`

### MCP功能测试
⚠️ **待用户测试** - 需要IDE重启

---

## 🎯 MCP vs CLI 对比

### CLI模式（已测试）✅
```bash
# 通过命令行直接调用
task-master parse-prd docs/prd.txt
task-master list
task-master next
task-master expand --id=1
task-master analyze-complexity
```

**特点**:
- ✅ 在终端中运行
- ✅ 直接命令行交互
- ✅ 适合脚本和自动化
- ✅ 读取`.taskmaster/config.json`中的provider配置

---

### MCP模式（待测试）⚠️
```
# 在IDE聊天界面中使用自然语言
"Can you parse my PRD at docs/prd.txt?"
"What's the next task I should work on?"
"Show me task 1"
"Expand task 2"
"Analyze the complexity of all tasks"
```

**特点**:
- ✅ 在IDE中通过聊天使用
- ✅ 自然语言交互
- ✅ 无需记忆命令
- ✅ 与代码编辑器集成
- ✅ 通过MCP协议调用

---

## 🔧 MCP配置状态

### 当前配置

**文件**: `.mcp.json`
```json
{
  "mcpServers": {
    "task-master-ai": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "task-master-ai"],
      "env": {
        "TASK_MASTER_TOOLS": "standard"
      }
    }
  }
}
```

**关键配置**:
- ✅ `TASK_MASTER_TOOLS: "standard"` - 加载15个常用工具
- ✅ 不需要API密钥（使用`.taskmaster/config.json`中的Claude Code配置）

---

## 📚 可用的MCP工具

根据官方文档，Taskmaster MCP服务器提供以下工具：

### Core工具（7个）- ✅ 包含在standard模式
1. `get_tasks` - 获取任务列表
2. `next_task` - 获取下一个应该做的任务
3. `get_task` - 获取特定任务详情
4. `set_task_status` - 更新任务状态
5. `update_subtask` - 更新子任务
6. `parse_prd` - 解析PRD生成任务
7. `expand_task` - 扩展任务为子任务

### Standard工具（15个）- ✅ 当前配置
Core工具 + 以下8个:
8. `initialize_project` - 初始化项目
9. `analyze_project_complexity` - 分析项目复杂度
10. `expand_all` - 扩展所有任务
11. `add_subtask` - 添加子任务
12. `remove_task` - 删除任务
13. `generate` - 生成内容
14. `add_task` - 添加新任务
15. `complexity_report` - 生成复杂度报告

### All工具（36个）
包含所有功能，包括：
- 项目设置
- 任务管理
- 分析
- 依赖管理
- 标签管理
- 研究功能
- 等等...

---

## 🧪 MCP测试步骤

### 前提条件
1. ✅ Claude Code已安装(2.0.46)
2. ✅ `.mcp.json`已配置
3. ✅ `.taskmaster/config.json`使用claude-code provider
4. ⚠️ **需要重启IDE** - 让MCP配置生效

### 测试步骤

#### 步骤1: 重启Claude Code或IDE
```bash
# 如果使用Claude Code CLI
# 退出当前会话并重新启动

# 如果使用其他IDE（Cursor等）
# 完全退出并重新启动
```

#### 步骤2: 验证MCP服务器已加载
在IDE聊天界面中询问：
```
"What MCP tools are available?"
"Show me the task-master-ai tools"
```

**预期结果**: 应显示15个standard工具（或更多）

#### 步骤3: 测试基础查询功能
```
"Can you list all tasks in taskmaster?"
"What's the next task I should work on?"
"Show me task 1"
```

**对应CLI**: 
- `task-master list`
- `task-master next`
- `task-master show 1`

#### 步骤4: 测试AI功能（关键！）
```
"Can you parse my PRD at .taskmaster/docs/test_prd_claude_code.txt?"
"Can you expand task 2?"
"Can you analyze the complexity of all tasks?"
```

**对应CLI**:
- `task-master parse-prd ...`
- `task-master expand --id=2`
- `task-master analyze-complexity`

#### 步骤5: 测试任务管理
```
"Can you set task 1 status to in-progress?"
"Can you add a subtask to task 2 with title 'Test feature X'?"
```

**对应CLI**:
- `task-master set-status --id=1 --status=in-progress`
- `task-master add-subtask --parent=2 --title="Test feature X"`

---

## 🔍 MCP vs CLI 功能对照

| 功能 | CLI命令 | MCP自然语言 | 状态 |
|------|---------|------------|------|
| **列出任务** | `task-master list` | "List all tasks" | CLI✅ MCP⚠️ |
| **下一个任务** | `task-master next` | "What's next?" | CLI✅ MCP⚠️ |
| **查看任务** | `task-master show 1` | "Show me task 1" | CLI✅ MCP⚠️ |
| **解析PRD** | `task-master parse-prd <file>` | "Parse my PRD at <file>" | CLI✅ MCP⚠️ |
| **扩展任务** | `task-master expand --id=1` | "Expand task 1" | CLI✅ MCP⚠️ |
| **复杂度分析** | `task-master analyze-complexity` | "Analyze complexity" | CLI✅ MCP⚠️ |
| **更新状态** | `task-master set-status --id=1 --status=done` | "Mark task 1 as done" | CLI✅ MCP⚠️ |

---

## 💡 MCP的优势

### 1. 自然语言交互
**CLI**:
```bash
task-master parse-prd .taskmaster/docs/test_prd_claude_code.txt --num-tasks=5
```

**MCP**:
```
"Can you parse my PRD and generate 5 tasks?"
```

### 2. 上下文感知
**CLI**: 需要明确指定文件路径

**MCP**: AI可以理解上下文
```
"Parse the test PRD we created earlier"
"Expand the authentication task"
```

### 3. IDE集成
- ✅ 在代码编辑器中直接使用
- ✅ 查看任务的同时编辑代码
- ✅ 无需切换到终端

### 4. 组合操作
```
"Parse my PRD, analyze complexity, and expand all high-complexity tasks"
```

相当于：
```bash
task-master parse-prd docs/prd.txt
task-master analyze-complexity
task-master expand --id=2
task-master expand --id=5
```

---

## ⚠️ 为什么MCP需要单独测试？

### 1. 不同的认证机制
- **CLI**: 直接读取`.taskmaster/config.json`
- **MCP**: 通过MCP环境变量或使用项目配置

### 2. 不同的执行环境
- **CLI**: Node.js进程直接运行
- **MCP**: 通过stdio协议与IDE通信

### 3. 不同的配置优先级
可能的配置冲突：
```
.mcp.json环境变量
    vs
.taskmaster/config.json provider配置
```

### 4. 工具加载机制
- **CLI**: 所有功能都可用
- **MCP**: 受`TASK_MASTER_TOOLS`限制

---

## 🧪 MCP验证清单

### 配置验证
- [x] `.mcp.json`存在且格式正确
- [x] `TASK_MASTER_TOOLS`设置为`standard`
- [x] `.taskmaster/config.json`使用`claude-code` provider
- [ ] IDE已重启（用户需要执行）
- [ ] MCP服务器已加载（用户需要验证）

### 功能验证
- [ ] MCP工具列表可见
- [ ] `get_tasks`工具可用
- [ ] `parse_prd`工具可用（AI功能）
- [ ] `expand_task`工具可用（AI功能）
- [ ] `analyze_project_complexity`工具可用（AI功能）

### Claude Code集成验证
- [ ] MCP调用使用Claude Code provider
- [ ] Token使用统计显示$0.00
- [ ] 输出质量与CLI一致

---

## 📊 预期MCP测试结果

### 成功标志
```
✅ MCP工具列表显示15个工具
✅ AI功能正常工作（parse_prd, expand_task等）
✅ 使用Claude Code provider（免费）
✅ 输出质量与CLI一致
✅ 自然语言交互顺畅
```

### 可能的问题

#### 问题1: MCP服务器未加载
**症状**: IDE显示"0 tools enabled"或找不到task-master-ai

**解决**:
1. 检查`.mcp.json`语法
2. 重启IDE
3. 检查MCP服务器日志

#### 问题2: AI功能不工作
**症状**: parse_prd等命令失败

**可能原因**:
- MCP环境变量覆盖了`.taskmaster/config.json`
- Claude Code CLI未正确配置

**解决**: 
确保MCP环境变量不包含API密钥配置，让其使用`.taskmaster/config.json`

#### 问题3: Token费用产生
**症状**: Est. Cost不为$0.00

**原因**: MCP可能使用了API密钥而非Claude Code

**解决**: 检查MCP环境变量，移除所有API密钥

---

## 🎯 下一步：用户测试MCP

### 立即可做

**1. 重启IDE**
```bash
# 完全退出并重新启动Claude Code或IDE
```

**2. 在聊天中测试**
```
"What taskmaster tools are available?"
"List all my tasks"
"What's the next task?"
```

**3. 测试AI功能**
```
"Parse my PRD at .taskmaster/docs/test_prd_claude_code.txt"
"Expand task 2"
```

**4. 验证使用Claude Code**
```
检查输出中是否显示:
- Provider: claude-code
- Est. Cost: $0.000000
```

---

## 📝 测试记录模板

### MCP测试日期: ___________

#### 1. MCP服务器加载
- [ ] 工具数量: ____个
- [ ] 包含parse_prd工具
- [ ] 包含expand_task工具

#### 2. 基础功能测试
- [ ] get_tasks: _____ (成功/失败)
- [ ] next_task: _____ (成功/失败)
- [ ] get_task: _____ (成功/失败)

#### 3. AI功能测试
- [ ] parse_prd: _____ (成功/失败)
  - Provider: _____
  - Cost: $_____
  
- [ ] expand_task: _____ (成功/失败)
  - Provider: _____
  - Cost: $_____
  
- [ ] analyze_complexity: _____ (成功/失败)
  - Provider: _____
  - Cost: $_____

#### 4. 输出质量
- [ ] 中文输出正常
- [ ] 代码示例完整
- [ ] 依赖关系准确

#### 5. 问题记录
- 问题描述: _____________________________
- 解决方法: _____________________________

---

## 🔗 相关文档

- **CLI测试报告**: `CLAUDE_CODE_INTEGRATION_TEST.md`
- **配置指南**: `API_CONFIGURATION_GUIDE.md`
- **快速参考**: `CONFIG_QUICK_REFERENCE.md`
- **MCP官方文档**: https://docs.task-master.dev/capabilities/mcp

---

## 💬 总结

### 当前状态
- ✅ CLI功能：100%测试完成
- ⚠️ MCP功能：配置完成，等待用户测试

### 为什么需要用户测试MCP？
1. **需要IDE重启** - 我无法重启用户的IDE
2. **需要交互验证** - MCP在聊天界面中使用
3. **环境差异** - MCP配置可能因IDE而异

### 建议
**重启Claude Code，然后在聊天中尝试**:
```
"List all tasks in taskmaster"
"Parse my PRD at .taskmaster/docs/test_prd_claude_code.txt"
```

如果成功，你将拥有：
- ✅ 免费的AI任务管理
- ✅ CLI + MCP双模式
- ✅ 自然语言交互
- ✅ IDE无缝集成

**让我们一起验证MCP功能！** 🚀
