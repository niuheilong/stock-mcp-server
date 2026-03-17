#!/bin/bash
# 青龙 Stock MCP Server - 备份脚本
# 使用方法: ./qinglong-backup.sh [备份名称]

set -e

# 配置
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKUP_DIR="$PROJECT_DIR/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="${1:-qinglong_backup_$TIMESTAMP}"

echo "🐉 青龙备份工具"
echo "==============="
echo ""

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 检查项目文件
if [ ! -f "$PROJECT_DIR/server.py" ]; then
    echo "❌ 错误: 未找到 server.py，请在项目目录中运行此脚本"
    exit 1
fi

echo "📦 正在备份项目..."
echo "   源目录: $PROJECT_DIR"
echo "   备份名: $BACKUP_NAME"
echo ""

# 执行备份
tar czf "$BACKUP_DIR/${BACKUP_NAME}.tar.gz" \
    -C "$PROJECT_DIR" \
    --exclude='backups' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    --exclude='*.db' \
    --exclude='test_*.db' \
    .

# 保留最近20个备份
echo "🧹 清理旧备份..."
ls -t "$BACKUP_DIR"/qinglong_backup_*.tar.gz 2>/dev/null | tail -n +21 | xargs rm -f 2>/dev/null || true

echo ""
echo "✅ 备份完成!"
echo "   文件: $BACKUP_DIR/${BACKUP_NAME}.tar.gz"
echo "   大小: $(du -h "$BACKUP_DIR/${BACKUP_NAME}.tar.gz" | cut -f1)"
echo ""
echo "📊 最近5个备份:"
ls -lt "$BACKUP_DIR"/qinglong_backup_*.tar.gz 2>/dev/null | head -5 | awk '{print "   " $9 " (" $5 ")"}'
