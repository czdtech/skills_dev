# Requirements Document

## Introduction

本规范定义了将 droid-executor-skill 和 droid-executor-mcp 优化为符合各自标准的工作。

- **droid-executor-skill** 参照已完成的 **codex-advisor-skill** 实现，遵循 Claude Code Skills 规范
- **droid-executor-mcp** 参照已完成的 **codex-advisor-mcp** 实现，作为 MCP 服务器项目

两个项目的 bridge 实现基本一致，主要差异在于目录结构：
- Skill 项目使用 `scripts/bridge/` 目录（Skills 规范要求）
- MCP 项目使用 `bridges/` 目录（MCP 项目惯例）

## Glossary

- **Skill**: 一个包含 SKILL.md 文件的文件夹，供 AI 代理动态发现和加载以执行特定任务
- **Bridge**: 一个 HTTP 服务进程，负责将请求转换为 CLI 调用
- **PM2**: Node.js 进程管理器，用于管理 Bridge 服务的生命周期
- **Wrapper**: 封装脚本，提供简化的命令行接口并自动管理 Bridge 服务
- **MCP**: Model Context Protocol，AI 代理与工具交互的协议
- **Socket Port Check**: 使用 TCP socket 连接检测服务端口是否开放的方法

## Requirements

### Requirement 1: Skill 目录结构标准化

**User Story:** As a skill developer, I want droid-executor-skill to have a standardized directory structure, so that it complies with the Claude Code Skills specification and is consistent with codex-advisor-skill.

#### Acceptance Criteria

1. WHEN the skill directory is organized THEN the Droid_Executor_Skill SHALL have `scripts/bridge/` directory containing bridge implementation files (droid_bridge.py, server_lib.py)
2. WHEN the skill directory is organized THEN the Droid_Executor_Skill SHALL have `references/` directory containing protocol documentation (droid-executor-protocol.md)
3. WHEN the skill directory is organized THEN the Droid_Executor_Skill SHALL NOT contain `bridges/` or `docs/` directories at the root level
4. WHEN the skill directory is organized THEN the Droid_Executor_Skill SHALL contain only SKILL.md, LICENSE.txt, ecosystem.config.cjs, and the scripts/ and references/ directories as primary content

### Requirement 2: SKILL.md 规范化

**User Story:** As a skill developer, I want the SKILL.md file to include all required and recommended fields, so that it fully complies with the Agent Skills Spec.

#### Acceptance Criteria

1. WHEN the SKILL.md frontmatter is defined THEN the Droid_Executor_Skill SHALL include `name` field with value `droid-executor`
2. WHEN the SKILL.md frontmatter is defined THEN the Droid_Executor_Skill SHALL include `description` field describing when to use the skill
3. WHEN the SKILL.md frontmatter is defined THEN the Droid_Executor_Skill SHALL include `license` field with value `Complete terms in LICENSE.txt`
4. WHEN the skill is packaged THEN the Droid_Executor_Skill SHALL include a LICENSE.txt file with Apache License 2.0 terms

### Requirement 3: Skill ecosystem 配置优化

**User Story:** As a skill developer, I want the skill ecosystem configuration to use the correct format and paths, so that PM2 can properly manage the bridge service.

#### Acceptance Criteria

1. WHEN the ecosystem configuration is defined THEN the Droid_Executor_Skill SHALL use `.cjs` file extension for Node.js CommonJS compatibility
2. WHEN the ecosystem configuration is defined THEN the Droid_Executor_Skill SHALL reference bridge script at `./scripts/bridge/droid_bridge.py`
3. WHEN the ecosystem configuration is defined THEN the Droid_Executor_Skill SHALL configure PORT environment variable as 53002
4. WHEN the ecosystem configuration is defined THEN the Droid_Executor_Skill SHALL configure DROID_TIMEOUT environment variable as 600

### Requirement 4: Skill wrapper 脚本优化

**User Story:** As a skill user, I want the wrapper script to automatically manage the bridge service, so that I can use the skill without manual service management.

#### Acceptance Criteria

1. WHEN the wrapper script is executed THEN the Droid_Executor_Skill SHALL check if the bridge port (53002) is open using socket connection
2. WHEN the bridge is not running THEN the Droid_Executor_Skill SHALL automatically start the bridge using PM2
3. WHEN starting the bridge THEN the Droid_Executor_Skill SHALL wait up to 30 seconds for the bridge to become ready
4. WHEN the bridge fails to start THEN the Droid_Executor_Skill SHALL provide a warning message and continue execution attempt

### Requirement 5: Skill 非标准文件清理

**User Story:** As a skill developer, I want to remove non-standard files from the skill directory, so that the skill package is clean and compliant.

#### Acceptance Criteria

1. WHEN the skill directory is cleaned THEN the Droid_Executor_Skill SHALL NOT contain BUG_REPORT.md, DOCUMENTATION_CHECKLIST.md, FIXES_SUMMARY.md, FOCUSED_TEST_REPORT.md, SKILL_OPTIMIZATION_SUMMARY.md, STANDARDS_COMPLIANCE_REPORT.md files
2. WHEN the skill directory is cleaned THEN the Droid_Executor_Skill SHALL NOT contain README.md file (SKILL.md serves this purpose)
3. WHEN the skill directory is cleaned THEN the Droid_Executor_Skill SHALL NOT contain test files (hello.txt, test.txt)
4. WHEN the skill directory is cleaned THEN the Droid_Executor_Skill SHALL NOT contain .factory/ directory

### Requirement 6: MCP ecosystem 配置优化

**User Story:** As a MCP developer, I want droid-executor-mcp to use the correct ecosystem configuration format, so that it is consistent with codex-advisor-mcp.

#### Acceptance Criteria

1. WHEN the MCP ecosystem configuration is defined THEN the Droid_Executor_MCP SHALL use `.cjs` file extension for Node.js CommonJS compatibility
2. WHEN the MCP ecosystem configuration is defined THEN the Droid_Executor_MCP SHALL reference bridge script at `./bridges/droid_bridge.py`
3. WHEN the MCP ecosystem configuration is defined THEN the Droid_Executor_MCP SHALL configure PORT environment variable as 53002
4. WHEN the MCP ecosystem configuration is defined THEN the Droid_Executor_MCP SHALL configure DROID_TIMEOUT environment variable as 600

### Requirement 7: MCP 服务器优化

**User Story:** As a MCP developer, I want the mcp_server.py to use socket port checking for bridge detection, so that it is consistent with codex-advisor-mcp.

#### Acceptance Criteria

1. WHEN the MCP server starts THEN the Droid_Executor_MCP SHALL use socket port checking to detect if bridge is running
2. WHEN the MCP server manages bridge lifecycle THEN the Droid_Executor_MCP SHALL reference ecosystem.config.cjs (not .js)

### Requirement 8: Bridge 代码清理

**User Story:** As a developer, I want the bridge implementation to be clean and functional, so that it properly handles Droid CLI execution.

#### Acceptance Criteria

1. WHEN the bridge code is reviewed THEN the Droid_Bridge SHALL NOT contain debug print statements in production code
2. WHEN the bridge code is reviewed THEN the Droid_Bridge SHALL NOT contain unused code blocks or excessive comments
3. WHEN the bridge handles requests THEN the Droid_Bridge SHALL properly validate input parameters
4. WHEN the bridge executes commands THEN the Droid_Bridge SHALL respect the configured timeout value

### Requirement 9: MCP 非标准文件清理

**User Story:** As a MCP developer, I want to remove non-standard files from the MCP directory, so that the project is clean.

#### Acceptance Criteria

1. WHEN the MCP directory is cleaned THEN the Droid_Executor_MCP SHALL NOT contain fibonacci.py and hello_world.py test files
2. WHEN the MCP directory is cleaned THEN the Droid_Executor_MCP SHALL NOT contain .factory/ directory
3. WHEN the MCP directory is cleaned THEN the Droid_Executor_MCP SHALL retain only essential files: mcp_server.py, ecosystem.config.cjs, requirements.txt, setup.sh, README.md, .gitignore, bridges/ directory
