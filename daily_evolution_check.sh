#!/bin/bash
# 每日进化监控脚本
# 添加到 crontab: 0 9 * * * /path/to/daily_evolution_check.sh

cd ~/projects/stock-mcp-server

echo "🔍 $(date '+%Y-%m-%d %H:%M') 开始每日进化检查"

# 1. 检查 EvoMap PR 状态
echo "📋 1. 检查 awesome-mcp-servers PR 状态..."
PR_URL="https://github.com/punkpeye/awesome-mcp-servers/pulls"
echo "   PR #2463 链接: $PR_URL"
echo "   请手动检查是否已合并"

# 2. 检查 Evolver（如果有运行）
echo ""
echo "🧬 2. 检查 Evolver 状态..."
if pgrep -f "evolver" > /dev/null; then
    echo "   ✅ Evolver 正在运行"
    # 这里可以添加检查进化日志的逻辑
else
    echo "   ⏸️ Evolver 未运行"
    echo "   如需启动: python3 capability-evolver/main.py"
fi

# 3. 检查 EvoMap 发布
echo ""
echo "🌐 3. 检查 EvoMap 发布状态..."
echo "   建议: 每周发布一次 Stock MCP Server 胶囊"
echo "   命令: python3 publish_to_evomap.py"

# 4. 生成监控报告
echo ""
echo "📊 4. 生成监控报告..."
python3 evolution_monitor.py

# 5. 检查 GitHub 仓库更新
echo ""
echo "📁 5. 检查 GitHub 仓库..."
git fetch origin
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ $LOCAL != $REMOTE ]; then
    echo "   ⚠️ 本地与远程不同步，建议推送更新"
    git log --oneline HEAD..origin/main
else
    echo "   ✅ 仓库已同步"
fi

echo ""
echo "✅ $(date '+%Y-%m-%d %H:%M') 检查完成"
echo ""
echo "💡 今日待办:"
echo "   ☐ 检查 PR #2463 审核状态"
echo "   ☐ 查看是否有新的 Issue/PR"
echo "   ☐ 阅读 Evolver 日志（如有）"
echo "   ☐ 考虑发布 EvoMap 胶囊"
