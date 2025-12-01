# Implementation Plan

## droid-executor-skill 优化

- [x] 1. 目录结构重组
  - [x] 1.1 创建 scripts/bridge/ 目录并移动 bridge 文件
    - 将 `bridges/droid_bridge.py` 移动到 `scripts/bridge/droid_bridge.py`
    - 将 `bridges/server_lib.py` 移动到 `scripts/bridge/server_lib.py`
    - 删除空的 `bridges/` 目录
    - _Requirements: 1.1, 1.3_
  - [x] 1.2 创建 references/ 目录并移动文档
    - 将 `docs/droid-executor-protocol.md` 移动到 `references/droid-executor-protocol.md`
    - 删除空的 `docs/` 目录
    - _Requirements: 1.2, 1.3_
  - [x] 1.3 清理非标准文件
    - 删除 BUG_REPORT.md, DOCUMENTATION_CHECKLIST.md, FIXES_SUMMARY.md
    - 删除 FOCUSED_TEST_REPORT.md, SKILL_OPTIMIZATION_SUMMARY.md, STANDARDS_COMPLIANCE_REPORT.md
    - 删除 README.md, hello.txt, test.txt
    - 删除 .factory/ 目录
    - 删除 scripts/ 下的测试脚本 (comprehensive_test_suite.py, focused_test_suite.py, test_suite_droid.py, verify_fixes.py, wrapper_service.py)
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [x] 2. SKILL.md 和 LICENSE.txt 更新
  - [x] 2.1 更新 SKILL.md frontmatter
    - 添加 `license: Complete terms in LICENSE.txt` 字段
    - 确保 name 和 description 字段正确
    - _Requirements: 2.1, 2.2, 2.3_
  - [x] 2.2 创建 LICENSE.txt 文件
    - 使用 Apache License 2.0 模板
    - 参照 codex-advisor-skill/LICENSE.txt 格式
    - _Requirements: 2.4_

- [x] 3. ecosystem 配置优化
  - [x] 3.1 重命名并更新 ecosystem.config.cjs
    - 将 ecosystem.config.js 重命名为 ecosystem.config.cjs
    - 更新 script 路径为 `./scripts/bridge/droid_bridge.py`
    - 确保 PORT=53002 和 DROID_TIMEOUT=600 配置正确
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [x] 4. wrapper 脚本优化
  - [x] 4.1 重写 wrapper_droid.py
    - 添加 socket 端口检测函数 `is_port_open()`
    - 添加 bridge 自动管理函数 `ensure_bridge()`
    - 更新 BRIDGE_PORT 为 53002
    - 更新 BRIDGE_URL 为 `http://localhost:53002`
    - 参照 codex-advisor-skill/scripts/wrapper_codex.py 实现
    - _Requirements: 4.1, 4.2, 4.3, 4.4_
  - [x] 4.2 编写 Property 1 属性测试
    - **Property 1: Socket Port Detection Accuracy**
    - **Validates: Requirements 4.1**

- [x] 5. Bridge 代码清理
  - [x] 5.1 清理 droid_bridge.py
    - 移除 build_prompt 函数中的 debug print 语句
    - 移除 build_prompt 函数中未使用的 cmd 构建代码块
    - 移除过多的注释
    - _Requirements: 8.1, 8.2_
  - [x] 5.2 编写 Property 2 属性测试
    - **Property 2: Input Validation Completeness**
    - **Validates: Requirements 8.3**

- [x] 6. Checkpoint - Skill 项目验证
  - Ensure all tests pass, ask the user if questions arise.

## droid-executor-mcp 优化

- [x] 7. MCP ecosystem 配置优化
  - [x] 7.1 重命名并更新 ecosystem.config.cjs
    - 将 ecosystem.config.js 重命名为 ecosystem.config.cjs
    - 确保 script 路径为 `./bridges/droid_bridge.py`
    - 确保 PORT=53002 和 DROID_TIMEOUT=600 配置正确
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 8. MCP 服务器优化
  - [x] 8.1 更新 mcp_server.py
    - 更新 startup/shutdown 函数引用 ecosystem.config.cjs
    - _Requirements: 7.1, 7.2_

- [x] 9. MCP Bridge 代码清理
  - [x] 9.1 清理 bridges/droid_bridge.py
    - 移除 build_prompt 函数中的 debug print 语句
    - 移除 build_prompt 函数中未使用的 cmd 构建代码块
    - 移除过多的注释
    - _Requirements: 8.1, 8.2_

- [x] 10. MCP 非标准文件清理
  - [x] 10.1 删除测试文件和目录
    - 删除 fibonacci.py, hello_world.py
    - 删除 .factory/ 目录
    - 删除 tests/ 目录
    - 删除 run_tests.py, requirements-test.txt, .coveragerc
    - _Requirements: 9.1, 9.2, 9.3_

- [x] 11. Final Checkpoint - 完整验证
  - Ensure all tests pass, ask the user if questions arise.
