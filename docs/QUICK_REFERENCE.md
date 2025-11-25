# 📋 文档系统快速参考

> **快速查找常用文档和维护命令**  
> **最后更新**: 2025-11-24

---

## 🎯 常用文档快速入口

### 了解架构
```bash
# 完整的多角色协作工作流
cat docs/architecture/multi-agent-workflow.md

# Skills实现对比(Bridge vs 脚本)
cat docs/architecture/skills-implementation.md

# 系统提示词演化历程
cat docs/architecture/prompt-evolution.md
```

### 配置集成
```bash
# Taskmaster三层集成指南
cat docs/integration/taskmaster-integration.md

# API配置完全指南
cat docs/reports/configuration.md

# MCP集成指南(各IDE)
cat docs/reports/mcp-integration.md
```

### 测试报告
```bash
# Taskmaster能力测试
cat docs/reports/taskmaster-tests.md
```

---

## 🛠️ 维护命令

### 日常检查
```bash
# 运行完整检查
./scripts/check-docs.sh

# 查看文档结构
tree docs/ -L 2

# 统计文档数量
find docs/ -name '*.md' | wc -l
```

### 查找文档
```bash
# 搜索包含特定内容的文档
grep -r "Taskmaster" docs/**/*.md

# 列出所有架构文档
ls docs/architecture/

# 查看最近修改的文档
find docs/ -name '*.md' -mtime -7
```

### 验证链接
```bash
# 检查缺少元数据的文档
grep -L "最后更新" docs/**/*.md

# 列出所有Markdown文件
find docs/ -name '*.md' -type f
```

---

## 📂 目录结构

```
docs/
├── README.md                          # 📚 主导航
├── MAINTENANCE_GUIDE.md               # 🔧 维护指南
├── REORGANIZATION_SUMMARY.md          # 📊 整理总结
│
├── architecture/                      # 🏗️ 架构设计
│   ├── multi-agent-workflow.md
│   ├── skills-implementation.md
│   └── prompt-evolution.md
│
├── integration/                       # 🔌 集成指南
│   ├── taskmaster-integration.md
│   └── skills-ecosystem.md
│
└── reports/                           # 📊 测试报告
    ├── taskmaster-tests.md
    ├── configuration.md
    └── mcp-integration.md
```

---

## 🔍 常见任务

### 新增文档
```bash
# 1. 确定分类并创建文档
vi docs/integration/new-guide.md

# 2. 添加元数据
cat > docs/integration/new-guide.md << 'EOF'
# 新指南标题

> **类型**: 集成指南  
> **最后更新**: $(date +%Y-%m-%d)  
> **来源**: 新创建

---
[内容]
EOF

# 3. 更新导航
echo "- **[新指南](./integration/new-guide.md)** - 描述" >> docs/README.md

# 4. 运行检查
./scripts/check-docs.sh
```

### 更新文档
```bash
# 1. 编辑文档
vi docs/architecture/multi-agent-workflow.md

# 2. 更新元数据中的日期
# > **最后更新**: 2025-11-24

# 3. 提交更改
git add docs/architecture/multi-agent-workflow.md
git commit -m "docs: 更新多角色工作流(添加XXX)"
```

### 归档文档
```bash
# 1. 移到归档
mv docs/reports/old-report.md .archive/reports/

# 2. 记录归档
echo "### $(date +%Y-%m-%d)" >> .archive/README.md
echo "- old-report.md → 替换为 new-report.md" >> .archive/README.md

# 3. 更新导航
# 从 docs/README.md 中移除对应链接
```

---

## ⚡ 快捷别名

添加到 `~/.bashrc` 或 `~/.zshrc`:

```bash
# 文档相关别名
alias docs='cd /home/jiang/work/for_claude/skills_dev/docs'
alias doccheck='cd /home/jiang/work/for_claude/skills_dev && ./scripts/check-docs.sh'
alias doctree='tree /home/jiang/work/for_claude/skills_dev/docs -L 2'
alias docnav='cat /home/jiang/work/for_claude/skills_dev/docs/README.md'
```

使用:
```bash
docs       # 快速进入文档目录
doccheck   # 运行文档检查
doctree    # 查看文档结构
docnav     # 查看导航
```

---

## 📱 移动端访问

如果使用GitHub/GitLab托管:

```
# 主导航
https://github.com/[用户名]/[仓库]/tree/main/docs

# 直接访问文档
https://github.com/[用户名]/[仓库]/blob/main/docs/architecture/multi-agent-workflow.md
```

---

## 🎯 记忆要点

| 要查... | 看这里 |
|---------|--------|
| 🏗️ 架构设计 | `docs/architecture/` |
| 🔌 集成方法 | `docs/integration/` |
| 📊 测试结果 | `docs/reports/` |
| 🔧 如何维护 | `docs/MAINTENANCE_GUIDE.md` |
| 📚 完整导航 | `docs/README.md` |

---

## 📅 维护时间表

- **每次更新**: 检查元数据、导航
- **每周**: 运行 `./scripts/check-docs.sh`
- **每月**: 审查内容准确性
- **每季度**: 清理超过90天的归档

---

## 🆘 需要帮助?

```bash
# 查看维护指南
cat docs/MAINTENANCE_GUIDE.md

# 查看整理总结
cat docs/REORGANIZATION_SUMMARY.md

# 查看主导航
cat docs/README.md
```

---

**提示**: 将此文件加入书签,方便快速查找! 📌
