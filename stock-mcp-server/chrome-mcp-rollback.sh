#!/bin/bash
# 青龙 Chrome MCP 工作流 - 回滚脚本
# 使用方法: ./chrome-mcp-rollback.sh [备份文件]

set -e

PROJECT_DIR="/Users/laoniu/.openclaw/workspace/stock-mcp-server"
BACKUP_DIR="$PROJECT_DIR/backups/chrome-mcp"

echo "🐉 青龙 Chrome MCP 工作流回滚"
echo "==============================="
echo ""

# 如果没有指定备份文件，列出可用备份
if [ -z "$1" ]; then
    echo "📋 可用备份列表:"
    echo ""
    
    if [ ! -d "$BACKUP_DIR" ] || [ -z "$(ls -A "$BACKUP_DIR" 2>/dev/null)" ]; then
        echo "   暂无备份文件"
        exit 1
    fi
    
    ls -lt "$BACKUP_DIR"/chrome-mcp-backup_*.tar.gz 2>/dev/null | nl -w2 -s'. ' | while read line; do
        echo "   $line"
    done
    
    echo ""
    echo "Usage: $0 <备份文件路径>"
    echo "Example: $0 $BACKUP_DIR/chrome-mcp-backup_20260318_175500.tar.gz"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ 备份文件不存在: $BACKUP_FILE"
    exit 1
fi

echo "⚠️  即将回滚到: $(basename $BACKUP_FILE)"
echo "   目标目录: $PROJECT_DIR"
echo ""
echo "⏳ 5秒后开始回滚..."
echo "   按 Ctrl+C 取消"
sleep 5

# 先备份当前状态（防止后悔）
echo ""
echo "💾 备份当前状态..."
CURRENT_BACKUP="$BACKUP_DIR/pre_rollback_$(date +%Y%m%d_%H%M%S).tar.gz"
tar czf "$CURRENT_BACKUP" \
    -C "$PROJECT_DIR" \
    chrome_mcp_workflow.py \
    chrome_mcp_analyzer.py \
    chrome_mcp_cron.sh \
    *.db \
    2>/dev/null || true

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
echo "🔧 请检查文件是否正确恢复:"
ls -lh chrome_mcp_*.py chrome_mcp_*.sh 2>/dev/null | awk '{print "   " $9 " (" $5 ")"}'
