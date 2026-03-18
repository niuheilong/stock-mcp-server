#!/bin/bash
# 青龙 Chrome MCP 工作流 - 完整备份脚本
# 备份所有工作流相关文件

set -e

PROJECT_DIR="/Users/laoniu/.openclaw/workspace/stock-mcp-server"
BACKUP_DIR="$PROJECT_DIR/backups/chrome-mcp"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="chrome-mcp-backup_$TIMESTAMP"

echo "🐉 青龙 Chrome MCP 工作流备份"
echo "==============================="
echo ""

# 创建备份目录
mkdir -p "$BACKUP_DIR"

echo "📦 备份内容:"
echo "  - chrome_mcp_workflow.py (主工作流)"
echo "  - chrome_mcp_analyzer.py (数据分析)"
echo "  - chrome_mcp_cron.sh (定时任务)"
echo "  - 数据库文件 (*.db)"
echo "  - 配置文件"
echo ""

# 执行备份
tar czf "$BACKUP_DIR/${BACKUP_NAME}.tar.gz" \
    -C "$PROJECT_DIR" \
    chrome_mcp_workflow.py \
    chrome_mcp_analyzer.py \
    chrome_mcp_cron.sh \
    *.db \
    2>/dev/null || true

# 同时备份到本地版本库
LOCAL_BACKUP="/Users/laoniu/牛黑龙的股票行情/青龙项目版本库/v4.4.0/chrome-mcp-backups"
mkdir -p "$LOCAL_BACKUP"
cp "$BACKUP_DIR/${BACKUP_NAME}.tar.gz" "$LOCAL_BACKUP/" 2>/dev/null || true

# 保留最近20个备份
echo "🧹 清理旧备份..."
ls -t "$BACKUP_DIR"/chrome-mcp-backup_*.tar.gz 2>/dev/null | tail -n +21 | xargs rm -f 2>/dev/null || true

echo ""
echo "✅ 备份完成!"
echo "   文件: $BACKUP_DIR/${BACKUP_NAME}.tar.gz"
echo "   大小: $(du -h "$BACKUP_DIR/${BACKUP_NAME}.tar.gz" | cut -f1)"
echo ""
echo "📊 最近5个备份:"
ls -lt "$BACKUP_DIR"/chrome-mcp-backup_*.tar.gz 2>/dev/null | head -5 | awk '{print "   " $9 " (" $5 ")"}'
