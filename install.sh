#!/bin/bash
# 安装脚本 - Stock MCP Server

echo "🚀 安装 Stock MCP Server 依赖..."

# 使用 --break-system-packages 绕过 macOS 限制
pip3 install --break-system-packages -r requirements.txt

echo "✅ 安装完成！"
echo ""
echo "现在可以运行: python3 stock_mcp_server.py"