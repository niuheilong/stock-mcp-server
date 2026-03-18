#!/usr/bin/env python3
"""
系统健康监控模块
监控系统状态，及时预警和清理
"""

import os
import sys
import time
import psutil
from datetime import datetime
from typing import Dict, List
import json


class SystemHealthMonitor:
    """系统健康监控器"""
    
    def __init__(self, workspace_dir: str = None):
        self.workspace_dir = workspace_dir or os.path.expanduser("~/.openclaw/workspace")
        self.check_count = 0
        self.last_check = datetime.now()
        
        # 阈值配置
        self.thresholds = {
            "memory_percent": 80,      # 内存使用超过80%报警
            "disk_percent": 85,        # 磁盘使用超过85%报警
            "cpu_percent": 90,         # CPU使用超过90%报警
            "context_size_mb": 50,     # 上下文超过50MB报警
            "browser_idle_min": 10,    # 浏览器空闲10分钟关闭
        }
        
        # 警报记录
        self.alerts: List[Dict] = []
        
    def check_all(self) -> Dict:
        """执行所有检查"""
        self.check_count += 1
        self.last_check = datetime.now()
        
        results = {
            "timestamp": self.last_check.isoformat(),
            "check_count": self.check_count,
            "memory": self._check_memory(),
            "disk": self._check_disk(),
            "cpu": self._check_cpu(),
            "context": self._check_context_size(),
            "browser": self._check_browser(),
            "alerts": len(self.alerts),
        }
        
        # 检查是否有警报
        self._process_alerts(results)
        
        return results
        
    def _check_memory(self) -> Dict:
        """检查内存使用"""
        memory = psutil.virtual_memory()
        status = {
            "total_gb": memory.total / 1024 / 1024 / 1024,
            "used_gb": memory.used / 1024 / 1024 / 1024,
            "percent": memory.percent,
            "status": "ok" if memory.percent < self.thresholds["memory_percent"] else "warning"
        }
        
        if status["status"] == "warning":
            self._add_alert("memory", f"内存使用过高: {memory.percent}%")
            
        return status
        
    def _check_disk(self) -> Dict:
        """检查磁盘使用"""
        disk = psutil.disk_usage(self.workspace_dir)
        percent = (disk.used / disk.total) * 100
        
        status = {
            "total_gb": disk.total / 1024 / 1024 / 1024,
            "used_gb": disk.used / 1024 / 1024 / 1024,
            "percent": percent,
            "status": "ok" if percent < self.thresholds["disk_percent"] else "warning"
        }
        
        if status["status"] == "warning":
            self._add_alert("disk", f"磁盘使用过高: {percent:.1f}%")
            
        return status
        
    def _check_cpu(self) -> Dict:
        """检查CPU使用"""
        percent = psutil.cpu_percent(interval=1)
        
        status = {
            "percent": percent,
            "status": "ok" if percent < self.thresholds["cpu_percent"] else "warning"
        }
        
        if status["status"] == "warning":
            self._add_alert("cpu", f"CPU使用过高: {percent}%")
            
        return status
        
    def _check_context_size(self) -> Dict:
        """检查上下文大小"""
        # 估算上下文大小（通过内存中的对象）
        import gc
        context_size = 0
        
        for obj in gc.get_objects():
            try:
                context_size += sys.getsizeof(obj)
            except:
                pass
                
        context_mb = context_size / 1024 / 1024
        
        status = {
            "size_mb": context_mb,
            "status": "ok" if context_mb < self.thresholds["context_size_mb"] else "warning"
        }
        
        if status["status"] == "warning":
            self._add_alert("context", f"上下文过大: {context_mb:.1f}MB")
            
        return status
        
    def _check_browser(self) -> Dict:
        """检查浏览器状态"""
        try:
            from browser_manager import get_browser_manager
            manager = get_browser_manager()
            status = manager.get_status()
            
            if status["should_close"]:
                self._add_alert("browser", f"浏览器空闲 {status['idle_seconds']:.0f} 秒，建议关闭")
                
            return status
        except:
            return {"active": False, "status": "ok"}
            
    def _add_alert(self, alert_type: str, message: str):
        """添加警报"""
        alert = {
            "type": alert_type,
            "message": message,
            "timestamp": datetime.now().isoformat(),
        }
        self.alerts.append(alert)
        
        # 只保留最近20条警报
        if len(self.alerts) > 20:
            self.alerts = self.alerts[-20:]
            
    def _process_alerts(self, results: Dict):
        """处理警报"""
        warnings = []
        
        for key in ["memory", "disk", "cpu", "context"]:
            if results.get(key, {}).get("status") == "warning":
                warnings.append(f"{key}: {results[key]}")
                
        if warnings:
            print("⚠️ 系统健康警告:")
            for w in warnings:
                print(f"  - {w}")
                
    def get_recommendations(self) -> List[str]:
        """获取优化建议"""
        recommendations = []
        
        # 检查内存
        memory = psutil.virtual_memory()
        if memory.percent > 70:
            recommendations.append("建议重启会话释放内存")
            
        # 检查磁盘
        disk = psutil.disk_usage(self.workspace_dir)
        if (disk.used / disk.total) > 0.7:
            recommendations.append("建议清理磁盘空间")
            
        # 检查浏览器
        try:
            from browser_manager import get_browser_manager
            manager = get_browser_manager()
            if manager.should_close_browser():
                recommendations.append("建议关闭浏览器释放资源")
        except:
            pass
            
        # 检查运行时间
        uptime = time.time() - psutil.boot_time()
        if uptime > 4 * 3600:  # 4小时
            recommendations.append("系统运行时间较长，建议重启")
            
        return recommendations
        
    def print_report(self):
        """打印健康报告"""
        results = self.check_all()
        
        print("\n" + "="*60)
        print("📊 系统健康报告")
        print("="*60)
        print(f"检查时间: {results['timestamp']}")
        print(f"检查次数: {results['check_count']}")
        print()
        
        print("💾 内存:")
        print(f"  使用: {results['memory']['used_gb']:.1f}GB / {results['memory']['total_gb']:.1f}GB ({results['memory']['percent']}%)")
        print(f"  状态: {'✅ 正常' if results['memory']['status'] == 'ok' else '⚠️ 警告'}")
        print()
        
        print("💿 磁盘:")
        print(f"  使用: {results['disk']['used_gb']:.1f}GB / {results['disk']['total_gb']:.1f}GB ({results['disk']['percent']:.1f}%)")
        print(f"  状态: {'✅ 正常' if results['disk']['status'] == 'ok' else '⚠️ 警告'}")
        print()
        
        print("🔥 CPU:")
        print(f"  使用: {results['cpu']['percent']}%")
        print(f"  状态: {'✅ 正常' if results['cpu']['status'] == 'ok' else '⚠️ 警告'}")
        print()
        
        print("📄 上下文:")
        print(f"  大小: {results['context']['size_mb']:.1f}MB")
        print(f"  状态: {'✅ 正常' if results['context']['status'] == 'ok' else '⚠️ 警告'}")
        print()
        
        print("🌐 浏览器:")
        print(f"  状态: {'活跃' if results['browser'].get('active') else '已关闭'}")
        if results['browser'].get('active'):
            print(f"  空闲: {results['browser'].get('idle_seconds', 0):.0f}秒")
        print()
        
        # 建议
        recommendations = self.get_recommendations()
        if recommendations:
            print("💡 优化建议:")
            for rec in recommendations:
                print(f"  - {rec}")
        else:
            print("✅ 系统状态良好")
            
        print("="*60)


# 使用示例
if __name__ == "__main__":
    monitor = SystemHealthMonitor()
    monitor.print_report()
