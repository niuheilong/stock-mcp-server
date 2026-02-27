#!/usr/bin/env python3
"""
Evolver & EvoMap 监控系统
防止遗忘的关键任务监控器
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List


class EvolutionMonitor:
    """进化监控器"""
    
    def __init__(self):
        self.state_file = os.path.expanduser("~/.openclaw/workspace/evolution_state.json")
        self.checklist = {
            "evolver": {
                "name": "能力进化器 (Evolver)",
                "frequency": "daily",
                "last_check": None,
                "status": "pending",
                "action": "检查进化日志，应用改进"
            },
            "evomap": {
                "name": "EvoMap 胶囊发布",
                "frequency": "weekly",
                "last_check": None,
                "status": "pending", 
                "action": "发布股票数据服务胶囊"
            },
            "awesome_mcp": {
                "name": "awesome-mcp-servers PR",
                "frequency": "daily",
                "last_check": None,
                "status": "pending",
                "action": "检查 PR #2463 审核状态"
            },
            "stock_server": {
                "name": "Stock MCP Server维护",
                "frequency": "daily",
                "last_check": None,
                "status": "active",
                "action": "监控运行状态，处理Issue"
            }
        }
        self._load_state()
    
    def _load_state(self):
        """加载状态"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    saved_state = json.load(f)
                    self.checklist.update(saved_state)
            except:
                pass
    
    def _save_state(self):
        """保存状态"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.checklist, f, indent=2)
        except Exception as e:
            print(f"保存状态失败: {e}")
    
    def check_all(self) -> Dict:
        """检查所有任务"""
        now = datetime.now()
        alerts = []
        
        for key, task in self.checklist.items():
            last_check = task.get("last_check")
            if last_check:
                last = datetime.fromisoformat(last_check)
                days_since = (now - last).days
                
                if task["frequency"] == "daily" and days_since >= 1:
                    alerts.append({
                        "task": key,
                        "name": task["name"],
                        "days_overdue": days_since,
                        "action": task["action"]
                    })
                elif task["frequency"] == "weekly" and days_since >= 7:
                    alerts.append({
                        "task": key,
                        "name": task["name"],
                        "days_overdue": days_since,
                        "action": task["action"]
                    })
            else:
                # 从未检查
                alerts.append({
                    "task": key,
                    "name": task["name"],
                    "days_overdue": 999,
                    "action": task["action"]
                })
        
        return {
            "timestamp": now.isoformat(),
            "alerts": alerts,
            "total_tasks": len(self.checklist),
            "overdue_tasks": len(alerts)
        }
    
    def mark_checked(self, task_key: str):
        """标记任务已检查"""
        if task_key in self.checklist:
            self.checklist[task_key]["last_check"] = datetime.now().isoformat()
            self.checklist[task_key]["status"] = "checked"
            self._save_state()
    
    def generate_report(self) -> str:
        """生成监控报告"""
        result = self.check_all()
        alerts = result["alerts"]
        
        lines = [
            "=" * 70,
            "🚨 进化监控报告 - 防止遗忘系统",
            "=" * 70,
            f"生成时间: {result['timestamp']}",
            f"总任务数: {result['total_tasks']}",
            f"待处理任务: {result['overdue_tasks']}",
            "",
        ]
        
        if alerts:
            lines.append("⚠️ 需要关注的任务:")
            lines.append("-" * 70)
            for alert in alerts:
                lines.append(f"\n🔴 {alert['name']}")
                lines.append(f"   逾期: {alert['days_overdue']} 天")
                lines.append(f"   行动: {alert['action']}")
        else:
            lines.append("✅ 所有任务正常，无逾期")
        
        lines.extend([
            "",
            "=" * 70,
            "💡 建议:",
            "1. 每天检查 Evolver 日志并应用改进",
            "2. 每周发布 EvoMap 胶囊",
            "3. 关注 awesome-mcp-servers PR 审核",
            "4. 维护 Stock MCP Server 稳定性",
            "",
        ])
        
        return "\n".join(lines)


# 全局监控器
_monitor = None

def get_monitor() -> EvolutionMonitor:
    """获取监控器"""
    global _monitor
    if _monitor is None:
        _monitor = EvolutionMonitor()
    return _monitor


if __name__ == "__main__":
    monitor = get_monitor()
    report = monitor.generate_report()
    print(report)
    
    # 保存报告
    report_file = "/tmp/evolution_monitor_report.txt"
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"\n📄 报告已保存: {report_file}")
