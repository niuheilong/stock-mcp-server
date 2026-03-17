#!/usr/bin/env python3
"""
青龙预警系统 v4.4.0
价格预警 + 情绪预警 + 资金流向预警 + 板块异动预警
"""

import json
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import threading
import time


class AlertType(str, Enum):
    """预警类型"""
    PRICE_CHANGE = "price_change"  # 价格涨跌幅
    PRICE_THRESHOLD = "price_threshold"  # 价格突破
    VOLUME_SPIKE = "volume_spike"  # 成交量异动
    SENTIMENT_EXTREME = "sentiment_extreme"  # 情绪极值
    FLOW_DIVERGENCE = "flow_divergence"  # 资金流向背离
    SECTOR_LEADER = "sector_leader"  # 板块龙头
    SCORE_CHANGE = "score_change"  # 评分变化
    TECH_SIGNAL = "tech_signal"  # 技术信号


class AlertLevel(str, Enum):
    """预警等级"""
    INFO = "info"  # 提示
    WARNING = "warning"  # 警告
    CRITICAL = "critical"  # 严重


@dataclass
class AlertRule:
    """预警规则"""
    id: str  # 规则ID
    name: str  # 规则名称
    code: str  # 股票代码
    alert_type: AlertType  # 预警类型
    level: AlertLevel  # 预警等级
    
    # 阈值配置
    threshold_value: float  # 阈值
    threshold_direction: str  # 方向: "above", "below", "change"
    
    # 可选配置
    cooldown_minutes: int = 60  # 冷却时间(分钟)
    enabled: bool = True  # 是否启用
    
    # 元数据
    description: str = ""  # 描述
    created_at: str = ""  # 创建时间
    
    # 运行时状态
    last_triggered: Optional[str] = None  # 上次触发时间
    trigger_count: int = 0  # 触发次数


@dataclass
class AlertEvent:
    """预警事件"""
    id: str  # 事件ID
    rule_id: str  # 规则ID
    code: str  # 股票代码
    name: str  # 股票名称
    alert_type: AlertType  # 预警类型
    level: AlertLevel  # 预警等级
    
    # 触发数据
    trigger_value: float  # 触发值
    threshold_value: float  # 阈值
    current_data: Dict  # 当前数据快照
    
    # 时间信息
    timestamp: str  # 触发时间
    message: str  # 预警消息


class AlertEngine:
    """预警引擎"""
    
    def __init__(self):
        self.rules: Dict[str, AlertRule] = {}  # 规则存储
        self.events: List[AlertEvent] = []  # 事件历史
        self.handlers: List[Callable] = []  # 通知处理器
        self._lock = threading.Lock()
    
    def add_rule(self, rule: AlertRule) -> str:
        """添加预警规则"""
        with self._lock:
            if not rule.created_at:
                rule.created_at = datetime.now().isoformat()
            self.rules[rule.id] = rule
            return rule.id
    
    def remove_rule(self, rule_id: str) -> bool:
        """删除预警规则"""
        with self._lock:
            if rule_id in self.rules:
                del self.rules[rule_id]
                return True
            return False
    
    def get_rules(self, code: str = None, enabled_only: bool = True) -> List[AlertRule]:
        """获取预警规则"""
        rules = list(self.rules.values())
        
        if code:
            rules = [r for r in rules if r.code == code]
        
        if enabled_only:
            rules = [r for r in rules if r.enabled]
        
        return rules
    
    def add_handler(self, handler: Callable):
        """添加通知处理器"""
        self.handlers.append(handler)
    
    def check_alerts(self, code: str, data: Dict) -> List[AlertEvent]:
        """检查预警条件"""
        triggered = []
        
        rules = self.get_rules(code=code)
        
        for rule in rules:
            event = self._check_rule(rule, data)
            if event:
                triggered.append(event)
                self._trigger_alert(event)
        
        return triggered
    
    def _check_rule(self, rule: AlertRule, data: Dict) -> Optional[AlertEvent]:
        """检查单个规则"""
        # 检查冷却时间
        if rule.last_triggered:
            last = datetime.fromisoformat(rule.last_triggered)
            cooldown = timedelta(minutes=rule.cooldown_minutes)
            if datetime.now() - last < cooldown:
                return None
        
        # 获取当前值
        current_value = self._get_value_for_rule(rule, data)
        if current_value is None:
            return None
        
        # 检查阈值条件
        triggered = False
        
        if rule.threshold_direction == "above":
            triggered = current_value >= rule.threshold_value
        elif rule.threshold_direction == "below":
            triggered = current_value <= rule.threshold_value
        elif rule.threshold_direction == "change":
            # 变化幅度检查
            triggered = abs(current_value) >= abs(rule.threshold_value)
        
        if not triggered:
            return None
        
        # 创建预警事件
        event = AlertEvent(
            id=f"{rule.id}_{datetime.now().timestamp()}",
            rule_id=rule.id,
            code=rule.code,
            name=data.get("name", ""),
            alert_type=rule.alert_type,
            level=rule.level,
            trigger_value=current_value,
            threshold_value=rule.threshold_value,
            current_data=data,
            timestamp=datetime.now().isoformat(),
            message=self._generate_message(rule, current_value, data)
        )
        
        # 更新规则状态
        rule.last_triggered = event.timestamp
        rule.trigger_count += 1
        
        return event
    
    def _get_value_for_rule(self, rule: AlertRule, data: Dict) -> Optional[float]:
        """根据规则类型获取对应数据值"""
        alert_type = rule.alert_type
        
        if alert_type == AlertType.PRICE_CHANGE:
            return data.get("change_percent")
        
        elif alert_type == AlertType.PRICE_THRESHOLD:
            return data.get("price")
        
        elif alert_type == AlertType.VOLUME_SPIKE:
            volume = data.get("volume", 0)
            avg_volume = data.get("avg_volume", 1)
            return (volume / avg_volume - 1) * 100 if avg_volume > 0 else 0
        
        elif alert_type == AlertType.SENTIMENT_EXTREME:
            return data.get("sentiment_score", 50)
        
        elif alert_type == AlertType.FLOW_DIVERGENCE:
            return data.get("flow_score", 50)
        
        elif alert_type == AlertType.SECTOR_LEADER:
            return data.get("sector_rank", 999)
        
        elif alert_type == AlertType.SCORE_CHANGE:
            return data.get("qinglong_score", 50)
        
        elif alert_type == AlertType.TECH_SIGNAL:
            rsi = data.get("rsi", 50)
            return rsi
        
        return None
    
    def _generate_message(self, rule: AlertRule, value: float, data: Dict) -> str:
        """生成预警消息"""
        name = data.get("name", rule.code)
        
        messages = {
            AlertType.PRICE_CHANGE: f"{name} 价格变动 {value:+.2f}%",
            AlertType.PRICE_THRESHOLD: f"{name} 价格达到 {value:.2f}",
            AlertType.VOLUME_SPIKE: f"{name} 成交量异动 {value:+.1f}%",
            AlertType.SENTIMENT_EXTREME: f"{name} 情绪极值 {value:.1f}",
            AlertType.FLOW_DIVERGENCE: f"{name} 资金流向异常 {value:.1f}",
            AlertType.SECTOR_LEADER: f"{name} 成为板块龙头 (排名{int(value)})",
            AlertType.SCORE_CHANGE: f"{name} 青龙评分变化至 {value:.1f}",
            AlertType.TECH_SIGNAL: f"{name} 技术信号 RSI={value:.1f}",
        }
        
        return messages.get(rule.alert_type, f"{name} 触发预警: {value}")
    
    def _trigger_alert(self, event: AlertEvent):
        """触发预警通知"""
        # 保存事件
        self.events.append(event)
        
        # 调用所有处理器
        for handler in self.handlers:
            try:
                handler(event)
            except Exception as e:
                print(f"Alert handler error: {e}")
    
    def get_events(self, code: str = None, limit: int = 100) -> List[AlertEvent]:
        """获取预警事件历史"""
        events = self.events
        
        if code:
            events = [e for e in events if e.code == code]
        
        # 按时间倒序
        events = sorted(events, key=lambda x: x.timestamp, reverse=True)
        
        return events[:limit]
    
    def export_rules(self) -> str:
        """导出规则为JSON"""
        rules_dict = {k: asdict(v) for k, v in self.rules.items()}
        return json.dumps(rules_dict, indent=2, ensure_ascii=False)
    
    def import_rules(self, json_str: str):
        """从JSON导入规则"""
        rules_dict = json.loads(json_str)
        for rule_id, rule_data in rules_dict.items():
            rule = AlertRule(**rule_data)
            self.rules[rule_id] = rule


# 默认通知处理器
def console_alert_handler(event: AlertEvent):
    """控制台输出预警"""
    level_emoji = {
        AlertLevel.INFO: "ℹ️",
        AlertLevel.WARNING: "⚠️",
        AlertLevel.CRITICAL: "🚨"
    }
    
    emoji = level_emoji.get(event.level, "🔔")
    
    print(f"\n{emoji} [{event.level.upper()}] {event.alert_type.value}")
    print(f"   股票: {event.name} ({event.code})")
    print(f"   时间: {event.timestamp}")
    print(f"   消息: {event.message}")
    print(f"   触发值: {event.trigger_value:.2f} (阈值: {event.threshold_value})")
    print("-" * 50)


# 测试代码
if __name__ == "__main__":
    print("=" * 60)
    print("测试: 青龙预警系统")
    print("=" * 60)
    
    # 创建预警引擎
    engine = AlertEngine()
    
    # 添加控制台处理器
    engine.add_handler(console_alert_handler)
    
    # 添加测试规则
    rules = [
        AlertRule(
            id="price_up_5",
            name="价格上涨5%",
            code="sh600410",
            alert_type=AlertType.PRICE_CHANGE,
            level=AlertLevel.WARNING,
            threshold_value=5.0,
            threshold_direction="above",
            description="当价格上涨超过5%时预警"
        ),
        AlertRule(
            id="sentiment_extreme",
            name="情绪极值",
            code="sh600410",
            alert_type=AlertType.SENTIMENT_EXTREME,
            level=AlertLevel.INFO,
            threshold_value=80.0,
            threshold_direction="above",
            description="情绪指数超过80时预警"
        ),
        AlertRule(
            id="sector_leader",
            name="成为板块龙头",
            code="sh600410",
            alert_type=AlertType.SECTOR_LEADER,
            level=AlertLevel.CRITICAL,
            threshold_value=3.0,
            threshold_direction="below",
            description="成为板块前3名时预警"
        ),
    ]
    
    for rule in rules:
        engine.add_rule(rule)
        print(f"✅ 添加规则: {rule.name}")
    
    print(f"\n共添加 {len(rules)} 条预警规则\n")
    
    # 模拟数据检测
    test_data = {
        "name": "华胜天成",
        "price": 28.5,
        "change_percent": 6.5,
        "volume": 1000000,
        "avg_volume": 800000,
        "sentiment_score": 85,
        "flow_score": 70,
        "sector_rank": 2,
        "qinglong_score": 82,
        "rsi": 75
    }
    
    print("模拟检测数据:")
    print(f"  价格变动: {test_data['change_percent']}%")
    print(f"  情绪评分: {test_data['sentiment_score']}")
    print(f"  板块排名: {test_data['sector_rank']}")
    print("\n开始检测预警...\n")
    
    events = engine.check_alerts("sh600410", test_data)
    
    print(f"\n检测到 {len(events)} 条预警")
    
    # 显示规则状态
    print("\n" + "=" * 60)
    print("规则触发统计:")
    print("=" * 60)
    for rule in engine.get_rules():
        print(f"  {rule.name}: 触发 {rule.trigger_count} 次")
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)
