#!/bin/bash
# Evolver & EvoMap 监控脚本
# 每天自动检查状态

REPORT_FILE="/tmp/evolver_evomap_daily_report.txt"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "🔍 Evolver & EvoMap 每日监控报告" > $REPORT_FILE
echo "时间: $DATE" >> $REPORT_FILE
echo "======================================" >> $REPORT_FILE
echo "" >> $REPORT_FILE

# 检查 Evolver 状态（如果运行中）
echo "📊 Evolver 状态:" >> $REPORT_FILE
if pgrep -f "evolver" > /dev/null; then
    echo "  ✅ Evolver 正在运行" >> $REPORT_FILE
else
    echo "  ⏸️ Evolver 未运行（可能需要启动）" >> $REPORTFILE
fi
echo "" >> $REPORT_FILE

# 检查 EvoMap 相关文件
echo "🌐 EvoMap 状态:" >> $REPORT_FILE
if ls /tmp/evomap* 1> /dev/null 2>&1; then
    echo "  ✅ 找到 EvoMap 相关文件:" >> $REPORT_FILE
    ls -lh /tmp/evomap* | awk '{print "    - " $9 " (" $5 ")"}' >> $REPORT_FILE
else
    echo "  ⚠️ 未找到 EvoMap 临时文件" >> $REPORT_FILE
fi

# 检查 GitHub 仓库状态
echo "" >> $REPORT_FILE
echo "📁 GitHub 仓库状态:" >> $REPORT_FILE
if [ -d "$HOME/.openclaw/workspace/.git" ]; then
    cd $HOME/.openclaw/workspace
    COMMIT_COUNT=$(git rev-list --count HEAD 2>/dev/null || echo "0")
    LAST_COMMIT=$(git log -1 --format=%cd --date=short 2>/dev/null || echo "无")
    echo "  总提交数: $COMMIT_COUNT" >> $REPORT_FILE
    echo "  最后提交: $LAST_COMMIT" >> $REPORT_FILE
else
    echo "  未找到 Git 仓库" >> $REPORT_FILE
fi

echo "" >> $REPORT_FILE
echo "💡 今日行动建议:" >> $REPORT_FILE
echo "  1. 检查 awesome-mcp-servers PR 状态" >> $REPORT_FILE
echo "  2. 查看 EvoMap 胶囊发布情况" >> $REPORT_FILE
echo "  3. 更新 Evolver 配置（如有需要）" >> $REPORT_FILE

cat $REPORT_FILE
