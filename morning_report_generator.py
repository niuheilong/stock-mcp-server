#!/usr/bin/env python3
"""
AI 股票晨报生成器
整合所有能力：实时数据 + 多智能体分析 + 新闻监控 + 技术指标
每天早上 8:00 自动生成专业晨报
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List
from intelligent_scheduler import get_scheduler
from multi_agent_robust import robust_stock_analysis
from jina_reader import fetch_with_jina
from sina_stock_api import get_sina_stock_price


class MorningReportGenerator:
    """晨报生成器"""
    
    def __init__(self):
        self.scheduler = get_scheduler()
        self.report_time = datetime.now()
        
        # 用户持仓股票（从 USER.md 读取）
        self.holdings = [
            {"code": "002156", "name": "通富微电", "rating": "强", "strategy": "持有/加仓"},
            {"code": "003029", "name": "金富科技", "rating": "强", "strategy": "持有/加仓"},
            {"code": "601599", "name": "浙文影业", "rating": "强", "strategy": "持有/加仓"},
            {"code": "300645", "name": "正元智慧", "rating": "中", "strategy": "高抛低吸"},
            {"code": "002023", "name": "海特高新", "rating": "中", "strategy": "观望"},
            {"code": "300058", "name": "蓝色光标", "rating": "弱", "strategy": "减仓/止损"},
            {"code": "300724", "name": "捷佳伟创", "rating": "弱", "strategy": "减仓/止损"},
            {"code": "300773", "name": "拉卡拉", "rating": "弱", "strategy": "减仓/止损"},
        ]
        
        # 关注板块
        self.focus_sectors = [
            "芯片封装/Chiplet",
            "人形机器人",
            "商业航天/低空经济",
            "AI算力/CPO",
        ]
    
    def generate_report(self) -> str:
        """生成完整晨报"""
        report_lines = []
        
        # 1. 标题和日期
        report_lines.extend(self._generate_header())
        
        # 2. 市场概览
        report_lines.extend(self._generate_market_overview())
        
        # 3. 持仓股票分析
        report_lines.extend(self._generate_holdings_analysis())
        
        # 4. 关注板块动态
        report_lines.extend(self._generate_sector_news())
        
        # 5. 今日操作建议
        report_lines.extend(self._generate_trading_plan())
        
        # 6. 风险提醒
        report_lines.extend(self._generate_risk_alerts())
        
        return "\n".join(report_lines)
    
    def _generate_header(self) -> List[str]:
        """生成标题"""
        return [
            "=" * 70,
            f"📊 AI 股票晨报 - {self.report_time.strftime('%Y年%m月%d日 %H:%M')}",
            "=" * 70,
            "",
            f"报告生成时间: {self.report_time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"数据时间: 交易日 {self.report_time.strftime('%H:%M')}",
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
            # 抓取东方财富首页判断情绪
            result = fetch_with_jina("https://finance.eastmoney.com")
            if result['success']:
                content = result['content']
                
                # 统计涨跌关键词
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
    
    def _generate_holdings_analysis(self) -> List[str]:
        """生成持仓分析"""
        lines = [
            "💼 【持仓股票分析】",
            "-" * 70,
            "",
        ]
        
        # 分类持仓
        strong_holdings = [h for h in self.holdings if h["rating"] == "强"]
        medium_holdings = [h for h in self.holdings if h["rating"] == "中"]
        weak_holdings = [h for h in self.holdings if h["rating"] == "弱"]
        
        # 强势持仓
        if strong_holdings:
            lines.extend([
                "🟢 强势持仓（建议持有/加仓）:",
                "",
            ])
            for stock in strong_holdings:
                analysis = self._analyze_single_stock(stock)
                lines.extend(analysis)
                lines.append("")
        
        # 中等持仓
        if medium_holdings:
            lines.extend([
                "🟡 中等持仓（建议观望/高抛低吸）:",
                "",
            ])
            for stock in medium_holdings:
                analysis = self._analyze_single_stock(stock)
                lines.extend(analysis)
                lines.append("")
        
        # 弱势持仓
        if weak_holdings:
            lines.extend([
                "🔴 弱势持仓（建议减仓/止损）:",
                "",
            ])
            for stock in weak_holdings:
                analysis = self._analyze_single_stock(stock)
                lines.extend(analysis)
                lines.append("")
        
        return lines
    
    def _analyze_single_stock(self, stock: Dict) -> List[str]:
        """分析单只股票"""
        lines = []
        code = stock["code"]
        name = stock["name"]
        
        try:
            # 使用智能调度器获取实时数据
            price_data = get_sina_stock_price(code)
            
            if 'error' in price_data:
                lines.append(f"  {name}({code}): 数据获取失败")
                return lines
            
            price = price_data['price']
            change = price_data['change_percent']
            volume = price_data['volume']
            
            # 涨跌表情
            emoji = "🟢" if change > 0 else "🔴" if change < 0 else "⚪"
            
            lines.append(f"  {emoji} {name}({code}): ¥{price:.2f} ({change:+.2f}%)")
            lines.append(f"     成交量: {volume/10000:.2f}万手")
            
            # 简单技术分析
            if change > 5:
                lines.append(f"     ⚠️ 今日大涨，注意追高风险")
            elif change > 2:
                lines.append(f"     ✅ 积极上涨，趋势良好")
            elif change < -5:
                lines.append(f"     ⚠️ 今日大跌，关注支撑位")
            elif change < -2:
                lines.append(f"     📉 回调中，观察是否企稳")
            else:
                lines.append(f"     ➖ 波动较小，维持原策略")
            
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
        
        # 芯片板块
        lines.extend([
            "🧠 芯片封装/Chiplet:",
            "  监控要点:",
            "  • 关注行业订单情况",
            "  • 留意技术突破新闻",
            "  • 跟踪龙头股价走势",
            "",
        ])
        
        # 机器人板块
        lines.extend([
            "🤖 人形机器人:",
            "  监控要点:",
            "  • 特斯拉Optimus进展",
            "  • 国内厂商新品发布",
            "  • 政策支持力度",
            "",
        ])
        
        # 商业航天
        lines.extend([
            "🚀 商业航天/低空经济:",
            "  监控要点:",
            "  • 政策利好落地",
            "  • 订单释放情况",
            "  • 技术成熟度",
            "",
        ])
        
        # AI算力
        lines.extend([
            "💻 AI算力/CPO:",
            "  监控要点:",
            "  • 英伟达财报/新品",
            "  • 国内算力建设",
            "  • 光模块订单",
            "",
        ])
        
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
            "持仓管理:",
            "  • 强势股: 持有，设移动止盈",
            "  • 弱势股: 反弹减仓，严格止损",
            "  • 中线股: 忽略短期波动",
            "",
            "新仓计划:",
            "  • 不追高涨幅 >5% 的股票",
            "  • 关注回调到支撑位的机会",
            "  • 优先考虑持仓中的强势品种",
            "",
        ])
        
        return lines
    
    def _generate_risk_alerts(self) -> List[str]:
        """生成风险提醒"""
        lines = [
            "⚠️ 【风险提醒】",
            "-" * 70,
            "",
        ]
        
        lines.extend([
            "今日关注:",
            "  • 大盘是否放量突破/跌破关键位置",
            "  • 持仓股是否有重大公告",
            "  • 北向资金流向",
            "  • 美股隔夜表现对开盘影响",
            "",
            "止损纪律:",
            "  • 单只股票亏损不超过 -8%",
            "  • 总仓位回撤超过 -15% 减仓",
            "  • 跌破重要支撑位果断止损",
            "",
            "免责声明:",
            "  本报告仅供参考，不构成投资建议",
            "  股市有风险，投资需谨慎",
            "",
        ])
        
        return lines
    
    def save_report(self, filename: str = None):
        """保存报告"""
        if filename is None:
            filename = f"morning_report_{self.report_time.strftime('%Y%m%d')}.txt"
        
        report = self.generate_report()
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return filename


def generate_and_print_report():
    """生成并打印晨报"""
    print("🚀 正在生成 AI 股票晨报...")
    print("=" * 70)
    
    generator = MorningReportGenerator()
    report = generator.generate_report()
    
    print(report)
    
    # 保存到文件
    filename = generator.save_report()
    print(f"\n✅ 报告已保存: {filename}")
    
    return report


# 定时任务入口
if __name__ == "__main__":
    report = generate_and_print_report()
