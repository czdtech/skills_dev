# Taskmaster 快速参考卡

## ✅ 当前可用功能（无需配置）

### 基础任务管理
```bash
# 列出任务
task-master list
task-master list --status pending

# 查看下一个任务
task-master next

# 查看任务详情
task-master show <id>

# 更新任务状态
task-master set-status --id=<id> --status=<status>
# 状态值: pending | in-progress | done | deferred | cancelled | blocked | review
```

### 依赖管理
```bash
# 添加依赖
task-master add-dependency --id=<id> --depends-on=<parent-id>

# 删除依赖
task-master remove-dependency --id=<id> --depends-on=<parent-id>

# 验证依赖
task-master validate-dependencies

# 自动修复
task-master fix-dependencies
```

### 标签管理
```bash
# 列出标签
task-master tags

# 创建标签
task-master add-tag <name> -d="描述"

# 切换标签
task-master use-tag <name>

# 删除标签
task-master delete-tag <name>
```

### 子任务管理
```bash
# 手动添加子任务
task-master add-subtask --parent=<id> --title="标题" --description="描述"

# 删除子任务
task-master remove-subtask --id=<parentId>.<subtaskId>

# 清空子任务
task-master clear-subtasks --id=<id>
```

---

## ⚠️ 需要API配置的功能

### 配置步骤
```bash
# 1. 创建.env文件
echo "ANTHROPIC_API_KEY=sk-ant-your-key-here" > .env

# 2. 或更新.mcp.json中的env配置
```

### AI驱动功能
```bash
# PRD解析
task-master parse-prd <file.md> --num-tasks=20

# 智能创建任务
task-master add-task --prompt="实现用户登录功能"

# 任务扩展（生成子任务）
task-master expand --id=<id> --research

# 复杂度分析
task-master analyze-complexity --threshold=7
task-master complexity-report
```

### Autopilot TDD
```bash
# 启动TDD工作流
task-master autopilot start <task-id>

# 查看状态
task-master autopilot status

# 恢复会话
task-master autopilot resume
```

---

## 📋 任务JSON格式

```json
{
  "id": "1",
  "title": "任务标题",
  "description": "任务描述",
  "status": "pending",
  "priority": "high",
  "tag": "master",
  "dependencies": [],
  "details": "详细信息（可选）",
  "testStrategy": "测试策略（可选）",
  "subtasks": [
    {
      "id": "1.1",
      "title": "子任务标题",
      "description": "子任务描述",
      "status": "pending",
      "priority": "high",
      "dependencies": [],
      "estimatedTime": "60分钟"
    }
  ]
}
```

---

## 🎯 使用场景推荐

### 场景1: 小项目（< 20任务）
✅ 手动管理tasks.json  
✅ 使用task-master list和next  
❌ 无需配置API

### 场景2: 中型项目（20-50任务）
✅ 配置API密钥  
✅ 使用parse-prd自动生成  
✅ 使用expand拆分复杂任务

### 场景3: 大型项目（50+任务）
✅ 完整配置MCP  
✅ 使用标签管理多模块  
✅ 使用复杂度分析识别风险

### 场景4: TDD开发
✅ 配置测试框架  
✅ 使用Autopilot模式  
✅ 自动化Git提交

---

## 📊 评分概览

| 功能 | 评分 |
|------|------|
| 易用性 | ⭐⭐⭐⭐☆ |
| 功能完整性 | ⭐⭐⭐⭐⭐ |
| 灵活性 | ⭐⭐⭐⭐⭐ |
| 稳定性 | ⭐⭐⭐⭐☆ |
| 文档质量 | ⭐⭐⭐⭐⭐ |

**总评**: 4.4/5 ⭐

---

## 🔗 快速链接

- **详细报告**: `.taskmaster/reports/TASKMASTER_CAPABILITY_TEST_SUMMARY.md`
- **配置文件**: `.taskmaster/config.json`
- **任务数据**: `.taskmaster/tasks/tasks.json`
- **工作流集成**: `.claude/CLAUDE.md` (行105-209)
- **官方仓库**: https://github.com/eyaltoledano/claude-task-master
