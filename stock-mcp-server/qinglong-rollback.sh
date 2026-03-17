#!/bin/bash
# 青龙 Stock MCP Server - 回滚脚本
# 使用方法: ./qinglong-rollback.sh [备份文件]

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKUP_DIR="$PROJECT_DIR/backups"

echo "🐉 青龙回滚工具"
echo "==============="
echo ""

# 如果没有指定备份文件，列出可用备份
if [ -z "$1" ]; then
    echo "📋 可用备份列表:"
    echo ""
    
    if [ ! -d "$BACKUP_DIR" ] || [ -z "$(ls -A "$BACKUP_DIR" 2>/dev/null)" ]; then
        echo "   暂无备份文件"
        exit 1
    fi
    
    ls -lt "$BACKUP_DIR"/*.tar.gz 2>/dev/null | head -10 | nl -w2 -s'. ' | while read line; do
        echo "   $line"
    done
    
    echo ""
    echo "Usage: $0 <备份文件路径>"
    echo "Example: $0 $BACKUP_DIR/qinglong_backup_20260317_213815.tar.gz"
    exit 1
fi

BACKUP_FILE="$1"

# 检查备份文件
if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ 错误: 备份文件不存在: $BACKUP_FILE"
    exit 1
fi

echo "⚠️  即将回滚到: $(basename $BACKUP_FILE)"
echo "   目标目录: $PROJECT_DIR"
echo ""
echo "⏳ 5秒后开始回滚..."
echo "   按 Ctrl+C 取消"
sleep 5

# 创建当前状态备份（防止后悔）
echo ""
echo "💾 备份当前状态..."
CURRENT_BACKUP="$BACKUP_DIR/pre_rollback_$(date +%Y%m%d_%H%M%S).tar.gz"
tar czf "$CURRENT_BACKUP" \
    -C "$PROJECT_DIR" \
    --exclude='backups' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    . 2>/dev/null || true

echo "   当前状态已保存: $(basename $CURRENT_BACKUP)"

# 执行回滚
echo ""
echo "🔄 执行回滚..."
cd "$PROJECT_DIR"

# 解压备份
tar xzf "$BACKUP_FILE" --overwrite

echo ""
echo "✅ 回滚完成!"
echo ""
echo "📝 如需撤销回滚，使用命令:"
echo "   $0 $CURRENT_BACKUP"
echo ""
echo "🔧 请重启服务以应用更改:"
echo "   python server.py"
