# 端口变更说明

## 背景

为避免与常用服务端口冲突，已将所有 Bridge 服务的端口从低位端口改为高位端口。

## 端口变更

| 服务 | 旧端口 | 新端口 | 说明 |
|------|--------|--------|------|
| codex-bridge | 3001 | **53001** | Codex Advisor Bridge |
| droid-bridge | 3002 | **53002** | Droid Executor Bridge |

**端口选择理由**：
- 50000+ 范围属于动态/私有端口，不太可能与系统服务冲突
- 保留原端口尾号（01、02），便于记忆
- 开头的 "5" 表示高位端口，"3" 对应原端口的 "3000" 系列

## 影响范围

### 已更新的配置文件

#### Skills 版本
- ✅ `codex-advisor-skill/ecosystem.config.js`
- ✅ `droid-executor-skill/ecosystem.config.js`

#### MCP 版本
- ✅ `codex-advisor-mcp/ecosystem.config.js`
- ✅ `codex-advisor-mcp/mcp_server.py` （默认 URL）
- ✅ `droid-executor-mcp/ecosystem.config.js`
- ✅ `droid-executor-mcp/mcp_server.py` （默认 URL）

#### 原始版本
- ✅ `multi-agent-mcp/ecosystem.config.js`
- ✅ `multi-agent-mcp/mcp_server.py`

### 已更新的文档

- ✅ `codex-advisor-mcp/README.md`
- ✅ `droid-executor-mcp/README.md`
- ✅ `docs/multi-agent-architecture-alignment.md`
- ✅ `docs/multi-agent-mcp-migration-guide.md`
- ✅ `docs/multi-agent-mcp-quick-reference.md`
- ✅ `docs/multi-agent-mcp-split-summary.md`

## 如何应用变更

### 新安装用户

**无需任何操作**。所有配置文件已更新为新端口，按照文档正常安装即可。

### 现有用户

如果您已经安装并运行了旧版本，需要重启 Bridge 服务：

```bash
# 1. 停止现有服务
npx pm2 stop all

# 2. 删除旧的 PM2 进程配置
npx pm2 delete all

# 3.重新启动（会使用新端口）
cd codex-advisor-mcp  # 或对应的项目目录
npx pm2 start ecosystem.config.js

# 4. 验证
npx pm2 status
# 应该看到 PORT 列显示 53001 或 53002
```

### 验证端口

```bash
# 检查端口是否正在监听
lsof -i :53001  # Codex Bridge
lsof -i :53002  # Droid Bridge

# 或使用 netstat
netstat -tuln | grep 53001
netstat -tuln | grep 53002

# 或测试连接
curl http://localhost:53001/analyze -X POST -d '{"problem":"test"}'
curl http://localhost:53002/execute -X POST -d '{"objective":"test"}'
```

## 自定义端口

如需使用其他端口，可在各项目的 `ecosystem.config.js` 中修改：

```javascript
env: {
  PORT: 您的端口号,
  // ... 其他配置
}
```

对于 MCP 版本，还需同步更新 `mcp_server.py` 中的默认 URL，或设置环境变量：

```bash
export CODEX_BRIDGE_URL="http://localhost:您的端口号"
export DROID_BRIDGE_URL="http://localhost:您的端口号"
```

## 端口范围参考

| 范围 | 类型 | 说明 |
|------|------|------|
| 0-1023 | 系统保留端口 | 需要 root 权限，不建议使用 |
| 1024-49151 | 注册端口 | 常用软件端口，易冲突 |
| 49152-65535 | 动态/私有端口 | **推荐使用**，冲突概率低 |

本次选择的 **53001-53002** 在动态端口范围内，既安全又易记。

## 兼容性说明

### 与旧版本兼容

- ✅ **API 签名不变**：工具调用方式完全相同
- ✅ **功能不变**：Bridge 逻辑完全相同
- ⚠️ **端口不兼容**：无法同时运行新旧版本（除非修改端口）

### 迁移路径

从旧端口（3001/3002）迁移到新端口（53001/53002）：

1. **停止旧版 Bridge**
2. **拉取最新代码**（已包含端口更新）
3. **重启服务**

无需修改任何 MCP 客户端配置（如 Claude Code 中的 MCP 注册），因为端口变更在 Bridge 层，对 MCP 客户端透明。

## 故障排查

### 端口已被占用

如果新端口仍被占用：

```bash
# 查看占用端口的进程
lsof -i :53001
# 或
sudo netstat -tulnp | grep 53001

# 如果是其他服务占用，选择替代端口
# 编辑 ecosystem.config.js，选择其他端口（如 54001）
```

### 无法连接到 Bridge

```bash
# 1. 确认 PM2 进程正在运行
npx pm2 status

# 2. 检查进程日志
npx pm2 logs codex-bridge
npx pm2 logs droid-bridge

# 3. 确认端口监听
lsof -i :53001
lsof -i :53002
```

## 常见问题

### Q: 为什么不使用默认的 3001/3002？

**A**: 3000 系列端口常被开发工具占用（如 React dev server: 3000, Next.js: 3000, 等），容易冲突。

### Q: 可以改回 3001/3002 吗？

**A**: 可以。在 `ecosystem.config.js` 中修改 `PORT` 即可。但建议使用高位端口避免冲突。

### Q: MCP 客户端需要重新配置吗？

**A**: **不需要**。端口变更只影响 Bridge 层，MCP 服务器会自动连接到正确的 Bridge 端口。

### Q: 这会影响性能吗？

**A**: **不会**。端口号对性能没有影响，只是网络地址的标识符。

## 更新日期

- **初次变更**: 2025-11-24
- **影响版本**: 所有 codex-advisor 和 droid-executor 项目（Skill & MCP）

---

**总结**：所有服务端口已从 3001/3002 更新为 53001/53002，现有用户只需重启 PM2 服务即可应用变更。
