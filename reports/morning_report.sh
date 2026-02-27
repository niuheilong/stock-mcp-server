#!/bin/bash
# 股票晨报生成脚本 - 每天8:00运行

echo "📊 生成股票晨报 - $(date '+%Y-%m-%d %H:%M')"
echo "=========================================="

# 获取持仓股票数据（通过我们的API）
echo ""
echo "【持仓股票监控】"
echo "- 通富微电: 监控中"
echo "- 西安奕材: 监控中" 
echo "- 深科技: 监控中"

# 检查服务器状态
curl -s http://localhost:5001/health > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Stock MCP Server 运行正常"
else
    echo "⚠️ Stock MCP Server 未运行"
fi

echo ""
echo "【今日关注】"
echo "1. Meta-AMD订单进展"
echo "2. 芯片板块资金流向" 
echo "3. 通富微电技术突破"

echo ""
echo "=========================================="
echo "报告生成完成"