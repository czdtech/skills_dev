# Claude Skills 创建指南

基于官方 `skill-creator` 技能的完整指南和工具。

---

## 📚 文档导航

本项目已建立完整的文档系统,请访问 **[docs/](./docs/)** 目录:

### 🏗️ [架构设计](./docs/architecture/)
- **[多角色协作工作流](./docs/architecture/multi-agent-workflow.md)** - Claude Code + Codex + Droid + Taskmaster 完整架构
- **[Skills 实现架构](./docs/architecture/skills-implementation.md)** - Bridge 服务 vs 脚本式实现对比
- **[系统提示词演化](./docs/architecture/prompt-evolution.md)** - CLAUDE.md 的优化历程

### 🔌 [集成指南](./docs/integration/)
- **[Taskmaster 完整集成](./docs/integration/taskmaster-integration.md)** - MCP + CLI + Autopilot 三层集成
- **[Skills 生态依赖](./docs/integration/skills-ecosystem.md)** - skill-creator 依赖关系图

### 📊 [测试报告](./docs/reports/)
- **[Taskmaster 能力测试](./docs/reports/taskmaster-tests.md)** - 完整功能测试与评估
- **[API 配置指南](./docs/reports/configuration.md)** - Provider 配置完全指南
- **[MCP 集成指南](./docs/reports/mcp-integration.md)** - IDE MCP 配置详解

---

## 🗂 仓库结构一览

当前工作目录下包含 4 个与 Claude Skills 紧密相关的项目：

- `awesome-claude-skills/`：社区维护的 Awesome 列表，汇总官方与第三方技能、资源与示例。
- `claude-code/`：Claude 终端 / IDE 编码助手本体，包含若干官方插件示例。
- `claude-cookbooks/`：Claude API 官方 Cookbook，内含 Skills 专题示例与大量工具调用 / RAG / 多模态示例。
- `skills/`：Anthropic 官方 Skills 示例仓库，包含规范说明、模板技能、文档技能与 skill-creator 工具。

建议把本仓库视为一个 “Claude Skills 学习与实验工作区”：
- 在 `skills/` 中学习 Skill 规范与结构
- 在 `claude-cookbooks/` 中学习如何通过 API 使用 Skills
- 在 `claude-code/` 中把 Skills 融入日常开发工作流
- 借助 `awesome-claude-skills/` 浏览生态与优秀实践

### 🤖 Multi-Agent 系统

本仓库还包含两种形式的 Multi-Agent 实现：

#### Claude Code Skills（深度集成）
- **`codex-advisor-skill/`** - Codex 技术顾问 Skill，提供高级设计咨询
- **`droid-executor-skill/`** - Droid 执行代理 Skill，自动化编码任务

#### MCP 服务器（通用集成）
- **`codex-advisor-mcp/`** - Codex Advisor MCP 服务器，适用于任何 MCP 客户端
- **`droid-executor-mcp/`** - Droid Executor MCP 服务器，适用于任何 MCP 客户端

**选择建议**：
- 在 **Claude Code** 中：优先使用 **Skill** 版本（集成更深、有辅助脚本）
- 在 **Claude Desktop** 或其他客户端：使用 **MCP** 版本
- 查看 [Multi-Agent 架构对齐分析](./docs/multi-agent-architecture-alignment.md) 了解详细对比

**快速开始**：
```bash
# 安装 Codex Advisor MCP
cd codex-advisor-mcp && ./setup.sh

# 安装 Droid Executor MCP  
cd droid-executor-mcp && ./setup.sh
```

详见各项目的 README.md 和 [迁移指南](./docs/multi-agent-mcp-migration-guide.md)。

## 🚀 正确创建方式

### 强烈推荐：使用官方 skill-creator 技能

在Claude中启用 `skill-creator` 技能，然后告诉Claude：

```
我想创建一个[主题]的技能，用于[具体场景]。
用户会说："[具体请求示例]"
```

Claude会引导你完成完整的6步创建流程。

### 官方6步创建流程

1. **理解需求** - 收集具体使用示例
2. **规划内容** - 确定 scripts/references/assets
3. **初始化** - 使用官方脚本
4. **编辑** - 使用祈使语态编写
5. **打包** - 验证并打包
6. **迭代** - 持续改进

### 官方工具脚本

```bash
# 初始化技能
python skills/skill-creator/scripts/init_skill.py my-skill --path ./skills

# 验证结构
python skills/skill-creator/scripts/quick_validate.py ./skills/my-skill

# 打包技能
python skills/skill-creator/scripts/package_skill.py ./skills/my-skill ./dist
```

## 📁 技能结构

```
skill-name/
├── SKILL.md (必需)
│   ├── YAML frontmatter
│   │   ├── name: 标识符 (小写连字符)
│   │   └── description: 详细描述
│   └── Markdown 指令
└── Bundled Resources
    ├── scripts/ - 可执行代码
    ├── references/ - 参考文档
    └── assets/ - 输出资源
```

### 渐进式披露机制

1. **元数据** (~100词) - name + description 始终在上下文
2. **技能主体** (<5k词) - 技能被触发时加载
3. **资源文件** - 根据需要加载 (无限量)

## 💡 关键要点

### 命名规范
```yaml
# ✅ 正确
name: financial-analyzer
name: document-processor

# ❌ 错误
name: MySkill      # 大写
name: analyzer     # 太通用
```

### 描述指南
```yaml
# ✅ 好的描述
description: 用于分析财务数据，计算关键指标，生成图表。用户会说"分析这个财务报表"。

# ❌ 差的描述
description: 财务分析工具。
```

### 指令编写
```markdown
# ✅ 使用祈使语态
Load the data file
Process the data
Generate the report

# ❌ 避免第二人称
You should load the data...
```

### 资源分类

**scripts/** - 可执行代码
- 重复性任务
- 自动化操作
- 确定性逻辑

**references/** - 参考文档
- API文档
- 数据库模式
- 公司政策

**assets/** - 输出资源
- 模板文件
- 图片资源
- 样式文件

## 📦 部署技能

### Claude Code
```bash
/plugin add ./my-skill
```

### Claude API
```python
from anthropic import Anthropic
from anthropic.lib import files_from_dir

client = Anthropic(api_key="key", default_headers={
    "anthropic-beta": "skills-2025-10-02"
})

skill = client.beta.skills.create(
    display_title="My Skill",
    files=files_from_dir("./my-skill")
)
```

## 🔧 工具和示例

### 辅助工具
- **skill_creator_tool.py** - 辅助工具 (仅作参考)
- **example-skill/** - 完整示例技能
- **test-official/** - 官方脚本生成的示例

### 官方工具位置
- `skills/skill-creator/scripts/init_skill.py` - 初始化
- `skills/skill-creator/scripts/quick_validate.py` - 验证
- `skills/skill-creator/scripts/package_skill.py` - 打包

## 📚 子项目详细说明

### `skills/`（官方 Skills 示例与规范）

- 包含 `agent_skills_spec.md`：Agent Skills 规范文档，定义 `SKILL.md` 的 frontmatter、目录结构和命名规则。
- 提供大量示例技能：如 `algorithmic-art/`、`brand-guidelines/`、`webapp-testing/` 等，适合作为写 Skill 的参考模板。
- `document-skills/` 目录中包含 docx / pdf / pptx / xlsx 等文档技能的实现，是复杂二进制文档处理的示例。
- `skill-creator/` 提供 Skill 创建向导技能以及本 README 中引用的官方脚本：
  - `scripts/init_skill.py`：初始化新技能目录
  - `scripts/quick_validate.py`：快速校验技能结构
  - `scripts/package_skill.py`：打包技能用于分发
- `template-skill/` 提供最小可用 Skill 模板，适合复制后按需修改。

### `claude-cookbooks/`（API 与 Skills Cookbook）

- 顶层包含 `capabilities/`、`tool_use/`、`multimodal/` 等多种能力示例。
- `skills/` 子目录是 “Claude Skills Cookbook”，通过 Jupyter Notebook 展示：
  - 如何用 Skills 生成 Excel / PowerPoint / PDF 等文件
  - 金融分析、报表生成等业务场景示例
  - 如何通过 API 配置 Skills 所需的 beta headers 与 Files API
- `skills/custom_skills/` 中包含财务分析等自定义技能示例，可对照 `skills/` 仓库中的 SKILL 结构来理解实际落地方式。

### `claude-code/`（Claude 终端编码助手）

- `README.md` 说明如何安装并在终端中使用 `claude` 命令。
- `plugins/` 目录包含多个官方插件，用于展示如何扩展 Claude Code：
  - `agent-sdk-dev/`：辅助开发 Claude Agent SDK 应用
  - `commit-commands/`：封装常用 git 提交 / 推送 / PR 流程
  - `code-review/`：多 Agent 协作的自动化代码审查
  - `feature-dev/`：结构化的特性开发工作流
- 可将 `skills/` 仓库作为 Claude Code 的插件 marketplace，从而在本地开发环境中直接调用 Skills。

### `awesome-claude-skills/`（社区 Skills 导航）

- 这是一个 Awesome 风格的社区项目，整理了大量官方与第三方技能仓库。
- 按类别列出：文档处理、设计创意、开发/调试工具、企业沟通、多模态等。
- 适合作为 “灵感库”，在掌握基础规范后浏览他人的 Skill 设计方式和工程实践。

## 🔗 官方 Skills 资料收藏

> 以下链接均为 Anthropic 官方关于 Skills 的核心资料，推荐在深入设计和实现技能前通读一遍。

- Skills 官方文档（Agent Skills 总览与规范）：
  - https://docs.claude.com/en/docs/agents-and-tools/agent-skills
- Skills API 快速上手（如何通过 API 创建与管理 Skills）：
  - https://docs.claude.com/en/api/skills-guide#creating-a-skill
- 工程博客：Equipping agents for the real world with Agent Skills
  - https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
- 产品发布：Claude Skills 功能介绍与应用案例
  - https://www.anthropic.com/news/skills

## 🔰 推荐学习路径

如果你希望系统掌握 Claude Skills，可以按以下顺序使用本工作区：

1. **理解规范与结构**：
   - 阅读根目录本 README 与 `skills/agent_skills_spec.md`
   - 浏览 `skills/template-skill/` 了解最小 Skill 结构
2. **学习官方示例**：
   - 挑选 1–2 个技能（如 `skills/algorithmic-art/`、`skills/document-skills/xlsx/`）
   - 重点关注它们的 `SKILL.md` 如何组织章节、指令和示例
3. **动手创建自己的技能**：
   - 使用 `skills/skill-creator/scripts/init_skill.py` 在 `skills/` 目录下初始化新技能
   - 按本 README 的规范完善 `SKILL.md` 与相关资源
   - 使用 `quick_validate.py` 和 `package_skill.py` 进行验证与打包
4. **通过 API 练习调用 Skills**：
   - 进入 `claude-cookbooks/skills/`，按 README 配好环境
   - 跑通 Notebook（从 `01_skills_introduction.ipynb` 开始），理解 Skills 在 API 侧的使用方式
5. **融入开发工作流**：
   - 安装 Claude Code（见 `claude-code/README.md`）
   - 将 `skills/` 仓库注册为插件 marketplace，在终端中直接调用你的技能
6. **借助社区拓展思路**：
   - 浏览 `awesome-claude-skills/README.md` 中的各类 Skill 链接
   - 对比不同项目的 `SKILL.md` 与目录结构，吸收优秀写法与模式

## ✅ 最佳实践

1. **优先使用官方方法** - skill-creator 是最权威的工具
2. **遵循官方流程** - 6步创建流程经过验证
3. **使用官方脚本** - 验证和打包工具
4. **关注渐进式披露** - 优化token使用
5. **持续迭代** - 测试和改进

## 📖 示例

### 创建数据分析技能

#### 交互式方式 (推荐)
```
我想创建一个数据分析技能，用于分析CSV、Excel文件。
用户会说："分析这个销售数据"、"生成财务图表"
```

#### 手动方式
```bash
python skills/skill-creator/scripts/init_skill.py data-analyzer --path ./skills

# 编辑 skills/data-analyzer/SKILL.md

# 验证
python skills/skill-creator/scripts/quick_validate.py ./skills/data-analyzer

# 打包
python skills/skill-creator/scripts/package_skill.py ./skills/data-analyzer ./dist
```

## 🎯 结论

创建Claude Skills的最佳方法是：
1. 使用官方的 skill-creator 技能
2. 遵循官方的6步流程
3. 利用官方工具脚本
4. 持续测试和迭代

记住：**官方工具和方法永远是最权威和可靠的！**
