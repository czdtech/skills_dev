# 归档文档说明

> **归档日期**: 2025-11-24  
> **原因**: 文档整理与重构,合并重复内容

---

## 📁 归档内容

### old-docs/ - 根目录旧文档

这些文档已被合并到新的`docs/`结构中:

| 旧文档 | 合并到 |
|--------|--------|
| `ARCHITECTURE_COMPARISON.md` | `docs/architecture/skills-implementation.md` |
| `SKILLS_COMPARISON.md` | `docs/architecture/skills-implementation.md` |
| `PROMPT_COMPARISON.md` | `docs/architecture/prompt-evolution.md` |
| `CLAUDE_OPTIMIZATION_SUMMARY.md` | `docs/architecture/prompt-evolution.md` |
| `CLAUDE_RESTRUCTURE_SUMMARY.md` | `docs/architecture/prompt-evolution.md` |
| `TASKMASTER_COMPLETE_ANALYSIS.md` | `docs/integration/taskmaster-integration.md` |
| `TASKMASTER_INTEGRATION_ANALYSIS.md` | `docs/integration/taskmaster-integration.md` |
| `WORKFLOW_GLOBAL_INTEGRATION_STRATEGY.md` | `docs/architecture/multi-agent-workflow.md` |

**删除的文件**:
- `test_prd.md` - 测试文件,无需保留

---

### taskmaster-reports/ - Taskmaster报告归档

这些报告已被合并到新的文档中:

| 旧报告 | 合并到 |
|--------|--------|
| `API_CONFIGURATION_GUIDE.md` | `docs/reports/configuration.md` |
| `TASKMASTER_CAPABILITY_TEST_SUMMARY.md` | `docs/reports/taskmaster-tests.md` |
| `MCP相关文档` | `docs/reports/mcp-integration.md` |

**保留在`.taskmaster/reports/`**:
- `CONFIG_QUICK_REFERENCE.md` - 配置快速参考
- `QUICK_REFERENCE.md` - 命令快速参考
- `task-complexity-report.json` - 复杂度分析报告

---

## 📚 新文档结构

请参考根目录的`docs/README.md`查看完整的文档导航。

**核心改进**:
1. ✅ 清晰的三层结构(架构/集成/报告)
2. ✅ 合并重复内容,避免冗余
3. ✅ 统一的导航入口
4. ✅ 保留所有重要信息

---

## 🔍 如何查找信息

### 旧 → 新文档映射

**查找架构设计**:
- 旧: `ARCHITECTURE_COMPARISON.md`, `WORKFLOW_GLOBAL_INTEGRATION_STRATEGY.md`
- 新: `docs/architecture/multi-agent-workflow.md`

**查找Skills实现**:
- 旧: `ARCHITECTURE_COMPARISON.md`, `SKILLS_COMPARISON.md`
- 新: `docs/architecture/skills-implementation.md`

**查找提示词演化**:
- 旧: `PROMPT_COMPARISON.md`, `CLAUDE_*_SUMMARY.md`
- 新: `docs/architecture/prompt-evolution.md`

**查找Taskmaster集成**:
- 旧: `TASKMASTER_*_ANALYSIS.md`
- 新: `docs/integration/taskmaster-integration.md`

**查找测试报告**:
- 旧: `.taskmaster/reports/TASKMASTER_CAPABILITY_TEST_SUMMARY.md`
- 新: `docs/reports/taskmaster-tests.md`

**查找配置指南**:
- 旧: `.taskmaster/reports/API_CONFIGURATION_GUIDE.md`
- 新: `docs/reports/configuration.md`

---

## ⏰ 保留期限

归档文档将保留**3个月** (至2026-02-24),之后可安全删除。

如有需要恢复,请在此日期前联系维护者。

---

## 🗑️ 安全删除

3个月后,可使用以下命令删除归档:

```bash
rm -rf .archive/
```

---

**整理者**: Multi-Agent Development Team  
**日期**: 2025-11-24
