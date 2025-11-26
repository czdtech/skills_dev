# Droid权限"low vs high"问题解析

## 🤔 问题描述

**用户疑问**：
- 代码中写的是 `--auto high` 
- 修改建议是改为 `--auto medium`
- 但测试时实际使用的却是 `--auto low`

这是怎么回事？

---

## 🎯 问题根源

### 代码优先级机制

在 `droid_bridge.py` 中的 `get_droid_cmd_base()` 函数：

```python
def get_droid_cmd_base() -> List[str]:
    env_cmd = os.getenv("DROID_CLI_CMD")  # ⬅️ 优先级1：环境变量
    if env_cmd:
        return env_cmd.split()  # 如果环境变量存在，直接使用
    
    # ⬇️ 优先级2：代码默认值（只有在环境变量不存在时才使用）
    return ["droid", "exec", "--output-format", "json", "--auto", "high"]
```

### 实际配置链

```
ecosystem.config.js (PM2配置)
    ↓ 设置环境变量
DROID_CLI_CMD="droid exec --auto low -o json"  ⬅️ 实际生效！
    ↓ 覆盖
droid_bridge.py 代码默认值 
return [..., "--auto", "high"]  ⬅️ 被忽略！
```

---

## 📂 问题文件定位

### ecosystem.config.js（PM2配置文件）
**位置**: `droid-executor-mcp/ecosystem.config.js`

**原始内容**（第10行）:
```javascript
DROID_CLI_CMD: "droid exec --auto low -o json",  // ⬅️ 这里设置了 low！
```

**为什么存在**：
- PM2 是进程管理器，通过此文件启动桥接服务
- 环境变量在这里定义
- 这个配置**优先于代码中的默认值**

---

## 🔧 完整修复方案

需要修改**两个地方**才能彻底修复：

### 1. ecosystem.config.js（主要问题）
```javascript
// 修改前
DROID_CLI_CMD: "droid exec --auto low -o json",

// 修改后  
DROID_CLI_CMD: "droid exec --auto medium -o json",
```

### 2. droid_bridge.py（备用默认值）
```python
# 修改前
return ["droid", "exec", "--output-format", "json", "--auto", "high"]

# 修改后
return ["droid", "exec", "--output-format", "json", "--auto", "medium"]
```

---

## ✅ 已完成的修复

| 文件 | 修改内容 | 状态 |
|------|---------|------|
| `ecosystem.config.js` | `low` → `medium` | ✅ 已修复 |
| `droid_bridge.py` | `high` → `medium` | ✅ 已修复 |

---

## 🔍 为什么之前看到了 high？

**时间线**：

1. **最初代码**：`droid_bridge.py` 中默认是 `high`
2. **但PM2配置**：`ecosystem.config.js` 中是 `low`
3. **实际运行**：环境变量优先，所以用的是 `low`
4. **代码审查**：只看了 Python 代码，看到 `high`
5. **实际测试**：运行时读取环境变量，用的是 `low`

**结论**：代码中的 `high` 从未真正生效过！

---

## 📊 权限级别对比

| 配置位置 | 原始值 | 现在值 | 实际生效 |
|---------|--------|--------|----------|
| ecosystem.config.js | `low` | `medium` | ✅ **是** |
| droid_bridge.py | `high` | `medium` | ❌ 仅备用 |

---

## 🚀 验证方法

### 1. 检查环境变量配置
```bash
cat droid-executor-mcp/ecosystem.config.js | grep "DROID_CLI_CMD"
# 应该看到: "droid exec --auto medium -o json"
```

### 2. 检查代码默认值
```bash
grep "return.*auto" droid-executor-mcp/bridges/droid_bridge.py
# 应该看到: return ["droid", "exec", "--output-format", "json", "--auto", "medium"]
```

### 3. 测试实际权限
```bash
# 创建文件任务应该成功（medium权限允许）
# 如果失败并提示需要higher权限，说明还是low
```

---

## 💡 经验教训

### 1. **环境变量优先级**
- 环境变量 > 代码默认值
- 检查配置时要看**所有可能的配置源**

### 2. **PM2 配置的影响**
- PM2 的 `ecosystem.config.js` 会设置环境变量
- 修改代码不够，还要修改PM2配置

### 3. **完整的测试**
- 不仅要看代码
- 还要测试实际运行效果
- 检查进程的实际环境变量

---

## 📝 最佳实践

### 推荐配置方式

**统一配置源**（推荐）:
- 只在 `ecosystem.config.js` 中配置
- 代码中保持合理的默认值作为备用

**环境变量优先级**:
```
1. 系统环境变量（export DROID_CLI_CMD=...）
2. PM2配置文件（ecosystem.config.js）
3. 代码默认值（droid_bridge.py）
```

### 修改权限时的检查清单

- [ ] 检查 `ecosystem.config.js`
- [ ] 检查 `droid_bridge.py` 
- [ ] 检查系统环境变量
- [ ] 重启桥接服务
- [ ] 测试实际权限级别

---

## 🎊 总结

**问题**：代码显示 `high`，测试却是 `low`

**原因**：`ecosystem.config.js` 中的环境变量覆盖了代码默认值

**解决**：修改 PM2 配置 + 修改代码默认值 = 全部使用 `medium`

**结果**：现在两处都是 `medium`，不会再有混淆！

---

**调查时间**: 2025-11-25 16:45  
**解决时间**: 2025-11-25 17:00  
**文档版本**: 1.0
