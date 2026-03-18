#!/bin/bash
# rollback-system.sh - 系统配置回滚脚本
# Usage: ./rollback-system.sh [backup-file]
# Created: 2026-03-17

set -e

WORKSPACE="$HOME/.openclaw/workspace"
BACKUP_DIR="$WORKSPACE/backups"

if [ -z "$1" ]; then
    echo "📋 可用备份列表:"
    ls -lt "$BACKUP_DIR"/system_backup_*.tar.gz 2>/dev/null | head -10 || echo "  无备份文件"
    echo ""
    echo "Usage: $0 <backup-file>"
    echo "Example: $0 $BACKUP_DIR/system_backup_20260317_205200.tar.gz"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ 备份文件不存在: $BACKUP_FILE"
    exit 1
fi

echo "⚠️  即将回滚到: $(basename $BACKUP_FILE)"
echo "⏳ 3秒后开始回滚..."
sleep 3

# 创建当前状态备份（防止回滚后悔）
CURRENT_BACKUP="$BACKUP_DIR/pre_rollback_$(date +%Y%m%d_%H%M%S).tar.gz"
tar czf "$CURRENT_BACKUP" -C "$WORKSPACE" . 2>/dev/null || true
echo "💾 当前状态已保存: $(basename $CURRENT_BACKUP)"

# 执行回滚
cd "$WORKSPACE"
tar xzf "$BACKUP_FILE" --overwrite

echo "✅ 回滚完成！"
echo "🔄 如需撤销回滚，使用: $0 $CURRENT_BACKUP"
