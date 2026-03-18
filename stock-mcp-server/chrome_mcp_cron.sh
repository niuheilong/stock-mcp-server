#!/bin/bash
# 青龙 Chrome MCP 定时抓取任务
# 使用方法: ./chrome_mcp_cron.sh [股票代码]

STOCK_CODE="${1:-sh600410}"
LOG_FILE="/Users/laoniu/.openclaw/workspace/stock-mcp-server/logs/chrome_mcp_$(date +%Y%m%d).log"

echo "$(date '+%Y-%m-%d %H:%M:%S') - 开始抓取: $STOCK_CODE" >> "$LOG_FILE"

cd /Users/laoniu/.openclaw/workspace/stock-mcp-server
python3 chrome_mcp_workflow.py --code "$STOCK_CODE" >> "$LOG_FILE" 2>&1

echo "$(date '+%Y-%m-%d %H:%M:%S') - 抓取完成" >> "$LOG_FILE"
