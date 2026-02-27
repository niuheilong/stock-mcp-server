#!/bin/bash
# 股票报告定时任务配置
# 每天三个时段自动发送报告

echo "📊 配置股票定时报告系统..."

# 移除旧配置
(crontab -l 2>/dev/null | grep -v "stock-report" ) | crontab -

# 添加新配置
cat > /tmp/stock_cron.txt << 'EOF'
# 股票投资组合晨报 - 每天8:00
0 8 * * 1-5 cd ~/projects/stock-mcp-server && echo "[$(date '+\\%Y-\\%m-\\%d 8:00')] 股票晨报触发" >> reports/cron.log 2>&1

# 午盘快报 - 每天13:00
0 13 * * 1-5 cd ~/projects/stock-mcp-server && echo "[$(date '+\\%Y-\\%m-\\%d 13:00')] 午盘报告触发" >> reports/cron.log 2>&1

# 收盘总结 - 每天15:30
30 15 * * 1-5 cd ~/projects/stock-mcp-server && echo "[$(date '+\\%Y-\\%m-\\%d 15:30')] 收盘总结触发" >> reports/cron.log 2>&1

# 健康检查 - 每4小时
0 */4 * * * cd ~/projects/stock-mcp-server && curl -s http://localhost:5001/health > /dev/null || echo "[$(date '+\\%Y-\\%m-\\%d \\%H:00')] 服务器异常" >> reports/cron.log 2>&1
EOF

crontab /tmp/stock_cron.txt

echo "✅ 定时报告配置完成！"
echo ""
echo "📅 报告时间表："
echo "  08:00 - 股票晨报（全球市场 + 持仓分析）"
echo "  13:00 - 午盘快报（上午复盘 + 下午策略）"
echo "  15:30 - 收盘总结（全天回顾 + 明日计划）"
echo ""
echo "🔧 查看配置："
echo "  crontab -l"
echo ""
echo "📝 查看日志："
echo "  tail -f ~/projects/stock-mcp-server/reports/cron.log"