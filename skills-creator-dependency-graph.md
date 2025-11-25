# Skills Creator 相关项目依赖关系图

> 目标：一眼看懂当前工作区中围绕 **skills/skill-creator** 的几个项目是如何配合使用的。

## 1️⃣ 角色说明

- **A. skills/skill-creator**  
  官方 Skill Creator 技能本体（对话式创建指南 + 本地脚本）：
  - `SKILL.md`：在 Claude 中启用 `skill-creator` 时加载的技能说明与流程
  - `scripts/init_skill.py`：初始化技能目录骨架
  - `scripts/quick_validate.py`：校验技能结构是否符合规范
  - `scripts/package_skill.py`：打包技能用于分发

- **B. skills/**  
  官方 Skills 示例与规范总仓：
  - 包含 `agent_skills_spec.md`（Agent Skills 规范）
  - 包含大量示例技能（如 `algorithmic-art/`、`document-skills/` 等）
  - **skill-creator 就是其中一个子技能目录：`skills/skill-creator/`**

- **C. claude-cookbooks/**  
  Claude API 官方 Cookbook：
  - 在 `skills/` 子目录中演示如何通过 **API 使用 Skills**（含文件生成、金融应用等）
  - 可以使用由 `skill-creator` 创建/打包好的技能目录，上传到 API 中使用

- **D. claude-code/**  
  Claude 终端 / IDE 编码助手：
  - 能安装 `anthropics/skills` 仓库作为插件 marketplace
  - 在 Claude Code 环境中，用户可以直接说「帮我创建一个技能」，触发 `skill-creator` 技能
  - 创建好的技能可以被 Claude Code 直接加载使用

- **E. awesome-claude-skills/**  
  社区维护的 Awesome 列表：
  - 收录官方 `skills/` 仓库以及社区技能
  - 为使用 `skill-creator` 创建新技能提供灵感和参考示例

- **F. 当前根目录 README.md**  
  本地中文创建指南：
  - 直接调用 `skills/skill-creator/scripts/*.py` 完成本地初始化 / 校验 / 打包
  - 作为你个人的操作手册，整合了上述所有项目的信息

## 2️⃣ 依赖关系概览

用依赖方向来读：**X ➜ Y 表示 X 依赖/使用 Y**。

```text
        awesome-claude-skills
                  │
                  ▼
              skills/ （B）
                  │
                  ▼
       skills/skill-creator （A）
          ▲            ▲      ▲
          │            │      │
          │            │      │
   当前 README （F）   │      │
                       │      │
          claude-cookbooks （C）
                       │
                       │
                 claude-code （D）
```

用文字解释上图：

1. **`skills/skill-creator`（A） 是整个体系的“创建核心”**：
   - 它作为一个 Skill，收录在官方 `skills/` 仓库（B）里。
   - 你本地的 `README.md`（F）直接调用它的脚本来创建 / 校验 / 打包技能。
   - Claude Code（D）和 Claude API Cookbook（C）都可以使用由它生成的技能目录。

2. **`skills/`（B） 是规范与示例的“基座”**：
   - 其中的 `agent_skills_spec.md` 定义 Skill 的结构规范。
   - `skill-creator` 本身就是 `skills/` 下的一个示例技能。
   - 其他示例技能（如 `document-skills/`）也都遵循同一套规范，因此可用同样的方式初始化/打包。

3. **`claude-cookbooks/`（C） 负责展示“如何在 API 中用 Skills”**：
   - Notebook 中展示如何通过 API 加载 Skills、生成文件、下载文件。
   - 这些 Skills 可以是官方示例，也可以是你用 `skill-creator` 生成并打包的自定义技能。

4. **`claude-code/`（D） 让 Skills 进入日常开发工作流**：
   - 可以安装 `anthropics/skills` 作为插件 marketplace，在终端直接使用 `skill-creator`。
   - 也能加载你本地打包好的技能，配合插件与 Agent SDK 实现完整工作流。

5. **`awesome-claude-skills/`（E） 提供生态视角与灵感来源**：
   - 它指向官方 `skills/` 仓库，以及大量社区技能仓库。
   - 当你用 `skill-creator` 设计新技能时，可以从这里挑选模式与最佳实践参考。

6. **根目录 `README.md`（F） 把所有东西串成一条学习与实战路径**：
   - 把 `skill-creator` 的官方脚本作为入口工具。
   - 帮你规划：先学 `skills/` 规范 → 用脚本创建技能 → 在 `claude-cookbooks/` 中通过 API 调用 → 在 `claude-code/` 中集成进日常开发 → 借助 `awesome-claude-skills/` 拓展思路。

## 3️⃣ 快速记忆版

- 想 **查规范 / 看例子**：去 `skills/`，其中就有 `skill-creator/` 本体。
- 想 **创建 / 校验 / 打包技能**：用 `skills/skill-creator/scripts/*.py`（本仓库 README 已给出命令）。
- 想 **通过 API 调用 Skills**：看 `claude-cookbooks/skills/` 里的 Notebook 示例。
- 想 **在终端 / IDE 里用 Skills**：用 `claude-code/`，让 Claude Code 调用这些技能。
- 想 **看别人怎么玩 Skills**：翻 `awesome-claude-skills/` 里的社区项目。

