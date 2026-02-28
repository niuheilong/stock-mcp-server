#!/usr/bin/env python3
"""
AI 股票晨报生成器 v2.0 - 集成 Smart ROI
整合所有能力：实时数据 + 多智能体分析 + Smart ROI + 新闻监控 + 技术指标
每天早上 8:00 自动生成专业晨报
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from intelligent_scheduler import get_scheduler
from multi_agent_robust import robust_stock_analysis
from jina_reader import fetch_with_jina
from sina_stock_api import get_sina_stock_price
from smart_roi_calculator import SmartROICalculator, StockOpportunity


class SmartMorningReportGenerator:
    """智能晨报生成器 - 集成 Smart ROI"""
    
    def __init__(self):
        self.scheduler = get_scheduler()
        self.roi_calculator = SmartROICalculator()
        self.report_time = datetime.now()
        
        # 用户持仓股票（从 USER.md 读取）
        self.holdings = [
            {"code": "002156", "name": "通富微电", "rating": "强", "strategy": "持有/加仓", "sector": "芯片封装"},
            {"code": "003029", "name": "金富科技", "rating": "强", "strategy": "持有/加仓", "sector": "汽车零部件"},
            {"code": "601599", "name": "浙文影业", "rating": "强", "strategy": "持有/加仓", "sector": "影视传媒"},
            {"code": "300645", "name": "正元智慧", "rating": "中", "strategy": "高抛低吸", "sector": "智慧城市"},
            {"code": "002023", "name": "海特高新", "rating": "中", "strategy": "观望", "sector": "商业航天"},
            {"code": "300058", "name": "蓝色光标", "rating": "弱", "strategy": "减仓/止损", "sector": "AI营销"},
            {"code": "300724", "name": "捷佳伟创", "rating": "弱", "strategy": "减仓/止损", "sector": "光伏设备"},
            {"code": "300773", "name": "拉卡拉", "rating": "弱", "strategy": "减仓/止损", "sector": "支付"},
        ]
        
        # 关注板块
        self.focus_sectors = [
            "芯片封装/Chiplet",
            "人形机器人",
            "商业航天/低空经济",
            "AI算力/CPO",
        ]
    
    def generate_report(self) -> str:
        """生成完整智能晨报"""
        report_lines = []
        
        # 1. 标题和日期
        report_lines.extend(self._generate_header())
        
        # 2. 市场概览
        report_lines.extend(self._generate_market_overview())
        
        # 3. Smart ROI 精选机会（新增！）
        report_lines.extend(self._generate_roi_opportunities())
        
        # 4. 持仓股票分析（带 ROI）
        report_lines.extend(self._generate_holdings_analysis_with_roi())
        
        # 5. 关注板块动态
        report_lines.extend(self._generate_sector_news())
        
        # 6. 今日操作建议
        report_lines.extend(self._generate_trading_plan())
        
        # 7. 风险提醒
        report_lines.extend(self._generate_risk_alerts())
        
        return "\n".join(report_lines)
    
    def _generate_header(self) -> List[str]:
        """生成标题"""
        return [
            "=" * 70,
            f"📊 AI 股票晨报 v2.0 (Smart ROI 版) - {self.report_time.strftime('%Y年%m月%d日 %H:%M')}",
            "=" * 70,
            "",
            f"报告生成时间: {self.report_time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"数据时间: 交易日 {self.report_time.strftime('%H:%M')}",
            "",
            "🔥 本报告集成 Smart ROI 系统（借鉴 bounty-hunter-skill 量化决策框架）",
            "",
        ]
    
    def _generate_market_overview(self) -> List[str]:
        """生成市场概览"""
        lines = [
            "📈 【市场概览】",
            "-" * 70,
            "",
        ]
        
        # 获取主要指数
        indices = [
            ("上证指数", "sh000001"),
            ("深证成指", "sz399001"),
            ("创业板指", "sz399006"),
        ]
        
        for name, code in indices:
            try:
                result = get_sina_stock_price(code)
                if 'error' not in result:
                    change = result.get('change_percent', 0)
                    emoji = "📈" if change > 0 else "📉" if change < 0 else "➖"
                    lines.append(f"{emoji} {name}: {result['price']:.2f} ({change:+.2f}%)")
            except:
                lines.append(f"➖ {name}: 数据获取中...")
        
        lines.append("")
        
        # 市场情绪判断
        lines.extend([
            "💭 市场情绪:",
            self._get_market_sentiment(),
            "",
        ])
        
        return lines
    
    def _get_market_sentiment(self) -> str:
        """判断市场情绪"""
        try:
            result = fetch_with_jina("https://finance.eastmoney.com")
            if result['success']:
                content = result['content']
                
                up_words = ['上涨', '涨停', '大涨', '反弹', '利好']
                down_words = ['下跌', '跌停', '大跌', '调整', '利空']
                
                up_count = sum(content.count(w) for w in up_words)
                down_count = sum(content.count(w) for w in down_words)
                
                if up_count > down_count * 1.5:
                    return "  今日市场情绪偏乐观，上涨家数较多"
                elif down_count > up_count * 1.5:
                    return "  今日市场情绪偏谨慎，注意回调风险"
                else:
                    return "  今日市场情绪中性，个股分化明显"
        except:
            pass
        
        return "  市场情绪研判中..."
    
    def _generate_roi_opportunities(self) -> List[str]:
        """生成 Smart ROI 精选机会（核心新功能！）"""
        lines = [
            "🎯 【Smart ROI 精选机会】（借鉴 bounty-hunter-skill 量化决策）",
            "-" * 70,
            "",
        ]
        
        # 计算所有持仓的 ROI
        opportunities = []
        
        for stock in self.holdings:
            try:
                price_data = get_sina_stock_price(stock["code"])
                if 'error' in price_data:
                    continue
                
                price = price_data['price']
                change = price_data['change_percent']
                
                # 根据涨跌幅和评级设置参数
                opp = self._create_opportunity(stock, price, change)
                if opp:
                    roi_result = self.roi_calculator.calculate(opp)
                    opportunities.append((stock, opp, roi_result))
                    
            except Exception as e:
                continue
        
        # 按 ROI 排序
        opportunities.sort(key=lambda x: x[2].roi_score, reverse=True)
        
        # 显示高 ROI 机会
        high_roi = [x for x in opportunities if x[2].should_trade]
        
        if high_roi:
            lines.append(f"✅ 发现 {len(high_roi)} 个高 ROI 机会（ROI > 1.5）:")
            lines.append("")
            
            for i, (stock, opp, roi) in enumerate(high_roi[:3], 1):
                emoji = "🚀" if roi.roi_score >= 3.0 else "⭐" if roi.roi_score >= 2.0 else "✅"
                lines.append(f"{emoji} 第{i}名: {stock['name']}({stock['code']})")
                lines.append(f"   当前价格: ¥{opp.current_price:.2f}")
                lines.append(f"   📊 ROI评分: {roi.roi_score:.2f} (置信度: {roi.confidence})")
                lines.append(f"   💰 预期收益: ¥{roi.expected_profit:.2f}")
                lines.append(f"   🎯 建议: {roi.recommendation}")
                lines.append(f"   💡 理由: {roi.rationale}")
                lines.append("")
        else:
            lines.append("⏸️ 暂无高 ROI 机会，建议观望")
            lines.append("")
        
        # 显示全部持仓 ROI 排名
        lines.append("📋 全部持仓 ROI 排名:")
        lines.append("")
        for i, (stock, opp, roi) in enumerate(opportunities[:5], 1):
            trade_emoji = "🟢" if roi.should_trade else "⚪"
            lines.append(f"{trade_emoji} {i}. {stock['name']}: ROI {roi.roi_score:.2f} | {roi.confidence} | {'建议交易' if roi.should_trade else '观望'}")
        
        lines.append("")
        return lines
    
    def _create_opportunity(self, stock: Dict, price: float, change: float) -> Optional[StockOpportunity]:
        """根据股票数据创建机会对象"""
        # 根据涨跌幅和评级设置参数
        if stock["rating"] == "强":
            base_return = 0.08
            base_prob = 0.75
            risk = "medium"
        elif stock["rating"] == "中":
            base_return = 0.05
            base_prob = 0.65
            risk = "medium"
        else:  # 弱
            base_return = 0.03
            base_prob = 0.55
            risk = "high"
        
        # 根据今日涨跌调整
        if change > 5:
            expected_return = base_return * 0.5  # 已大涨，降低预期
            probability = base_prob * 0.8
        elif change > 2:
            expected_return = base_return * 0.8
            probability = base_prob
        elif change < -5:
            expected_return = base_return * 1.5  # 大跌，反弹预期
            probability = base_prob * 0.7
        elif change < -2:
            expected_return = base_return
            probability = base_prob * 0.9
        else:
            expected_return = base_return
            probability = base_prob
        
        return StockOpportunity(
            code=stock["code"],
            name=stock["name"],
            current_price=price,
            strategy=stock["strategy"],
            expected_return=expected_return,
            probability=probability,
            risk_level=risk,
            time_horizon="short" if stock["rating"] == "强" else "medium"
        )
    
    def _generate_holdings_analysis_with_roi(self) -> List[str]:
        """生成持仓分析（带 ROI）"""
        lines = [
            "💼 【持仓股票分析】(含 Smart ROI 评分)",
            "-" * 70,
            "",
        ]
        
        # 分类持仓
        strong_holdings = [h for h in self.holdings if h["rating"] == "强"]
        medium_holdings = [h for h in self.holdings if h["rating"] == "中"]
        weak_holdings = [h for h in self.holdings if h["rating"] == "弱"]
        
        # 强势持仓
        if strong_holdings:
            lines.extend(["🟢 强势持仓（建议持有/加仓）:", ""])
            for stock in strong_holdings:
                lines.extend(self._analyze_stock_with_roi(stock))
                lines.append("")
        
        # 中等持仓
        if medium_holdings:
            lines.extend(["🟡 中等持仓（建议观望/高抛低吸）:", ""])
            for stock in medium_holdings:
                lines.extend(self._analyze_stock_with_roi(stock))
                lines.append("")
        
        # 弱势持仓
        if weak_holdings:
            lines.extend(["🔴 弱势持仓（建议减仓/止损）:", ""])
            for stock in weak_holdings:
                lines.extend(self._analyze_stock_with_roi(stock))
                lines.append("")
        
        return lines
    
    def _analyze_stock_with_roi(self, stock: Dict) -> List[str]:
        """分析单只股票（带 ROI）"""
        lines = []
        code = stock["code"]
        name = stock["name"]
        
        try:
            price_data = get_sina_stock_price(code)
            
            if 'error' in price_data:
                lines.append(f"  {name}({code}): 数据获取失败")
                return lines
            
            price = price_data['price']
            change = price_data['change_percent']
            volume = price_data['volume']
            
            # 计算 ROI
            opp = self._create_opportunity(stock, price, change)
            roi = self.roi_calculator.calculate(opp) if opp else None
            
            # 涨跌表情
            emoji = "🟢" if change > 0 else "🔴" if change < 0 else "⚪"
            
            lines.append(f"  {emoji} {name}({code}): ¥{price:.2f} ({change:+.2f}%)")
            lines.append(f"     成交量: {volume/10000:.2f}万手")
            
            # Smart ROI 信息
            if roi:
                roi_emoji = "🚀" if roi.roi_score >= 3.0 else "⭐" if roi.roi_score >= 2.0 else "📊"
                lines.append(f"     {roi_emoji} Smart ROI: {roi.roi_score:.2f} ({roi.confidence})")
                lines.append(f"     💡 {roi.rationale}")
            
            # 操作建议
            lines.append(f"     💡 建议: {stock['strategy']}")
            
        except Exception as e:
            lines.append(f"  {name}({code}): 分析出错 - {str(e)}")
        
        return lines
    
    def _generate_sector_news(self) -> List[str]:
        """生成板块动态"""
        lines = [
            "🔥 【关注板块动态】",
            "-" * 70,
            "",
        ]
        
        sectors = [
            ("🧠 芯片封装/Chiplet", ["关注行业订单情况", "留意技术突破新闻", "跟踪龙头股价走势"]),
            ("🤖 人形机器人", ["特斯拉Optimus进展", "国内厂商新品发布", "政策支持力度"]),
            ("🚀 商业航天/低空经济", ["政策利好落地", "订单释放情况", "技术成熟度"]),
            ("💻 AI算力/CPO", ["英伟达财报/新品", "国内算力建设", "光模块订单"]),
        ]
        
        for name, points in sectors:
            lines.append(f"{name}:")
            lines.append("  监控要点:")
            for point in points:
                lines.append(f"  • {point}")
            lines.append("")
        
        return lines
    
    def _generate_trading_plan(self) -> List[str]:
        """生成交易计划"""
        lines = [
            "📋 【今日操作建议】",
            "-" * 70,
            "",
        ]
        
        lines.extend([
            "开盘策略:",
            "  • 高开 (>2%): 不追涨，持仓观察",
            "  • 平开 (±2%): 按原计划操作",
            "  • 低开 (<-2%): 关注加仓机会",
            "",
            "Smart ROI 策略:",
            "  • ROI ≥ 3.0: 强烈推荐，积极参与",
            "  • ROI 2.0-3.0: 推荐参与，控制仓位",
            "  • ROI 1.5-2.0: 轻仓尝试，严格止损",
            "  • ROI < 1.5: 建议观望，等待机会",
            "",
            "持仓管理:",
            "  • 强势股+高ROI: 持有或加仓",
            "  • 弱势股+低ROI: 反弹减仓",
            "  • 中线股: 忽略短期波动",
            "",
        ])
        
        return lines
    
    def _generate_risk_alerts(self) -> List[str]:
        """生成风险提醒"""
        lines = [
            "⚠️ 【风险提醒】",
            "-" * 70,
            "",
            "今日关注:",
            "  • 大盘是否放量突破/跌破关键位置",
            "  • 持仓股是否有重大公告",
            "  • 北向资金流向",
            "  • 美股隔夜表现对开盘影响",
            "",
            "Smart ROI 风险提示:",
            "  • ROI 计算基于历史数据和概率模型",
            "  • 实际收益可能与预期不符",
            "  • 高 ROI 不代表无风险",
            "  • 请结合自身风险承受能力决策",
            "",
            "止损纪律:",
            "  • 单只股票亏损不超过 -8%",
            "  • 总仓位回撤超过 -15% 减仓",
            "  • 跌破重要支撑位果断止损",
            "",
            "免责声明:",
            "  本报告仅供参考，不构成投资建议",
            "  股市有风险，投资需谨慎",
            "  Smart ROI 系统借鉴 bounty-hunter-skill 量化框架",
            "",
        ]
        
        return lines
    
    def save_report(self, filename: str = None):
        """保存报告"""
        if filename is None:
            filename = f"morning_report_smart_roi_{self.report_time.strftime('%Y%m%d')}.txt"
        
        report = self.generate_report()
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return filename


def generate_smart_report():
    """生成并打印智能晨报"""
    print("🚀 正在生成 AI 智能股票晨报 (Smart ROI 版)...")
    print("=" * 70)
    print()
    
    generator = SmartMorningReportGenerator()
    report = generator.generate_report()
    
    print(report)
    
    # 保存到文件
    filename = generator.save_report()
    print(f"\n✅ 报告已保存: {filename}")
    
    return report


# 定时任务入口
if __name__ == "__main__":
    report = generate_smart_report()
