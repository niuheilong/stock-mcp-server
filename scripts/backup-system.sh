#!/bin/bash
# backup-system.sh - 系统配置备份脚本
# Created: 2026-03-17

set -e

WORKSPACE="$HOME/.openclaw/workspace"
BACKUP_DIR="$WORKSPACE/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="system_backup_$TIMESTAMP"

echo "🗄️  开始系统备份..."

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 备份关键文件
tar czf "$BACKUP_DIR/${BACKUP_NAME}.tar.gz" \
    -C "$WORKSPACE" \
    AGENTS.md \
    SOUL.md \
    SYSTEM_GUIDELINES.md \
    HEARTBEAT.md \
    IDENTITY.md \
    USER.md \
    TOOLS.md \
    memory/ \
    2>/dev/null || true

# 保留最近10个备份
ls -t "$BACKUP_DIR"/system_backup_*.tar.gz 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null || true

echo "✅ 备份完成: $BACKUP_DIR/${BACKUP_NAME}.tar.gz"
echo "📊 当前备份列表:"
ls -lh "$BACKUP_DIR"/system_backup_*.tar.gz 2>/dev/null | tail -5
