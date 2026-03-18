#!/bin/bash
# 青龙 Chrome MCP 工作流 - 部署管理工具
# 一键安装、备份、回滚、状态检查

PROJECT_DIR="/Users/laoniu/.openclaw/workspace/stock-mcp-server"

echo "🐉 青龙 Chrome MCP 工作流 - 部署管理"
echo "======================================"
echo ""

show_menu() {
    echo "请选择操作:"
    echo ""
    echo "  1. 安装/更新工作流"
    echo "  2. 运行工作流测试"
    echo "  3. 备份工作流"
    echo "  4. 回滚工作流"
    echo "  5. 查看状态"
    echo "  6. 查看日志"
    echo "  7. 生成分析报告"
    echo "  0. 退出"
    echo ""
}

install_workflow() {
    echo "📦 安装 Chrome MCP 工作流..."
    cd "$PROJECT_DIR"
    
    # 检查依赖
    echo "  检查依赖..."
    pip3 show websocket-client >/dev/null 2>&1 || pip3 install websocket-client --break-system-packages 2>/dev/null
    
    # 创建目录
    mkdir -p logs reports backups/chrome-mcp
    
    # 设置权限
    chmod +x chrome_mcp_cron.sh chrome-mcp-backup.sh chrome-mcp-rollback.sh 2>/dev/null || true
    
    echo "  ✅ 安装完成"
    echo ""
    echo "  文件列表:"
    ls -lh chrome_mcp_*.py chrome-mcp-*.sh 2>/dev/null | awk '{print "    " $9 " (" $5 ")"}'
}

run_test() {
    echo "🧪 运行工作流测试..."
    cd "$PROJECT_DIR"
    python3 -c "
import websocket
import json
import requests

# 检查 Chrome
resp = requests.get('http://localhost:9222/json/version')
print('✅ Chrome:', resp.json().get('Browser'))

# 创建页面
resp = requests.put('http://localhost:9222/json/new?https://quote.eastmoney.com/unify/r/1.600410')
page = resp.json()
print('✅ 页面:', page['id'][:8])

# 连接 WebSocket
ws = websocket.create_connection(page['webSocketDebuggerUrl'])

# 执行 JS
js = '(() => ({title: document.title, url: location.href}))()'
ws.send(json.dumps({
    'id': 1, 'method': 'Runtime.evaluate',
    'params': {'expression': js, 'returnByValue': True}
}))
result = ws.recv()
data = json.loads(result)['result']['result']['value']
print('✅ 数据:', data)

ws.close()
print('✅ 测试通过')
"
}

backup_workflow() {
    echo "💾 备份工作流..."
    cd "$PROJECT_DIR"
    ./chrome-mcp-backup.sh
}

rollback_workflow() {
    echo "🔄 回滚工作流..."
    cd "$PROJECT_DIR"
    ./chrome-mcp-rollback.sh
}

show_status() {
    echo "📊 工作流状态"
    echo "============"
    echo ""
    
    cd "$PROJECT_DIR"
    
    echo "核心文件:"
    for file in chrome_mcp_workflow.py chrome_mcp_analyzer.py chrome_mcp_cron.sh; do
        if [ -f "$file" ]; then
            size=$(ls -lh "$file" | awk '{print $5}')
            echo "  ✅ $file ($size)"
        else
            echo "  ❌ $file (缺失)"
        fi
    done
    
    echo ""
    echo "备份状态:"
    backup_count=$(ls backups/chrome-mcp/*.tar.gz 2>/dev/null | wc -l)
    echo "  备份数量: $backup_count"
    
    echo ""
    echo "数据库:"
    if [ -f "qinglong_stock_data.db" ]; then
        size=$(ls -lh qinglong_stock_data.db | awk '{print $5}')
        echo "  ✅ qinglong_stock_data.db ($size)"
    else
        echo "  ⚠️  数据库不存在"
    fi
    
    echo ""
    echo "Chrome 状态:"
    if curl -s http://localhost:9222/json/version >/dev/null 2>&1; then
        version=$(curl -s http://localhost:9222/json/version | grep -o '"Browser": "[^"]*"' | cut -d'"' -f4)
        echo "  🟢 运行中 ($version)"
    else
        echo "  🔴 未运行"
    fi
}

show_logs() {
    echo "📋 查看日志"
    echo "=========="
    echo ""
    
    cd "$PROJECT_DIR"
    
    if [ -d "logs" ] && [ "$(ls -A logs 2>/dev/null)" ]; then
        echo "可用日志文件:"
        ls -lt logs/*.log 2>/dev/null | head -5 | awk '{print "  " $9 " (" $5 ")"}'
        echo ""
        read -p "查看哪个日志? (输入文件名或按回车查看最新): " logfile
        
        if [ -z "$logfile" ]; then
            logfile=$(ls -t logs/*.log 2>/dev/null | head -1)
        fi
        
        if [ -f "$logfile" ]; then
            echo ""
            echo "=== $logfile ==="
            tail -50 "$logfile"
        else
            echo "文件不存在"
        fi
    else
        echo "暂无日志文件"
    fi
}

generate_report() {
    echo "📈 生成分析报告..."
    cd "$PROJECT_DIR"
    python3 chrome_mcp_analyzer.py
}

# 主循环
while true; do
    show_menu
    read -p "请输入选项 [0-7]: " choice
    
    case $choice in
        1) install_workflow ;;
        2) run_test ;;
        3) backup_workflow ;;
        4) rollback_workflow ;;
        5) show_status ;;
        6) show_logs ;;
        7) generate_report ;;
        0) echo "再见!"; exit 0 ;;
        *) echo "无效选项" ;;
    esac
    
    echo ""
    read -p "按回车键继续..."
    echo ""
done
