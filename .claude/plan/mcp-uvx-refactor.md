# MCP Server uvx 改造计划

## 目标
将 codex-advisor-mcp 和 droid-executor-mcp 从 HTTP Bridge 架构改造为 uvx + subprocess 直连模式。

## 架构变更
```
当前：Claude Code → MCP Server → HTTP → PM2 Bridge → Codex CLI
目标：Claude Code → MCP Server (uvx) → subprocess → Codex CLI
```

## 执行步骤
1. codex-advisor-mcp: 创建 pyproject.toml
2. codex-advisor-mcp: 创建 src 目录结构
3. codex-advisor-mcp: 实现 codex_client.py
4. codex-advisor-mcp: 重构 server.py
5. codex-advisor-mcp: 移除旧文件
6. droid-executor-mcp: 同样改造
7. 更新 .mcp.json 配置
8. 测试验证

## 预期结果
- 无端口占用问题
- 符合 MCP STDIO 标准
- 自动生命周期管理
- 保持 30 分钟超时功能
