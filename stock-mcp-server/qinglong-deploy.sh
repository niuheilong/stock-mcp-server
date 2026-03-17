#!/bin/bash
# 青龙 Stock MCP Server - 完整部署脚本
# 一键安装、备份、启动

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🐉 青龙部署工具"
echo "==============="
echo ""

# 显示菜单
show_menu() {
    echo "请选择操作:"
    echo ""
    echo "  1. 安装依赖"
    echo "  2. 运行测试"
    echo "  3. 备份项目"
    echo "  4. 回滚项目"
    echo "  5. 启动服务"
    echo "  6. 查看状态"
    echo "  0. 退出"
    echo ""
}

# 安装依赖
install_deps() {
    echo "📦 安装依赖..."
    cd "$PROJECT_DIR"
    
    if [ ! -f "requirements.txt" ]; then
        echo "❌ 未找到 requirements.txt"
        return 1
    fi
    
    pip3 install -r requirements.txt
    echo "✅ 依赖安装完成"
}

# 运行测试
run_tests() {
    echo "🧪 运行测试..."
    cd "$PROJECT_DIR"
    
    echo ""
    echo "测试资金流向模块..."
    python3 capital_flow.py
    
    echo ""
    echo "测试板块分析模块..."
    python3 sector_analysis.py
    
    echo ""
    echo "测试回测框架..."
    python3 backtest.py
    
    echo ""
    echo "测试预警系统..."
    python3 alert_system.py
    
    echo ""
    echo "✅ 所有测试完成"
}

# 备份项目
backup_project() {
    echo "💾 备份项目..."
    cd "$PROJECT_DIR"
    ./qinglong-backup.sh
}

# 回滚项目
rollback_project() {
    echo "🔄 回滚项目..."
    cd "$PROJECT_DIR"
    ./qinglong-rollback.sh
}

# 启动服务
start_server() {
    echo "🚀 启动青龙服务..."
    cd "$PROJECT_DIR"
    
    # 先备份
    ./qinglong-backup.sh auto_before_start
    
    echo ""
    echo "启动服务..."
    python3 server.py
}

# 查看状态
show_status() {
    echo "📊 项目状态"
    echo "=========="
    echo ""
    
    cd "$PROJECT_DIR"
    
    echo "项目目录: $PROJECT_DIR"
    echo ""
    
    echo "核心文件:"
    for file in server.py capital_flow.py sector_analysis.py backtest.py alert_system.py; do
        if [ -f "$file" ]; then
            echo "  ✅ $file"
        else
            echo "  ❌ $file (缺失)"
        fi
    done
    
    echo ""
    echo "最近备份:"
    if [ -d "backups" ]; then
        ls -lt backups/*.tar.gz 2>/dev/null | head -3 | awk '{print "  " $9 " (" $5 ")"}'
    else
        echo "  暂无备份"
    fi
    
    echo ""
    echo "服务状态:"
    if pgrep -f "python3 server.py" > /dev/null; then
        echo "  🟢 运行中"
    else
        echo "  🔴 未运行"
    fi
}

# 主循环
while true; do
    show_menu
    read -p "请输入选项 [0-6]: " choice
    
    case $choice in
        1) install_deps ;;
        2) run_tests ;;
        3) backup_project ;;
        4) rollback_project ;;
        5) start_server ;;
        6) show_status ;;
        0) echo "再见!"; exit 0 ;;
        *) echo "无效选项" ;;
    esac
    
    echo ""
    read -p "按回车键继续..."
    echo ""
done
