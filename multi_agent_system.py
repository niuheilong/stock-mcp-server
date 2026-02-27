#!/usr/bin/env python3
"""
多智能体股票分析系统
基于 TradingAgents-CN 架构简化实现

核心智能体：
1. 技术分析师 (Technical Analyst)
2. 基本面分析师 (Fundamental Analyst)  
3. 市场情绪分析师 (Sentiment Analyst)
4. 风险管理师 (Risk Manager)
5. 决策委员会 (Decision Committee)
"""

import json
import time
from typing import Dict, List, Optional
from datetime import datetime
from technical_indicators import TechnicalAnalyst


class FundamentalAnalyst:
    """
    基本面分析师
    分析公司财务数据、估值指标
    """
    
    def __init__(self, stock_code: str):
        self.stock_code = stock_code
    
    def analyze(self) -> Dict:
        """
        执行基本面分析
        """
        try:
            import akshare as ak
            
            # 获取股票基本信息
            stock_info = ak.stock_individual_info_em(symbol=self.stock_code)
            
            # 获取财务数据
            try:
                finance = ak.stock_financial_report_sina(stock=self.stock_code)
            except:
                finance = pd.DataFrame()
            
            # 构建分析报告
            report = {
                'stock_code': self.stock_code,
                'company_name': stock_info.loc[stock_info['item'] == '股票简称', 'value'].values[0] if not stock_info.empty else 'N/A',
                'industry': stock_info.loc[stock_info['item'] == '行业', 'value'].values[0] if not stock_info.empty else 'N/A',
                'total_market_cap': stock_info.loc[stock_info['item'] == '总市值', 'value'].values[0] if not stock_info.empty else 'N/A',
                'pe_ratio': stock_info.loc[stock_info['item'] == '市盈率', 'value'].values[0] if not stock_info.empty else 'N/A',
                'pb_ratio': stock_info.loc[stock_info['item'] == '市净率', 'value'].values[0] if not stock_info.empty else 'N/A',
                'analysis': self._generate_analysis(stock_info),
                'recommendation': self._generate_recommendation(stock_info)
            }
            
            return report
            
        except Exception as e:
            return {
                'stock_code': self.stock_code,
                'error': str(e),
                'recommendation': '数据获取失败，无法分析'
            }
    
    def _generate_analysis(self, stock_info) -> str:
        """生成基本面分析"""
        if stock_info.empty:
            return "无法获取基本面数据"
        
        analysis = []
        
        try:
            pe = float(stock_info.loc[stock_info['item'] == '市盈率', 'value'].values[0])
            if pe < 0:
                analysis.append("市盈率为负，公司处于亏损状态")
            elif pe < 20:
                analysis.append("市盈率较低，估值相对合理")
            elif pe > 50:
                analysis.append("市盈率较高，注意估值风险")
            else:
                analysis.append("市盈率处于正常区间")
        except:
            pass
        
        try:
            pb = float(stock_info.loc[stock_info['item'] == '市净率', 'value'].values[0])
            if pb < 1:
                analysis.append("市净率低于1，可能存在价值洼地")
            elif pb > 5:
                analysis.append("市净率较高，注意资产溢价风险")
        except:
            pass
        
        return "; ".join(analysis) if analysis else "基本面数据正常"
    
    def _generate_recommendation(self, stock_info) -> str:
        """生成投资建议"""
        try:
            pe = float(stock_info.loc[stock_info['item'] == '市盈率', 'value'].values[0])
            if pe < 0:
                return "亏损股，高风险，谨慎参与"
            elif pe < 20:
                return "估值合理，可考虑长期持有"
            elif pe > 100:
                return "估值过高，注意风险"
            return "估值适中，结合技术面决策"
        except:
            return "数据不足，无法给出建议"


class SentimentAnalyst:
    """
    市场情绪分析师
    分析新闻情绪、市场热度
    """
    
    def __init__(self, stock_code: str):
        self.stock_code = stock_code
    
    def analyze(self) -> Dict:
        """
        执行情绪分析
        """
        try:
            from jina_reader import fetch_with_jina
            
            # 抓取相关新闻
            search_url = f'https://so.eastmoney.com/web/s?keyword={self.stock_code}'
            result = fetch_with_jina(search_url)
            
            if not result['success']:
                return {
                    'stock_code': self.stock_code,
                    'sentiment_score': 0,
                    'mood': '中性',
                    'recommendation': '无法获取情绪数据'
                }
            
            content = result['content']
            
            # 简单关键词情绪分析
            positive_words = ['上涨', '涨停', '大涨', '利好', '增长', '突破', '看好', '买入']
            negative_words = ['下跌', '跌停', '大跌', '利空', '亏损', '跌破', '看空', '卖出']
            
            positive_count = sum(content.count(word) for word in positive_words)
            negative_count = sum(content.count(word) for word in negative_words)
            
            total = positive_count + negative_count
            if total > 0:
                sentiment_score = (positive_count - negative_count) / total
            else:
                sentiment_score = 0
            
            # 判断情绪
            if sentiment_score > 0.3:
                mood = '极度乐观'
            elif sentiment_score > 0.1:
                mood = '乐观'
            elif sentiment_score > -0.1:
                mood = '中性'
            elif sentiment_score > -0.3:
                mood = '悲观'
            else:
                mood = '极度悲观'
            
            report = {
                'stock_code': self.stock_code,
                'sentiment_score': round(sentiment_score, 2),
                'positive_signals': positive_count,
                'negative_signals': negative_count,
                'mood': mood,
                'hot_keywords': self._extract_keywords(content),
                'recommendation': self._generate_recommendation(sentiment_score)
            }
            
            return report
            
        except Exception as e:
            return {
                'stock_code': self.stock_code,
                'sentiment_score': 0,
                'mood': '未知',
                'error': str(e),
                'recommendation': '情绪分析失败'
            }
    
    def _extract_keywords(self, content: str) -> List[str]:
        """提取热门关键词"""
        keywords = ['算力', 'AI', '人工智能', '新能源', '芯片', '半导体', '业绩', '订单']
        found = []
        for kw in keywords:
            if kw in content:
                found.append(kw)
        return found[:5]
    
    def _generate_recommendation(self, score: float) -> str:
        """生成投资建议"""
        if score > 0.3:
            return "市场情绪极度乐观，注意追高风险"
        elif score > 0.1:
            return "市场情绪积极，可考虑参与"
        elif score > -0.1:
            return "市场情绪中性，观望为主"
        elif score > -0.3:
            return "市场情绪偏空，谨慎操作"
        else:
            return "市场情绪极度悲观，可能存在反弹机会"


class RiskManager:
    """
    风险管理师
    评估风险、给出仓位建议
    """
    
    def __init__(self, stock_code: str):
        self.stock_code = stock_code
    
    def analyze(self, technical_report: Dict, fundamental_report: Dict, sentiment_report: Dict) -> Dict:
        """
        执行风险评估
        """
        risks = []
        risk_level = 'low'
        
        # 技术分析风险
        if technical_report.get('signals'):
            if any('死叉' in s or '空头' in s or '超卖' in s for s in technical_report['signals']):
                risks.append("技术指标显示空头信号")
                risk_level = 'medium'
        
        # 基本面风险
        if fundamental_report.get('pe_ratio'):
            try:
                pe = float(fundamental_report['pe_ratio'])
                if pe < 0:
                    risks.append("公司处于亏损状态，基本面风险高")
                    risk_level = 'high'
                elif pe > 100:
                    risks.append("市盈率过高，估值风险")
                    risk_level = 'high'
            except:
                pass
        
        # 情绪风险
        sentiment_score = sentiment_report.get('sentiment_score', 0)
        if abs(sentiment_score) > 0.5:
            risks.append("市场情绪极端，波动风险大")
            risk_level = 'high' if risk_level != 'high' else 'high'
        
        # 生成建议
        position_sizing = self._calculate_position_size(risk_level)
        
        report = {
            'stock_code': self.stock_code,
            'risk_level': risk_level,
            'risks': risks,
            'position_sizing': position_sizing,
            'stop_loss_recommendation': self._recommend_stop_loss(technical_report),
            'recommendation': f"风险等级: {risk_level}，建议仓位: {position_sizing}"
        }
        
        return report
    
    def _calculate_position_size(self, risk_level: str) -> str:
        """计算建议仓位"""
        if risk_level == 'high':
            return "不超过10%（轻仓试探）"
        elif risk_level == 'medium':
            return "10%-30%（中等仓位）"
        else:
            return "30%-50%（重仓持有）"
    
    def _recommend_stop_loss(self, technical_report: Dict) -> str:
        """推荐止损位"""
        # 基于技术指标推荐止损
        return "建议止损位: 买入价下方 5-8%"


class DecisionCommittee:
    """
    决策委员会
    综合各智能体意见，给出最终决策
    """
    
    def __init__(self, stock_code: str):
        self.stock_code = stock_code
        self.technical_analyst = TechnicalAnalyst(stock_code)
        self.fundamental_analyst = FundamentalAnalyst(stock_code)
        self.sentiment_analyst = SentimentAnalyst(stock_code)
        self.risk_manager = RiskManager(stock_code)
    
    def make_decision(self) -> Dict:
        """
        综合决策流程
        """
        print(f"🔍 开始对 {self.stock_code} 进行多智能体分析...")
        
        # 1. 技术分析师
        print("  🤖 技术分析师分析中...")
        technical_report = self.technical_analyst.analyze()
        
        # 2. 基本面分析师
        print("  🤖 基本面分析师分析中...")
        fundamental_report = self.fundamental_analyst.analyze()
        
        # 3. 情绪分析师
        print("  🤖 市场情绪分析师分析中...")
        sentiment_report = self.sentiment_analyst.analyze()
        
        # 4. 风险管理师
        print("  🤖 风险管理师评估中...")
        risk_report = self.risk_manager.analyze(technical_report, fundamental_report, sentiment_report)
        
        # 5. 综合决策
        print("  🎯 决策委员会综合决策中...")
        final_decision = self._synthesize_decision(
            technical_report, fundamental_report, sentiment_report, risk_report
        )
        
        return {
            'stock_code': self.stock_code,
            'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'technical_analysis': technical_report,
            'fundamental_analysis': fundamental_report,
            'sentiment_analysis': sentiment_report,
            'risk_assessment': risk_report,
            'final_decision': final_decision
        }
    
    def _synthesize_decision(self, technical: Dict, fundamental: Dict, sentiment: Dict, risk: Dict) -> Dict:
        """综合各分析师意见生成最终决策"""
        
        # 收集各维度信号
        signals = []
        
        # 技术信号
        if technical.get('recommendation'):
            signals.append(('技术', technical['recommendation']))
        
        # 基本面信号
        if fundamental.get('recommendation'):
            signals.append(('基本面', fundamental['recommendation']))
        
        # 情绪信号
        if sentiment.get('recommendation'):
            signals.append(('情绪', sentiment['recommendation']))
        
        # 风险信号
        if risk.get('recommendation'):
            signals.append(('风险', risk['recommendation']))
        
        # 综合判断
        bullish_count = sum(1 for _, s in signals if '买入' in s or '持有' in s or '偏多' in s)
        bearish_count = sum(1 for _, s in signals if '卖出' in s or '观望' in s or '偏空' in s)
        
        if bullish_count > bearish_count:
            action = "买入/持有"
            confidence = f"{bullish_count}/{len(signals)} 分析师看多"
        elif bearish_count > bullish_count:
            action = "观望/减仓"
            confidence = f"{bearish_count}/{len(signals)} 分析师看空"
        else:
            action = "中性观望"
            confidence = "分析师意见分歧"
        
        return {
            'action': action,
            'confidence': confidence,
            'signals': signals,
            'rationale': f"基于 {len(signals)} 个维度分析，{confidence}"
        }


def multi_agent_stock_analysis(stock_code: str) -> Dict:
    """
    多智能体股票分析主函数
    
    Args:
        stock_code: 股票代码（如 '600519'）
    
    Returns:
        dict: 完整的分析报告
    """
    committee = DecisionCommittee(stock_code)
    return committee.make_decision()


# 测试
if __name__ == "__main__":
    print("🚀 多智能体股票分析系统测试")
    print("=" * 70)
    
    # 测试贵州茅台
    stock_code = "600519"
    print(f"\n📊 分析股票: {stock_code} (贵州茅台)")
    print("=" * 70)
    
    report = multi_agent_stock_analysis(stock_code)
    
    print("\n" + "=" * 70)
    print("📋 分析报告")
    print("=" * 70)
    
    # 技术层面
    tech = report['technical_analysis']
    if 'error' not in tech:
        print(f"\n📈 技术分析:")
        print(f"  最新价: ¥{tech.get('latest_price', 'N/A')}")
        print(f"  MACD: {tech['indicators']['macd'][:50]}...")
        print(f"  RSI: {tech['indicators']['rsi'][:50]}...")
        print(f"  信号: {', '.join(tech.get('signals', []))}")
        print(f"  建议: {tech.get('recommendation', 'N/A')}")
    
    # 基本面
    fund = report['fundamental_analysis']
    if 'error' not in fund:
        print(f"\n📊 基本面分析:")
        print(f"  公司: {fund.get('company_name', 'N/A')}")
        print(f"  行业: {fund.get('industry', 'N/A')}")
        print(f"  市盈率: {fund.get('pe_ratio', 'N/A')}")
        print(f"  建议: {fund.get('recommendation', 'N/A')}")
    
    # 情绪
    sent = report['sentiment_analysis']
    print(f"\n💭 市场情绪:")
    print(f"  情绪分数: {sent.get('sentiment_score', 0)}")
    print(f"  市场情绪: {sent.get('mood', 'N/A')}")
    print(f"  关键词: {', '.join(sent.get('hot_keywords', []))}")
    
    # 风险
    risk = report['risk_assessment']
    print(f"\n⚠️ 风险评估:")
    print(f"  风险等级: {risk.get('risk_level', 'N/A')}")
    print(f"  仓位建议: {risk.get('position_sizing', 'N/A')}")
    
    # 最终决策
    decision = report['final_decision']
    print(f"\n🎯 最终决策:")
    print(f"  建议操作: {decision.get('action', 'N/A')}")
    print(f"  置信度: {decision.get('confidence', 'N/A')}")
    print(f"  理由: {decision.get('rationale', 'N/A')}")
    
    print("\n" + "=" * 70)
    print("✅ 多智能体分析完成！")
