#!/usr/bin/env python3
"""
青龙资金流向分析模块 v4.1.0
东方财富API集成 - 北向资金、主力资金、散户资金分析
"""

import requests
import json
from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime
import re

@dataclass
class CapitalFlowData:
    """资金流向数据"""
    # 主力资金
    main_inflow: float  # 主力净流入
    main_inflow_percent: float  # 主力净流入占比
    main_buy: float  # 主力买入
    main_sell: float  # 主力卖出
    
    # 散户资金
    retail_inflow: float  # 散户净流入
    retail_inflow_percent: float  # 散户净流入占比
    retail_buy: float  # 散户买入
    retail_sell: float  # 散户卖出
    
    # 大单/小单
    large_order_inflow: float  # 大单净流入
    medium_order_inflow: float  # 中单净流入
    small_order_inflow: float  # 小单净流入
    
    # 历史数据
    main_flow_history: List[Dict]  # 主力历史净流入
    
    # 北向资金 (沪深港通)
    northbound_inflow: Optional[float] = None  # 北向净流入
    northbound_hold_percent: Optional[float] = None  # 北向持股占比
    
    # 融资融券
    margin_balance: Optional[float] = None  # 融资余额
    margin_inflow: Optional[float] = None  # 融资净流入


class EastMoneyAPI:
    """东方财富API封装"""
    
    BASE_URL = "http://push2.eastmoney.com/api/qt/stock/get"
    
    # 字段映射 (东方财富字段代码)
    FIELDS = {
        # 基础数据
        "price": "f43",  # 最新价
        "open": "f44",
        "high": "f45",
        "low": "f46",
        "volume": "f47",
        "turnover": "f48",
        "name": "f58",
        "code": "f57",
        "prev_close": "f60",
        
        # 资金流向 (主力/散户)
        "main_net_inflow": "f136",  # 主力净流入
        "main_buy": "f137",  # 主力买入
        "main_sell": "f138",  # 主力卖出
        "retail_net_inflow": "f139",  # 散户净流入
        "retail_buy": "f140",  # 散户买入
        "retail_sell": "f141",  # 散户卖出
        
        # 大单/中单/小单
        "large_order": "f142",  # 大单净流入
        "medium_order": "f143",  # 中单净流入
        "small_order": "f144",  # 小单净流入
        
        # 主力历史数据 (JSON格式)
        "main_flow_history": "f178",
        
        # 北向资金
        "northbound_inflow": "f184",  # 北向净流入
        "northbound_hold": "f185",  # 北向持股数量
        "northbound_percent": "f186",  # 北向持股占比
        
        # 融资融券
        "margin_balance": "f187",  # 融资余额
        "margin_buy": "f188",  # 融资买入
        "margin_repay": "f189",  # 融资偿还
        
        # 其他指标
        "turnover_rate": "f168",  # 换手率
        "pe_ratio": "f162",  # 市盈率
        "pb_ratio": "f167",  # 市净率
        "market_cap": "f116",  # 总市值
        "sector": "f127",  # 所属行业
        "region": "f128",  # 所属地区
        "concepts": "f129",  # 概念题材
    }
    
    @classmethod
    def get_stock_code_prefix(cls, code: str) -> str:
        """获取股票代码前缀 (1=上证, 0=深证)"""
        if code.startswith("sh"):
            return "1"
        elif code.startswith("sz"):
            return "0"
        elif code.startswith("bj"):
            return "0"  # 北交所
        else:
            # 根据代码判断
            num_code = code.replace("sh", "").replace("sz", "").replace("bj", "")
            if num_code.startswith("6"):
                return "1"
            else:
                return "0"
    
    @classmethod
    def fetch_stock_data(cls, code: str) -> Optional[Dict]:
        """获取股票完整数据"""
        try:
            prefix = cls.get_stock_code_prefix(code)
            clean_code = code.replace("sh", "").replace("sz", "").replace("bj", "")
            secid = f"{prefix}.{clean_code}"
            
            # 获取所有字段
            fields = ",".join(cls.FIELDS.values())
            url = f"{cls.BASE_URL}?secid={secid}&fields={fields}"
            
            response = requests.get(url, timeout=10)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                data = response.json()
                if data.get("rc") == 0 and data.get("data"):
                    return data["data"]
            return None
        except Exception as e:
            print(f"Error fetching EastMoney data: {e}")
            return None


class CapitalFlowAnalyzer:
    """资金流向分析器"""
    
    def __init__(self):
        self.api = EastMoneyAPI()
    
    def analyze(self, code: str) -> Optional[CapitalFlowData]:
        """分析资金流向"""
        raw_data = self.api.fetch_stock_data(code)
        if not raw_data:
            return None
        
        F = self.api.FIELDS
        
        # 解析主力历史数据 (JSON字符串)
        main_history = []
        history_str = raw_data.get(F["main_flow_history"], "[]")
        try:
            main_history = json.loads(history_str) if history_str else []
        except:
            main_history = []
        
        # 获取成交额用于计算占比
        turnover = float(raw_data.get(F["turnover"], 0) or 0)
        
        # 主力资金
        main_inflow = float(raw_data.get(F["main_net_inflow"], 0) or 0)
        main_buy = float(raw_data.get(F["main_buy"], 0) or 0)
        main_sell = float(raw_data.get(F["main_sell"], 0) or 0)
        main_percent = (main_inflow / turnover * 100) if turnover > 0 else 0
        
        # 散户资金
        retail_inflow = float(raw_data.get(F["retail_net_inflow"], 0) or 0)
        retail_buy = float(raw_data.get(F["retail_buy"], 0) or 0)
        retail_sell = float(raw_data.get(F["retail_sell"], 0) or 0)
        retail_percent = (retail_inflow / turnover * 100) if turnover > 0 else 0
        
        # 大单/中单/小单
        large_order = float(raw_data.get(F["large_order"], 0) or 0)
        medium_order = float(raw_data.get(F["medium_order"], 0) or 0)
        small_order = float(raw_data.get(F["small_order"], 0) or 0)
        
        # 北向资金
        northbound_inflow = raw_data.get(F["northbound_inflow"])
        northbound_percent = raw_data.get(F["northbound_percent"])
        
        # 融资融券
        margin_balance = raw_data.get(F["margin_balance"])
        
        return CapitalFlowData(
            main_inflow=main_inflow,
            main_inflow_percent=round(main_percent, 2),
            main_buy=main_buy,
            main_sell=main_sell,
            retail_inflow=retail_inflow,
            retail_inflow_percent=round(retail_percent, 2),
            retail_buy=retail_buy,
            retail_sell=retail_sell,
            large_order_inflow=large_order,
            medium_order_inflow=medium_order,
            small_order_inflow=small_order,
            main_flow_history=main_history,
            northbound_inflow=float(northbound_inflow) if northbound_inflow else None,
            northbound_hold_percent=float(northbound_percent) if northbound_percent else None,
            margin_balance=float(margin_balance) if margin_balance else None,
        )
    
    def calculate_flow_score(self, flow_data: CapitalFlowData) -> Dict:
        """计算资金流向评分"""
        score = 50  # 基础分
        signals = []
        
        # 1. 主力资金评分 (40分)
        if flow_data.main_inflow > 0:
            score += min(20, flow_data.main_inflow_percent * 2)
            signals.append(f"主力净流入 {flow_data.main_inflow_percent:.1f}%")
        else:
            score -= min(20, abs(flow_data.main_inflow_percent) * 2)
            signals.append(f"主力净流出 {abs(flow_data.main_inflow_percent):.1f}%")
        
        # 2. 散户反向指标 (20分)
        # 散户卖出 = 机构可能买入 (反向指标)
        if flow_data.retail_inflow < 0:
            score += 10
            signals.append("散户净流出 (正向)")
        else:
            score -= 10
            signals.append("散户净流入 (负向)")
        
        # 3. 大单动向 (20分)
        if flow_data.large_order_inflow > 0:
            score += 15
            signals.append("大单净流入")
        else:
            score -= 10
            signals.append("大单净流出")
        
        # 4. 北向资金 (20分)
        if flow_data.northbound_inflow is not None:
            if flow_data.northbound_inflow > 0:
                score += 15
                signals.append("北向资金净流入")
            else:
                score -= 10
                signals.append("北向资金净流出")
        
        # 限制分数范围
        score = max(0, min(100, score))
        
        # 确定等级
        if score >= 80:
            level = "强烈看多"
        elif score >= 60:
            level = "看多"
        elif score >= 40:
            level = "中性"
        elif score >= 20:
            level = "看空"
        else:
            level = "强烈看空"
        
        return {
            "score": round(score, 1),
            "level": level,
            "signals": signals,
            "main_force_trend": "流入" if flow_data.main_inflow > 0 else "流出",
            "retail_force_trend": "流入" if flow_data.retail_inflow > 0 else "流出",
            "smart_money_agreement": flow_data.main_inflow > 0 and flow_data.retail_inflow < 0
        }


# 测试代码
if __name__ == "__main__":
    analyzer = CapitalFlowAnalyzer()
    
    # 测试华胜天成
    print("=" * 50)
    print("测试: 华胜天成 (sh600410)")
    print("=" * 50)
    
    result = analyzer.analyze("sh600410")
    if result:
        print(f"主力净流入: {result.main_inflow:,.0f} ({result.main_inflow_percent}%)")
        print(f"散户净流入: {result.retail_inflow:,.0f} ({result.retail_inflow_percent}%)")
        print(f"大单净流入: {result.large_order_inflow:,.0f}")
        print(f"北向持股占比: {result.northbound_hold_percent}%" if result.northbound_hold_percent else "北向数据: 无")
        
        score = analyzer.calculate_flow_score(result)
        print(f"\n资金流向评分: {score['score']} - {score['level']}")
        print(f"信号: {', '.join(score['signals'])}")
    else:
        print("获取数据失败")
