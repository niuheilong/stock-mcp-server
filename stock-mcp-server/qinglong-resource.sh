#!/bin/bash
# 青龙系统资源管理脚本
# 一键执行资源清理、健康检查

echo "🐉 青龙系统资源管理"
echo "===================="
echo ""

# 显示菜单
show_menu() {
    echo "请选择操作:"
    echo ""
    echo "  1. 系统健康检查"
    echo "  2. 强制清理资源"
    echo "  3. 压缩大文件"
    echo "  4. 关闭浏览器"
    echo "  5. 查看状态报告"
    echo "  0. 退出"
    echo ""
}

# 系统健康检查
check_health() {
    echo "📊 执行系统健康检查..."
    echo ""
    cd /Users/laoniu/.openclaw/workspace/stock-mcp-server 2>/dev/null || cd .
    python3 health_monitor.py 2>/dev/null || echo "⚠️ 健康监控模块未安装"
}

# 强制清理资源
force_cleanup() {
    echo "🧹 强制清理资源..."
    echo ""
    
    # 关闭浏览器
    echo "1. 关闭浏览器..."
    python3 -c "from browser import browser; browser.stop()" 2>/dev/null || echo "   浏览器未运行"
    
    # Python垃圾回收
    echo "2. Python垃圾回收..."
    python3 -c "import gc; gc.collect(); print('   完成')"
    
    # 清理缓存
    echo "3. 清理缓存文件..."
    find /tmp -name "openclaw_*" -mtime +1 -delete 2>/dev/null || true
    echo "   完成"
    
    # 压缩日志
    echo "4. 压缩历史日志..."
    cd /Users/laoniu/.openclaw/workspace/memory 2>/dev/null
    for f in *.md; do
        if [ -f "$f" ] && [ ! -f "$f.gz" ]; then
            gzip "$f" 2>/dev/null && echo "   压缩: $f"
        fi
    done 2>/dev/null
    
    echo ""
    echo "✅ 资源清理完成"
}

# 压缩大文件
compress_files() {
    echo "📦 压缩大文件..."
    echo ""
    cd /Users/laoniu/.openclaw/workspace/stock-mcp-server 2>/dev/null || cd .
    python3 -c "
from resource_manager import ResourceManager
manager = ResourceManager()
manager._compress_large_files()
" 2>/dev/null || echo "⚠️ 资源管理模块未安装"
}

# 关闭浏览器
close_browser() {
    echo "🌐 关闭浏览器..."
    python3 -c "from browser import browser; browser.stop()" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✅ 浏览器已关闭"
    else
        echo "⚠️ 浏览器未运行或关闭失败"
    fi
}

# 查看状态报告
show_status() {
    echo "📈 系统状态报告"
    echo ""
    
    # 内存使用
    echo "💾 内存使用:"
    python3 -c "import psutil; m = psutil.virtual_memory(); print(f'  已用: {m.used/1024/1024/1024:.1f}GB / {m.total/1024/1024/1024:.1f}GB ({m.percent}%)')" 2>/dev/null || echo "  需要安装 psutil"
    
    # 磁盘使用
    echo ""
    echo "💿 磁盘使用:"
    df -h /Users/laoniu/.openclaw/workspace 2>/dev/null | tail -1 | awk '{print "  已用: "$3" / "$2" ("$5")"}'
    
    # 工作区大小
    echo ""
    echo "📁 工作区大小:"
    du -sh /Users/laoniu/.openclaw/workspace 2>/dev/null | awk '{print "  " $1}'
    
    # 浏览器状态
    echo ""
    echo "🌐 浏览器状态:"
    python3 -c "from browser_manager import get_browser_manager; m = get_browser_manager(); print(f'  状态: {\"运行中\" if m.browser_active else \"已关闭\"}')" 2>/dev/null || echo "  未知"
    
    echo ""
}

# 主循环
while true; do
    show_menu
    read -p "请输入选项 [0-5]: " choice
    
    case $choice in
        1) check_health ;;
        2) force_cleanup ;;
        3) compress_files ;;
        4) close_browser ;;
        5) show_status ;;
        0) echo "再见!"; exit 0 ;;
        *) echo "无效选项" ;;
    esac
    
    echo ""
    read -p "按回车键继续..."
    echo ""
done
