#!/bin/bash
set -e

echo "======================================"
echo "Codex Advisor MCP 安装脚本"
echo "======================================"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 1. 检查 Python 版本
echo "✓ 检查 Python 版本..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 python3，请先安装 Python 3.10+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "  找到 Python $PYTHON_VERSION"

# 2. 创建虚拟环境
if [ ! -d ".venv" ]; then
    echo "✓ 创建 Python 虚拟环境..."
    python3 -m venv .venv
else
    echo "✓ 虚拟环境已存在"
fi

# 3. 激活虚拟环境并安装依赖
echo "✓ 安装 Python 依赖..."
source .venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q

echo "  已安装: $(pip list | grep mcp | awk '{print $1 " " $2}')"
echo "  已安装: $(pip list | grep httpx | awk '{print $1 " " $2}')"

# 4. 检查 Codex CLI
echo "✓ 检查 Codex CLI..."
if command -v codex &> /dev/null; then
    CODEX_VERSION=$(codex --version 2>&1 | head -n 1 || echo "未知版本")
    echo "  找到 Codex: $CODEX_VERSION"
else
    echo "  ⚠️  警告: 未找到 codex 命令"
    echo "  请运行: npm install -g @openai/codex"
fi

# 5. 检查 PM2
echo "✓ 检查 PM2..."
if command -v pm2 &> /dev/null; then
    echo "  找到 PM2: $(pm2 --version)"
elif command -v npx &> /dev/null; then
    echo "  将使用 npx pm2"
else
    echo "  ⚠️  警告: 未找到 pm2 或 npx"
    echo "  请安装 Node.js"
fi

# 6. 注册到 Claude Code
echo ""
echo "======================================"
echo "注册到 Claude Code"
echo "======================================"
echo ""
echo "运行以下命令将此 MCP 服务器注册到 Claude Code："
echo ""
echo "  claude mcp add --transport stdio codex-advisor \\"
echo "    -- $SCRIPT_DIR/.venv/bin/python \\"
echo "       $SCRIPT_DIR/mcp_server.py"
echo ""
echo "或者手动添加到 ~/.claude/claude_desktop_config.json （如使用 Claude Desktop）"
echo ""

# 7. 完成
echo "======================================"
echo "✅ 安装完成！"
echo "======================================"
echo ""
echo "下一步："
echo "  1. 确保 Codex CLI 已安装并配置"
echo "  2. 注册 MCP 服务器到 Claude Code（见上方命令）"
echo "  3. 验证: claude mcp list"
echo "  4. 测试: 在 Claude Code 中询问技术问题"
echo ""
