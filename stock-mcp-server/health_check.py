#!/usr/bin/env python3
"""
简化版系统健康检查
不依赖外部库
"""

import os
import sys
import gc
from datetime import datetime


def check_system_health():
    """检查系统健康状态"""
    print("="*60)
    print("📊 青龙系统健康检查")
    print("="*60)
    print(f"检查时间: {datetime.now().isoformat()}")
    print()
    
    # 1. 检查工作区大小
    workspace = os.path.expanduser("~/.openclaw/workspace")
    if os.path.exists(workspace):
        total_size = 0
        file_count = 0
        large_files = []
        
        for root, dirs, files in os.walk(workspace):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    size = os.path.getsize(file_path)
                    total_size += size
                    file_count += 1
                    
                    if size > 10 * 1024 * 1024:  # 大于10MB
                        large_files.append((file_path, size))
                except:
                    pass
        
        print(f"📁 工作区: {workspace}")
        print(f"   总大小: {total_size / 1024 / 1024:.1f} MB")
        print(f"   文件数: {file_count}")
        print()
        
        # 显示大文件
        if large_files:
            print("⚠️  大文件 (>10MB):")
            for path, size in sorted(large_files, key=lambda x: x[1], reverse=True)[:5]:
                print(f"   - {os.path.basename(path)}: {size/1024/1024:.1f}MB")
            print()
    
    # 2. 检查内存使用（通过Python对象估算）
    gc.collect()
    object_count = len(gc.get_objects())
    print(f"🧠 Python对象数: {object_count:,}")
    print()
    
    # 3. 检查浏览器状态
    try:
        from browser_manager import get_browser_manager
        manager = get_browser_manager()
        status = manager.get_status()
        
        print(f"🌐 浏览器状态:")
        print(f"   运行中: {'是' if status['active'] else '否'}")
        if status['active']:
            print(f"   空闲时间: {status['idle_seconds']:.0f}秒")
            if status['should_close']:
                print("   ⚠️ 建议关闭浏览器释放资源")
        print()
    except ImportError:
        print("🌐 浏览器状态: 未加载管理模块")
        print()
    
    # 4. 检查项目文件
    project_dir = os.path.dirname(os.path.abspath(__file__))
    core_files = [
        'server.py',
        'capital_flow.py',
        'sector_analysis.py',
        'backtest.py',
        'alert_system.py',
        'resource_manager.py',
        'browser_manager.py',
        'health_monitor.py',
    ]
    
    print("📦 核心文件检查:")
    for file in core_files:
        path = os.path.join(project_dir, file)
        exists = os.path.exists(path)
        size = os.path.getsize(path) / 1024 if exists else 0
        status = "✅" if exists else "❌"
        print(f"   {status} {file} ({size:.1f}KB)")
    print()
    
    # 5. 给出建议
    print("💡 建议:")
    recommendations = []
    
    if total_size > 100 * 1024 * 1024:  # 100MB
        recommendations.append("工作区超过100MB，建议清理或压缩")
    
    if object_count > 500000:
        recommendations.append("Python对象过多，建议重启会话")
    
    try:
        if isinstance(status, dict) and status.get('active') and status.get('idle_seconds', 0) > 300:
            recommendations.append("浏览器空闲超过5分钟，建议关闭")
    except:
        pass
    
    if not recommendations:
        recommendations.append("系统状态良好")
    
    for rec in recommendations:
        print(f"   - {rec}")
    
    print()
    print("="*60)


if __name__ == "__main__":
    check_system_health()
