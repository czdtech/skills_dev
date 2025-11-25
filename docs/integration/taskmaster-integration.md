# Taskmaster 完整集成指南

> **核心理念**: 融入而非侵入,增强而非替代  
> **最后更新**: 2025-11-24  
> **来源**: 合并 TASKMASTER_COMPLETE_ANALYSIS + TASKMASTER_INTEGRATION_ANALYSIS + WORKFLOW_GLOBAL_INTEGRATION_STRATEGY

---

## 🎯 Taskmaster是什么?

官方定位: "A task management system for AI-driven development"

**三种使用方式**:
1. **MCP Server** - 与AI对话集成
2. **CLI 工具** - 命令行批量处理
3. **Autopilot** - 自动化TDD工作流

---

## 📊 三层集成模式

### 层1: MCP状态记录(贯穿全流程)

**作用**: 跨所有阶段的可选状态追踪

**使用方式**:
- 用户在对话中主动查询/更新
- Claude Code在关键节点**询问**是否记录

**MCP工具**(40+):
- `add_task`, `update_task`, `remove_task`
- `get_tasks`, `next_task`, `set_task_status`
- `add_subtask`, `expand_task`
- `parse_prd`, `analyze_project_complexity`
- `add_dependency`, `validate_dependencies`

**集成点**:
- 阶段1: 询问是否创建顶层任务
- 阶段4: 询问是否更新任务详情
- 阶段6: 询问是否更新状态
- 阶段7: 询问是否完成任务

**原则**: 完全用户主导,Claude Code只询问不强制

---

### 层2: CLI批量处理(阶段5辅助)

**作用**: 辅助任务拆分和分析

**核心命令**(20+):
```bash
# PRD解析
task-master parse-prd prd.txt --num-tasks=20

# 任务扩展
task-master expand --id=5 --num=3
task-master expand --all --research

# 复杂度分析
task-master analyze-complexity --threshold=7
task-master complexity-report

# 批量状态更新
task-master set-status --id=1,2,3 --status=done

# 依赖管理
task-master add-dependency --id=3 --depends-on=1
task-master validate-dependencies
```

**触发条件**:
- 有详细PRD文档
- 任务预计>20个
- 复杂度较高

**无需AI的基础功能**:
- ✅ 任务列表和查询(list/next/show)
- ✅ 状态手动更新(set-status)
- ✅ 依赖关系管理
- ✅ 标签系统
- ✅ 子任务添加

**需要AI的高级功能**:
- ❌ PRD解析(parse-prd)
- ❌ 智能任务创建(add-task)
- ❌ 任务自动扩展(expand)
- ❌ 复杂度分析(analyze-complexity)

---

### 层3: Autopilot TDD(阶段6可选模式)

**作用**: 提供严格的TDD执行路径

**工作流程**:
```
1. 启动: task-master autopilot start <task-id>
2. RED Phase: AI编写失败的测试
3. GREEN Phase: AI实现代码让测试通过
4. COMMIT Phase: Taskmaster自动创建commit
5. 重复: 直到所有子任务完成
```

**职责分工**:

| 角色 | 职责 |
|------|------|
| **Claude Code (AI Agent)** | 编写测试、实现代码、运行测试、报告结果 |
| **Taskmaster (工作流引擎)** | 管理状态机、验证测试结果、自动commit、跟踪进度 |

**前置条件**(同时满足):
1. 用户明确要求使用TDD
2. 项目已配置测试框架
3. Git仓库干净(无未提交更改)
4. API密钥已配置(或使用Claude Code provider)

**MCP工具**:
- `autopilot_start` - 启动工作流
- `autopilot_resume` - 恢复中断的工作流
- `autopilot_next` - 进入下一个子任务
- `autopilot_status` - 查看当前状态
- `autopilot_complete_phase` - 完成当前阶段
- `autopilot_commit` - 创建commit
- `autopilot_abort` - 中止工作流

**与Droid的关系**: 互斥但可选

---

## 🔧 配置方法

### 方法1: 使用Claude Code(推荐,无需API密钥)

```bash
# 1. 确保Claude Code已认证
claude --version

# 2. 配置.taskmaster/config.json
cat > .taskmaster/config.json << 'EOF'
{
  "models": {
    "main": {
      "provider": "claude-code",
      "modelId": "sonnet",
      "maxTokens": 64000
    },
    "research": {
      "provider": "claude-code",
      "modelId": "opus"
    }
  }
}
EOF

# 3. 测试
task-master parse-prd docs/prd.txt --num-tasks=10
```

---

### 方法2: 使用Anthropic API

```bash
# 1. 创建.env文件
echo "ANTHROPIC_API_KEY=sk-ant-xxx" > .env
echo "PERPLEXITY_API_KEY=pplx-xxx" >> .env  # 可选

# 2. 测试
task-master parse-prd docs/prd.txt
```

---

### 方法3: MCP集成(IDE使用)

```json
// ~/.cursor/mcp.json 或 ~/.codeium/windsurf/mcp_config.json
{
  "mcpServers": {
    "task-master-ai": {
      "command": "npx",
      "args": ["-y", "task-master-ai"],
      "env": {
        "TASK_MASTER_TOOLS": "standard",  // all/standard/core/lean
        "ANTHROPIC_API_KEY": "sk-ant-xxx"
      }
    }
  }
}
```

**重要**: 配置后需重启IDE

---

## 📋 使用场景

### 小型项目(<20任务)

```bash
# 直接使用CLI手动管理,无需API密钥
task-master list
task-master next
task-master set-status --id=1 --status=done
```

---

### 中型项目(20-50任务)

```bash
# 配置API密钥,使用AI辅助
task-master parse-prd requirements.md --num-tasks=30
task-master expand --id=1 --research
task-master analyze-complexity --threshold=7
```

---

### 大型项目(50+任务)

- ✅ 完整配置MCP
- ✅ 标签系统管理多模块
- ✅ 复杂度分析识别风险任务
- ✅ 跨会话追踪

---

### 核心功能开发(TDD)

```bash
# 使用Autopilot TDD
task-master autopilot start 7
# 自动TDD循环: RED → GREEN → COMMIT
```

---

## 🎯 集成到CLAUDE.md工作流

### 阶段1: 接单与现实检验

```bash
if [ -d ".taskmaster" ]; then
  询问: "检测到Taskmaster,是否创建顶层任务?(y/n)"
fi
```

---

### 阶段5: 任务拆分

**选项1**: 手动拆分(默认)  
**选项2**: Taskmaster CLI辅助(大型项目)

```bash
task-master parse-prd docs/prd.txt --num-tasks=20
task-master expand --all --research
```

---

### 阶段6: 执行

**模式A**: Droid标准执行(默认)  
**模式B**: Taskmaster Autopilot TDD(可选)

决策逻辑:
```
用户明确要求TDD?
  ├─ 是 → Autopilot模式
  └─ 否 → Droid模式
```

---

## 💡 最佳实践

### 推荐模式选择

| 场景 | 推荐模式 | 理由 |
|------|---------|------|
| 日常任务查询 | MCP对话 | 灵活互动 |
| 批量任务处理 | CLI脚本 | 自动化 |
| 严格TDD开发 | Autopilot | 质量保证 |
| 探索性开发 | Droid | 快速迭代 |

---

### 注意事项

1. ✅ **用户主导**: 所有Taskmaster功能都是**询问**后使用
2. ✅ **可选非强制**: 不强制使用,保持工作流灵活性
3. ✅ **Fallback机制**: Taskmaster不可用时使用Markdown记录
4. ✅ **明确标记**: 如使用Fallback,标记`[TASKMASTER_FALLBACK]`

---

## 🔍 与Droid的对比

| 维度 | Droid | Autopilot |
|------|-------|-----------|
| 速度 | 快 | 中等(严格流程) |
| 灵活性 | 高 | 低(强制TDD) |
| 质量保证 | 依赖验收 | 强制测试 |
| Git管理 | 手动 | 自动 |
| 适用场景 | 通用 | 核心功能/TDD |

---

## 📊 功能可用性矩阵

| 功能类别 | 无API | 有API | MCP | Autopilot |
|---------|-------|-------|-----|-----------|
| list/show/next |✅ | ✅ | ✅ | ✅ |
| set-status | ✅ | ✅ | ✅ | ✅ |
| expand(AI) | ❌ | ✅ | ✅ | ✅ |
| parse-prd | ❌ | ✅ | ✅ | ✅ |
| analyze-complexity | ❌ | ✅ | ✅ | ✅ |
| autopilot | ❌ | ❌ | ⚠️ | ✅ |

---

## 🎉 总结

**Taskmaster评分**: ⭐⭐⭐⭐☆ (4/5)

**优势**:
1. ✅ 渐进式设计(从简单到复杂)
2. ✅ CLI稳定性(基础功能无需配置)
3. ✅ 三层集成(灵活选择)
4. ✅ 文档完善

**限制**:
1. ⚠️ AI依赖(高级功能需要API)
2. ⚠️ MCP配置(需要重启IDE)
3. ⚠️ 学习曲线(Autopilot需要理解TDD)

**推荐**: 使用混合模式——用户主导+智能辅助 ✅

---

**相关文档**:
- [多角色协作工作流](../architecture/multi-agent-workflow.md)
- [Taskmaster能力测试](../reports/taskmaster-tests.md)
- [API配置指南](../reports/configuration.md)
