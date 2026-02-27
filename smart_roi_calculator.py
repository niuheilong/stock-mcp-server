#!/usr/bin/env python3
"""
Smart ROI Calculator - Stock MCP Server Integration
借鉴 bounty-hunter-skill 的 Smart ROI 思想
集成到 Stock MCP Server 作为核心功能
"""

import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from datetime import datetime


@dataclass
class StockOpportunity:
    """股票投资机会"""
    code: str
    name: str
    current_price: float
    strategy: str
    expected_return: float  # 预期收益率
    probability: float  # 成功概率 0-1
    risk_level: str  # low/medium/high
    time_horizon: str  # short/medium/long
    

@dataclass
class ROICalculation:
    """ROI 计算结果"""
    should_trade: bool
    roi_score: float
    expected_profit: float
    total_cost: float
    confidence: str
    rationale: str
    risk_adjusted_return: float
    recommendation: str


class SmartROICalculator:
    """
    智能 ROI 计算器
    核心算法借鉴 bounty-hunter-skill
    """
    
    # 阈值配置
    MIN_ROI_THRESHOLD = 1.5        # 最低 ROI 150%
    MIN_PROBABILITY = 0.6          # 最低成功率 60%
    MAX_RISK_ACCEPTANCE = 0.3      # 最大可接受风险 30%
    
    # 风险系数
    RISK_MULTIPLIERS = {
        "low": 1.0,
        "medium": 1.5,
        "high": 2.5
    }
    
    # 时间成本（元/小时）
    TIME_VALUE = 50
    
    def calculate(self, opp: StockOpportunity) -> ROICalculation:
        """
        计算投资 ROI
        
        Formula:
        ROI = (预期收益 × 成功概率) / (时间成本 + 资金成本 × 风险系数)
        
        借鉴 bounty-hunter-skill 的 Smart ROI 系统
        """
        # 1. 成本计算
        time_cost = self._calculate_time_cost(opp)
        capital_cost = self._calculate_capital_cost(opp)
        risk_multiplier = self.RISK_MULTIPLIERS.get(opp.risk_level, 2.0)
        
        total_cost = time_cost + capital_cost * risk_multiplier
        
        # 2. 收益计算
        expected_profit = self._calculate_expected_profit(opp)
        risk_adjusted_return = expected_profit * opp.probability
        
        # 3. ROI 计算
        roi_score = risk_adjusted_return / total_cost if total_cost > 0 else 0
        
        # 4. 决策判断
        should_trade = self._should_trade(opp, roi_score)
        
        # 5. 置信度和建议
        confidence = self._calculate_confidence(roi_score, opp.probability)
        rationale = self._generate_rationale(opp, roi_score)
        recommendation = self._generate_recommendation(opp, roi_score, should_trade)
        
        return ROICalculation(
            should_trade=should_trade,
            roi_score=round(roi_score, 2),
            expected_profit=round(expected_profit, 2),
            total_cost=round(total_cost, 2),
            confidence=confidence,
            rationale=rationale,
            risk_adjusted_return=round(risk_adjusted_return, 2),
            recommendation=recommendation
        )
    
    def _calculate_time_cost(self, opp: StockOpportunity) -> float:
        """计算时间成本"""
        time_multipliers = {
            "short": 0.5,   # 短期：半天
            "medium": 2.0,  # 中期：2天
            "long": 5.0     # 长期：5天
        }
        hours = time_multipliers.get(opp.time_horizon, 2.0)
        return hours * self.TIME_VALUE
    
    def _calculate_capital_cost(self, opp: StockOpportunity) -> float:
        """计算资金成本"""
        # 假设买入 1 手（100 股）
        position_value = opp.current_price * 100
        # 手续费 0.03%，印花税 0.1%（卖出）
        fee = position_value * 0.0003 * 2  # 买卖双向
        stamp_tax = position_value * 0.001  # 卖出时
        return fee + stamp_tax
    
    def _calculate_expected_profit(self, opp: StockOpportunity) -> float:
        """计算预期收益"""
        position_value = opp.current_price * 100
        return position_value * opp.expected_return
    
    def _should_trade(self, opp: StockOpportunity, roi: float) -> bool:
        """判断是否交易"""
        return (
            roi > self.MIN_ROI_THRESHOLD and
            opp.probability > self.MIN_PROBABILITY and
            opp.risk_level in ["low", "medium"]
        )
    
    def _calculate_confidence(self, roi: float, probability: float) -> str:
        """计算置信度"""
        score = roi * probability
        if score >= 3.0:
            return "极高"
        elif score >= 2.0:
            return "高"
        elif score >= 1.5:
            return "中"
        else:
            return "低"
    
    def _generate_rationale(self, opp: StockOpportunity, roi: float) -> str:
        """生成决策理由"""
        reasons = []
        
        if roi > 2.0:
            reasons.append(f"ROI优秀({roi:.1f})")
        elif roi > 1.5:
            reasons.append(f"ROI良好({roi:.1f})")
        
        if opp.probability > 0.8:
            reasons.append(f"成功率高({opp.probability:.0%})")
        elif opp.probability > 0.7:
            reasons.append(f"成功率较高({opp.probability:.0%})")
        
        if opp.risk_level == "low":
            reasons.append("风险低")
        elif opp.risk_level == "medium":
            reasons.append("风险可控")
        
        if opp.time_horizon == "short":
            reasons.append("短期见效")
        
        return "；".join(reasons) if reasons else "条件一般，谨慎参与"
    
    def _generate_recommendation(
        self, 
        opp: StockOpportunity, 
        roi: float, 
        should_trade: bool
    ) -> str:
        """生成交易建议"""
        if not should_trade:
            return "【观望】条件不满足，继续观察"
        
        if roi >= 3.0:
            return f"【强烈推荐】{opp.name}({opp.code}) ROI {roi:.1f}，建议重仓参与"
        elif roi >= 2.5:
            return f"【推荐】{opp.name}({opp.code}) ROI {roi:.1f}，建议积极参与"
        elif roi >= 2.0:
            return f"【建议参与】{opp.name}({opp.code}) ROI {roi:.1f}，可适度参与"
        else:
            return f"【轻仓尝试】{opp.name}({opp.code}) ROI {roi:.1f}，建议小仓位试单"
    
    def batch_calculate(
        self, 
        opportunities: List[StockOpportunity]
    ) -> List[Tuple[StockOpportunity, ROICalculation]]:
        """批量计算 ROI"""
        results = []
        for opp in opportunities:
            roi = self.calculate(opp)
            results.append((opp, roi))
        
        # 按 ROI 排序
        results.sort(key=lambda x: x[1].roi_score, reverse=True)
        return results


# MCP Tool 接口
class ROITool:
    """MCP Tool 封装"""
    
    def __init__(self):
        self.calculator = SmartROICalculator()
    
    def calculate_stock_roi(self, params: Dict) -> Dict:
        """
        MCP Tool: 计算股票 ROI
        
        参数:
        - code: 股票代码
        - name: 股票名称
        - price: 当前价格
        - strategy: 策略类型
        - expected_return: 预期收益率 (如 0.05 表示 5%)
        - probability: 成功概率 (0-1)
        - risk_level: 风险等级 (low/medium/high)
        - time_horizon: 时间周期 (short/medium/long)
        
        返回:
        - should_trade: 是否建议交易
        - roi_score: ROI 评分
        - confidence: 置信度
        - recommendation: 交易建议
        """
        try:
            opp = StockOpportunity(
                code=params["code"],
                name=params["name"],
                current_price=params["price"],
                strategy=params["strategy"],
                expected_return=params["expected_return"],
                probability=params["probability"],
                risk_level=params["risk_level"],
                time_horizon=params.get("time_horizon", "medium")
            )
            
            result = self.calculator.calculate(opp)
            
            return {
                "success": True,
                "data": {
                    "should_trade": result.should_trade,
                    "roi_score": result.roi_score,
                    "expected_profit": result.expected_profit,
                    "total_cost": result.total_cost,
                    "confidence": result.confidence,
                    "rationale": result.rationale,
                    "recommendation": result.recommendation
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def analyze_watchlist(self, watchlist: List[Dict]) -> Dict:
        """
        MCP Tool: 批量分析关注列表
        返回按 ROI 排序的交易建议
        """
        opportunities = []
        
        for item in watchlist:
            opp = StockOpportunity(
                code=item["code"],
                name=item["name"],
                current_price=item["price"],
                strategy=item["strategy"],
                expected_return=item["expected_return"],
                probability=item["probability"],
                risk_level=item["risk_level"],
                time_horizon=item.get("time_horizon", "medium")
            )
            opportunities.append(opp)
        
        results = self.calculator.batch_calculate(opportunities)
        
        return {
            "success": True,
            "data": [
                {
                    "stock": {
                        "code": opp.code,
                        "name": opp.name,
                        "price": opp.current_price
                    },
                    "roi": {
                        "score": roi.roi_score,
                        "should_trade": roi.should_trade,
                        "confidence": roi.confidence,
                        "recommendation": roi.recommendation
                    }
                }
                for opp, roi in results
            ]
        }


# 全局实例
_roi_tool = None

def get_roi_tool() -> ROITool:
    """获取 ROI 工具实例"""
    global _roi_tool
    if _roi_tool is None:
        _roi_tool = ROITool()
    return _roi_tool


# 便捷函数
def calculate_roi(**kwargs) -> Dict:
    """便捷函数：计算单只股票 ROI"""
    tool = get_roi_tool()
    return tool.calculate_stock_roi(kwargs)


def analyze_batch(watchlist: List[Dict]) -> Dict:
    """便捷函数：批量分析"""
    tool = get_roi_tool()
    return tool.analyze_watchlist(watchlist)


# 测试
if __name__ == "__main__":
    print("🚀 Smart ROI Calculator - 集成测试")
    print("=" * 60)
    
    # 测试单只股票
    result = calculate_roi(
        code="002156",
        name="通富微电",
        price=52.01,
        strategy="趋势跟踪",
        expected_return=0.08,
        probability=0.75,
        risk_level="medium",
        time_horizon="short"
    )
    
    print("\n📊 单股 ROI 分析:")
    print(f"股票: 通富微电(002156)")
    print(f"ROI评分: {result['data']['roi_score']}")
    print(f"置信度: {result['data']['confidence']}")
    print(f"建议: {result['data']['recommendation']}")
    print(f"理由: {result['data']['rationale']}")
    
    # 批量测试
    watchlist = [
        {"code": "002156", "name": "通富微电", "price": 52.01, "strategy": "趋势跟踪", "expected_return": 0.08, "probability": 0.75, "risk_level": "medium"},
        {"code": "003029", "name": "金富科技", "price": 15.85, "strategy": "突破买入", "expected_return": 0.05, "probability": 0.70, "risk_level": "low"},
        {"code": "300058", "name": "蓝色光标", "price": 12.30, "strategy": "反弹", "expected_return": 0.03, "probability": 0.55, "risk_level": "high"},
    ]
    
    batch_result = analyze_batch(watchlist)
    
    print("\n📈 批量分析结果 (按 ROI 排序):")
    print("-" * 60)
    for item in batch_result["data"]:
        print(f"{item['stock']['name']}: ROI {item['roi']['score']} - {item['roi']['recommendation'][:20]}...")
    
    print("\n" + "=" * 60)
    print("✅ Smart ROI 系统已就绪！")
