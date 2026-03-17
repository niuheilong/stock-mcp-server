#!/usr/bin/env python3
"""
青龙 Stock MCP Server v4.0.0
实时A股股票数据 + 技术分析 + 舆情情绪分析
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
import requests
import json
from datetime import datetime, timedelta
import asyncio
import re
from dataclasses import dataclass
from enum import Enum

# 导入资金流向模块
from capital_flow import CapitalFlowAnalyzer, CapitalFlowData

# 导入板块分析模块
from sector_analysis import SectorAnalyzer, SectorLinkage, StockSectorInfo

# 导入回测框架
from backtest import HistoryDatabase, BacktestEngine, HistoricalRecord

# 导入预警系统
from alert_system import AlertEngine, AlertRule, AlertEvent, AlertType, AlertLevel, console_alert_handler

app = FastAPI(title="青龙 Stock MCP Server", version="4.4.0")

# ==================== 数据模型 ====================

class SentimentLevel(str, Enum):
    """情绪等级"""
    EXTREME_FEAR = "极度恐慌"
    FEAR = "恐慌"
    NEUTRAL = "中性"
    GREED = "贪婪"
    EXTREME_GREED = "极度贪婪"

@dataclass
class SentimentScore:
    """情绪分数"""
    overall: float  # 0-100
    level: SentimentLevel
    news_sentiment: float  # 新闻情绪
    social_sentiment: float  # 社交媒体情绪
    volume_sentiment: float  # 成交量情绪
    factors: Dict[str, float]  # 各因子得分

class StockData(BaseModel):
    """股票数据"""
    code: str
    name: str
    price: float
    change: float
    change_percent: float
    volume: int
    turnover: float
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None

class TechnicalAnalysis(BaseModel):
    """技术分析"""
    code: str
    macd: Dict
    kdj: Dict
    rsi: float
    ma_trend: str
    support_resistance: Dict
    signals: List[str]

class SentimentAnalysis(BaseModel):
    """舆情情绪分析"""
    code: str
    overall_score: float
    sentiment_level: str
    news_sentiment: float
    social_sentiment: float
    volume_sentiment: float
    hot_topics: List[str]
    risk_alerts: List[str]
    analysis_summary: str

class CapitalFlowAnalysis(BaseModel):
    """资金流向分析"""
    code: str
    main_inflow: float
    main_inflow_percent: float
    retail_inflow: float
    retail_inflow_percent: float
    large_order_inflow: float
    medium_order_inflow: float
    small_order_inflow: float
    northbound_inflow: Optional[float]
    northbound_hold_percent: Optional[float]
    margin_balance: Optional[float]
    flow_score: float
    flow_level: str
    flow_signals: List[str]
    main_force_trend: str
    retail_force_trend: str
    smart_money_agreement: bool

class SectorAnalysis(BaseModel):
    """板块联动分析"""
    code: str
    sector_score: float
    sector_level: str
    description: str
    best_sector: str
    sector_rank: int
    is_sector_leader: bool
    is_sector_follower: bool
    top_sectors: List[Dict]
    peer_stocks: List[Dict]

class QingLongReport(BaseModel):
    """青龙分析报告"""
    code: str
    stock_data: StockData
    technical: TechnicalAnalysis
    sentiment: SentimentAnalysis
    capital_flow: CapitalFlowAnalysis
    sector_analysis: SectorAnalysis
    qinglong_score: float
    recommendation: str
    timestamp: str

# ==================== 股票列表 ====================

STOCK_WATCHLIST = {
    "sh600410": "华胜天成",
    "sh600620": "天宸股份",
    "sh603986": "兆易创新",
    "sh688525": "佰维存储",
    "sz002261": "拓维信息",
    "sz300428": "立中集团",  # 修正：原利通股份代码有误
    "sh688629": "华丰科技",
}

# ==================== 腾讯财经API ====================

def fetch_stock_data_tencent(code: str) -> Optional[Dict]:
    """从腾讯财经获取股票数据"""
    try:
        # 转换代码格式
        if code.startswith("sh"):
            tencent_code = code.replace("sh", "sh")  # 上证保持sh
        elif code.startswith("sz"):
            tencent_code = code.replace("sz", "sz")  # 深证保持sz
        else:
            return None
        
        url = f"http://qt.gtimg.cn/q={tencent_code}"
        response = requests.get(url, timeout=10)
        response.encoding = 'gbk'
        
        if response.status_code == 200:
            data = response.text
            # 解析腾讯返回的数据格式
            match = re.search(r'v_{}="([^"]+)"'.format(tencent_code), data)
            if match:
                fields = match.group(1).split('~')
                if len(fields) >= 45:
                    return {
                        "name": fields[1],
                        "code": code,
                        "price": float(fields[3]),
                        "change": float(fields[4]),
                        "change_percent": float(fields[5]),
                        "volume": int(fields[6]),
                        "turnover": float(fields[7]),
                        "market_cap": float(fields[14]) if fields[14] else None,
                        "pe_ratio": float(fields[39]) if fields[39] else None,
                        "pb_ratio": float(fields[46]) if len(fields) > 46 and fields[46] else None,
                    }
        return None
    except Exception as e:
        print(f"Error fetching stock data: {e}")
        return None

# ==================== 技术分析模块 ====================

def calculate_macd(prices: List[float]) -> Dict:
    """计算MACD指标"""
    if len(prices) < 26:
        return {"macd": 0, "signal": 0, "histogram": 0, "trend": "数据不足"}
    
    # 简化计算，实际应该用EMA
    ema12 = sum(prices[-12:]) / 12
    ema26 = sum(prices[-26:]) / 26
    macd = ema12 - ema26
    signal = macd * 0.9  # 简化信号线
    histogram = macd - signal
    
    trend = "金叉" if histogram > 0 and histogram > signal * 0.1 else \
            "死叉" if histogram < 0 and histogram < signal * 0.1 else "震荡"
    
    return {
        "macd": round(macd, 4),
        "signal": round(signal, 4),
        "histogram": round(histogram, 4),
        "trend": trend
    }

def calculate_kdj(prices: List[float], highs: List[float], lows: List[float]) -> Dict:
    """计算KDJ指标"""
    if len(prices) < 9:
        return {"k": 50, "d": 50, "j": 50, "signal": "数据不足"}
    
    # 简化计算
    rsv = 50  # 简化RSV
    k = 50 + rsv * 0.1
    d = 50 + k * 0.1
    j = 3 * k - 2 * d
    
    signal = "超买" if j > 80 else "超卖" if j < 20 else "中性"
    
    return {
        "k": round(k, 2),
        "d": round(d, 2),
        "j": round(j, 2),
        "signal": signal
    }

def calculate_rsi(prices: List[float], period: int = 14) -> float:
    """计算RSI指标"""
    if len(prices) < period + 1:
        return 50.0
    
    gains = []
    losses = []
    
    for i in range(1, period + 1):
        change = prices[-i] - prices[-i-1]
        if change > 0:
            gains.append(change)
        else:
            losses.append(abs(change))
    
    avg_gain = sum(gains) / period if gains else 0
    avg_loss = sum(losses) / period if losses else 0
    
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return round(rsi, 2)

# ==================== 舆情情绪分析模块 ====================

class SentimentAnalyzer:
    """舆情情绪分析器"""
    
    # 正面关键词词典
    POSITIVE_KEYWORDS = [
        "涨停", "大涨", "飙升", "突破", "利好", "增持", "回购", "业绩预增",
        "订单", "合作", "签约", "中标", "获批", "创新", "领先", "龙头",
        "政策利好", "行业景气", "需求旺盛", "产能扩张", "技术突破",
        "strong", "surge", "breakthrough", "bullish", "upgrade"
    ]
    
    # 负面关键词词典
    NEGATIVE_KEYWORDS = [
        "跌停", "大跌", "暴跌", "破位", "利空", "减持", "质押", "业绩预亏",
        "亏损", "下滑", "下降", "风险", "警示", "监管", "调查", "诉讼",
        "债务", "违约", "裁员", "停产", "召回", "事故",
        "weak", "crash", "breakdown", "bearish", "downgrade"
    ]
    
    # 中性关键词
    NEUTRAL_KEYWORDS = [
        "持平", "震荡", "盘整", "观望", "调整", "整理", "横盘",
        "flat", "consolidation", "sideways"
    ]
    
    def __init__(self):
        self.news_cache = {}
        self.social_cache = {}
    
    def analyze_text_sentiment(self, text: str) -> float:
        """分析文本情绪，返回-1到1的分数"""
        if not text:
            return 0.0
        
        text = text.lower()
        pos_count = sum(1 for kw in self.POSITIVE_KEYWORDS if kw in text)
        neg_count = sum(1 for kw in self.NEGATIVE_KEYWORDS if kw in text)
        neu_count = sum(1 for kw in self.NEUTRAL_KEYWORDS if kw in text)
        
        total = pos_count + neg_count + neu_count
        if total == 0:
            return 0.0
        
        # 计算情绪分数
        sentiment = (pos_count - neg_count) / (pos_count + neg_count + 1)
        return max(-1, min(1, sentiment))
    
    def fetch_news_sentiment(self, stock_name: str, stock_code: str) -> float:
        """获取新闻情绪（模拟实现，实际应调用新闻API）"""
        # 这里应该调用实际的新闻API
        # 例如：新浪财经、东方财富、同花顺等
        
        # 模拟数据 - 实际实现需要接入真实API
        mock_news = self._mock_news_data(stock_name, stock_code)
        
        sentiments = [self.analyze_text_sentiment(news) for news in mock_news]
        return sum(sentiments) / len(sentiments) if sentiments else 0.0
    
    def fetch_social_sentiment(self, stock_name: str, stock_code: str) -> float:
        """获取社交媒体情绪（模拟实现）"""
        # 这里应该调用雪球、股吧等社交媒体API
        mock_social = self._mock_social_data(stock_name, stock_code)
        
        sentiments = [self.analyze_text_sentiment(post) for post in mock_social]
        return sum(sentiments) / len(sentiments) if sentiments else 0.0
    
    def analyze_volume_sentiment(self, volume: int, avg_volume: int) -> float:
        """分析成交量情绪"""
        if avg_volume == 0:
            return 0.0
        
        ratio = volume / avg_volume
        
        if ratio > 3:
            return 0.8  # 极度放量，情绪高涨
        elif ratio > 2:
            return 0.5  # 明显放量
        elif ratio > 1.5:
            return 0.2  # 温和放量
        elif ratio > 0.8:
            return 0.0  # 正常
        elif ratio > 0.5:
            return -0.2  # 缩量
        else:
            return -0.5  # 极度缩量
    
    def calculate_overall_sentiment(
        self,
        news_sentiment: float,
        social_sentiment: float,
        volume_sentiment: float,
        price_change: float
    ) -> SentimentScore:
        """计算综合情绪分数"""
        
        # 价格变化对情绪的影响
        price_sentiment = max(-1, min(1, price_change / 10))
        
        # 加权计算
        weights = {
            "news": 0.25,
            "social": 0.25,
            "volume": 0.20,
            "price": 0.30
        }
        
        overall = (
            news_sentiment * weights["news"] +
            social_sentiment * weights["social"] +
            volume_sentiment * weights["volume"] +
            price_sentiment * weights["price"]
        )
        
        # 转换为0-100分数
        score = (overall + 1) * 50
        
        # 确定情绪等级
        if score >= 80:
            level = SentimentLevel.EXTREME_GREED
        elif score >= 60:
            level = SentimentLevel.GREED
        elif score >= 40:
            level = SentimentLevel.NEUTRAL
        elif score >= 20:
            level = SentimentLevel.FEAR
        else:
            level = SentimentLevel.EXTREME_FEAR
        
        return SentimentScore(
            overall=round(score, 2),
            level=level,
            news_sentiment=round((news_sentiment + 1) * 50, 2),
            social_sentiment=round((social_sentiment + 1) * 50, 2),
            volume_sentiment=round((volume_sentiment + 1) * 50, 2),
            factors={
                "news_weight": weights["news"],
                "social_weight": weights["social"],
                "volume_weight": weights["volume"],
                "price_weight": weights["price"]
            }
        )
    
    def _mock_news_data(self, stock_name: str, stock_code: str) -> List[str]:
        """模拟新闻数据"""
        return [
            f"{stock_name}获得大额订单，业绩有望大幅提升",
            f"{stock_name}技术突破，行业地位进一步巩固",
            f"分析师上调{stock_name}评级至买入",
            f"{stock_name}主力资金净流入超亿元",
        ]
    
    def _mock_social_data(self, stock_name: str, stock_code: str) -> List[str]:
        """模拟社交媒体数据"""
        return [
            f"看好{stock_name}，突破前高了！",
            f"{stock_name}今天放量上涨，有戏",
            "这股票基本面不错，可以长期持有",
            f"{stock_name}技术指标走好了",
        ]
    
    def extract_hot_topics(self, stock_name: str) -> List[str]:
        """提取热门话题"""
        # 实际实现应该从新闻和社交媒体中提取
        return [
            "业绩预增",
            "技术突破",
            "订单增长",
            "行业景气"
        ]
    
    def detect_risk_alerts(self, stock_data: Dict) -> List[str]:
        """检测风险信号"""
        alerts = []
        
        if stock_data.get("change_percent", 0) < -9:
            alerts.append("⚠️ 股价大幅下跌，注意风险")
        
        if stock_data.get("pe_ratio", 0) > 100:
            alerts.append("⚠️ 市盈率偏高，估值压力大")
        
        # 可以添加更多风险检测逻辑
        
        return alerts

# ==================== 青龙分析引擎 ====================

class QingLongEngine:
    """青龙分析引擎"""

    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()
        self.capital_flow_analyzer = CapitalFlowAnalyzer()
        self.sector_analyzer = SectorAnalyzer()
    
    def analyze_stock(self, code: str) -> QingLongReport:
        """分析单只股票"""
        
        # 1. 获取股票数据
        raw_data = fetch_stock_data_tencent(code)
        if not raw_data:
            raise HTTPException(status_code=404, detail=f"无法获取股票 {code} 的数据")
        
        stock_data = StockData(**raw_data)
        
        # 2. 技术分析
        # 实际应该获取历史价格数据
        mock_prices = [stock_data.price * (1 + (i-10)*0.01) for i in range(20)]
        
        technical = TechnicalAnalysis(
            code=code,
            macd=calculate_macd(mock_prices),
            kdj=calculate_kdj(mock_prices, mock_prices, mock_prices),
            rsi=calculate_rsi(mock_prices),
            ma_trend="上升趋势" if stock_data.change > 0 else "下降趋势",
            support_resistance={
                "support": round(stock_data.price * 0.95, 2),
                "resistance": round(stock_data.price * 1.05, 2)
            },
            signals=self._generate_signals(mock_prices, stock_data)
        )
        
        # 3. 舆情情绪分析
        news_sentiment = self.sentiment_analyzer.fetch_news_sentiment(
            stock_data.name, code
        )
        social_sentiment = self.sentiment_analyzer.fetch_social_sentiment(
            stock_data.name, code
        )
        volume_sentiment = self.sentiment_analyzer.analyze_volume_sentiment(
            stock_data.volume, stock_data.volume  # 简化处理
        )

        sentiment_score = self.sentiment_analyzer.calculate_overall_sentiment(
            news_sentiment,
            social_sentiment,
            volume_sentiment,
            stock_data.change_percent
        )

        sentiment = SentimentAnalysis(
            code=code,
            overall_score=sentiment_score.overall,
            sentiment_level=sentiment_score.level.value,
            news_sentiment=sentiment_score.news_sentiment,
            social_sentiment=sentiment_score.social_sentiment,
            volume_sentiment=sentiment_score.volume_sentiment,
            hot_topics=self.sentiment_analyzer.extract_hot_topics(stock_data.name),
            risk_alerts=self.sentiment_analyzer.detect_risk_alerts(raw_data),
            analysis_summary=self._generate_sentiment_summary(sentiment_score)
        )

        # 4. 资金流向分析
        flow_data = self.capital_flow_analyzer.analyze(code)
        if flow_data:
            flow_score_result = self.capital_flow_analyzer.calculate_flow_score(flow_data)
            capital_flow = CapitalFlowAnalysis(
                code=code,
                main_inflow=flow_data.main_inflow,
                main_inflow_percent=flow_data.main_inflow_percent,
                retail_inflow=flow_data.retail_inflow,
                retail_inflow_percent=flow_data.retail_inflow_percent,
                large_order_inflow=flow_data.large_order_inflow,
                medium_order_inflow=flow_data.medium_order_inflow,
                small_order_inflow=flow_data.small_order_inflow,
                northbound_inflow=flow_data.northbound_inflow,
                northbound_hold_percent=flow_data.northbound_hold_percent,
                margin_balance=flow_data.margin_balance,
                flow_score=flow_score_result["score"],
                flow_level=flow_score_result["level"],
                flow_signals=flow_score_result["signals"],
                main_force_trend=flow_score_result["main_force_trend"],
                retail_force_trend=flow_score_result["retail_force_trend"],
                smart_money_agreement=flow_score_result["smart_money_agreement"]
            )
        else:
            # 如果获取失败，使用默认值
            capital_flow = CapitalFlowAnalysis(
                code=code,
                main_inflow=0,
                main_inflow_percent=0,
                retail_inflow=0,
                retail_inflow_percent=0,
                large_order_inflow=0,
                medium_order_inflow=0,
                small_order_inflow=0,
                northbound_inflow=None,
                northbound_hold_percent=None,
                margin_balance=None,
                flow_score=50,
                flow_level="中性",
                flow_signals=["资金流向数据获取失败"],
                main_force_trend="未知",
                retail_force_trend="未知",
                smart_money_agreement=False
            )

        # 5. 板块联动分析
        # 需要从东方财富获取原始数据
        em_raw_data = self.capital_flow_analyzer.api.fetch_stock_data(code)
        linkages = self.sector_analyzer.analyze_sector_linkage(code, em_raw_data)
        sector_score_result = self.sector_analyzer.calculate_sector_score(linkages)

        # 获取热门板块
        top_sectors = []
        sectors = self.sector_analyzer.fetch_sectors("industry", top_n=10)
        for s in sectors[:5]:
            top_sectors.append({
                "name": s.name,
                "change": s.change_percent,
                "main_inflow": s.main_inflow
            })

        # 获取同板块股票
        peer_stocks = []
        if linkages:
            best_linkage = max(linkages, key=lambda x: x.correlation_score)
            peer_stocks = best_linkage.peer_stocks[:5]

        sector_analysis = SectorAnalysis(
            code=code,
            sector_score=sector_score_result["score"],
            sector_level=sector_score_result["level"],
            description=sector_score_result["description"],
            best_sector=sector_score_result.get("best_sector", ""),
            sector_rank=sector_score_result.get("sector_rank", 0),
            is_sector_leader=sector_score_result.get("is_leader", False),
            is_sector_follower=sector_score_result.get("is_follower", False),
            top_sectors=top_sectors,
            peer_stocks=peer_stocks
        )

        # 6. 计算青龙综合分数
        qinglong_score = self._calculate_qinglong_score(
            stock_data, technical, sentiment, capital_flow, sector_analysis
        )

        # 7. 生成建议
        recommendation = self._generate_recommendation(qinglong_score, sentiment, capital_flow, sector_analysis)

        return QingLongReport(
            code=code,
            stock_data=stock_data,
            technical=technical,
            sentiment=sentiment,
            capital_flow=capital_flow,
            sector_analysis=sector_analysis,
            qinglong_score=round(qinglong_score, 2),
            recommendation=recommendation,
            timestamp=datetime.now().isoformat()
        )
    
    def _generate_signals(self, prices: List[float], stock_data: StockData) -> List[str]:
        """生成技术信号"""
        signals = []
        
        if stock_data.change_percent > 5:
            signals.append("🔥 强势上涨")
        elif stock_data.change_percent < -5:
            signals.append("❄️ 大幅下跌")
        
        rsi = calculate_rsi(prices)
        if rsi > 70:
            signals.append("⚠️ RSI超买")
        elif rsi < 30:
            signals.append("✅ RSI超卖")
        
        return signals
    
    def _generate_sentiment_summary(self, score: SentimentScore) -> str:
        """生成情绪分析摘要"""
        summaries = {
            SentimentLevel.EXTREME_GREED: "市场情绪极度乐观，需警惕回调风险",
            SentimentLevel.GREED: "市场情绪积极，但需保持理性",
            SentimentLevel.NEUTRAL: "市场情绪平稳，观望为主",
            SentimentLevel.FEAR: "市场情绪偏悲观，可能存在错杀机会",
            SentimentLevel.EXTREME_FEAR: "市场情绪极度恐慌，或是布局良机"
        }
        return summaries.get(score.level, "情绪分析中")
    
    def _calculate_qinglong_score(
        self,
        stock_data: StockData,
        technical: TechnicalAnalysis,
        sentiment: SentimentAnalysis,
        capital_flow: CapitalFlowAnalysis,
        sector_analysis: SectorAnalysis
    ) -> float:
        """计算青龙综合分数 (0-100) - v4.2 增加板块联动权重"""

        # 技术面得分 (20%)
        tech_score = 50
        if technical.macd.get("trend") == "金叉":
            tech_score += 15
        if technical.rsi < 70 and technical.rsi > 30:
            tech_score += 10
        if technical.ma_trend == "上升趋势":
            tech_score += 10

        # 情绪面得分 (25%)
        sentiment_score = sentiment.overall_score

        # 资金流向得分 (25%)
        flow_score = capital_flow.flow_score

        # 板块联动得分 (20%) - v4.2 新增
        sector_score = sector_analysis.sector_score

        # 基本面得分 (10%)
        fund_score = 50
        if stock_data.pe_ratio and stock_data.pe_ratio < 30:
            fund_score += 15
        if stock_data.pb_ratio and stock_data.pb_ratio < 3:
            fund_score += 15
        if stock_data.change_percent > 0:
            fund_score += 10

        # 加权计算 (v4.2 新权重)
        total = (tech_score * 0.20 + sentiment_score * 0.25 +
                 flow_score * 0.25 + sector_score * 0.20 + fund_score * 0.10)
        return min(100, max(0, total))
    
    def _generate_recommendation(self, score: float, sentiment: SentimentAnalysis, capital_flow: CapitalFlowAnalysis, sector_analysis: SectorAnalysis) -> str:
        """生成投资建议 - v4.2 增加板块联动因素"""
        base_rec = ""
        if score >= 80:
            base_rec = "强烈推荐"
        elif score >= 60:
            base_rec = "推荐"
        elif score >= 40:
            base_rec = "中性"
        elif score >= 20:
            base_rec = "谨慎"
        else:
            base_rec = "回避"

        # 添加各维度说明
        flow_desc = f"资金流向{capital_flow.flow_level}"
        sentiment_desc = f"情绪{sentiment.sentiment_level}"
        sector_desc = f"板块{sector_analysis.sector_level}"

        # 添加龙头标识
        leader_tag = ""
        if sector_analysis.is_sector_leader:
            leader_tag = " [板块龙头]"
        elif sector_analysis.is_sector_follower:
            leader_tag = " [跟风]"

        return f"{base_rec}{leader_tag} - {flow_desc} | {sentiment_desc} | {sector_desc}"

# ==================== API路由 ====================

qinglong_engine = QingLongEngine()
history_db = HistoryDatabase()
backtest_engine = BacktestEngine(history_db)
alert_engine = AlertEngine()
alert_engine.add_handler(console_alert_handler)

@app.get("/")
def root():
    return {
        "message": "青龙 Stock MCP Server 运行中",
        "version": "4.4.0",
        "features": ["实时行情", "技术分析", "舆情情绪分析", "资金流向分析", "板块联动分析", "历史回测", "预警系统", "青龙评分"]
    }

@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/stock/{code}", response_model=QingLongReport)
def get_stock_analysis(code: str):
    """获取股票完整分析报告"""
    return qinglong_engine.analyze_stock(code)

@app.get("/stock/{code}/data", response_model=StockData)
def get_stock_data(code: str):
    """获取股票基础数据"""
    raw_data = fetch_stock_data_tencent(code)
    if not raw_data:
        raise HTTPException(status_code=404, detail=f"无法获取股票 {code} 的数据")
    return StockData(**raw_data)

@app.get("/stock/{code}/technical", response_model=TechnicalAnalysis)
def get_technical_analysis(code: str):
    """获取技术分析"""
    report = qinglong_engine.analyze_stock(code)
    return report.technical

@app.get("/stock/{code}/sentiment", response_model=SentimentAnalysis)
def get_sentiment_analysis(code: str):
    """获取舆情情绪分析"""
    report = qinglong_engine.analyze_stock(code)
    return report.sentiment

@app.get("/stock/{code}/capitalflow", response_model=CapitalFlowAnalysis)
def get_capital_flow_analysis(code: str):
    """获取资金流向分析"""
    report = qinglong_engine.analyze_stock(code)
    return report.capital_flow

@app.get("/stock/{code}/sector", response_model=SectorAnalysis)
def get_sector_analysis(code: str):
    """获取板块联动分析"""
    report = qinglong_engine.analyze_stock(code)
    return report.sector_analysis

@app.get("/sectors/hot")
def get_hot_sectors():
    """获取热门板块排名"""
    analyzer = SectorAnalyzer()
    sectors = analyzer.fetch_sectors("industry", top_n=20)
    return {
        "timestamp": datetime.now().isoformat(),
        "sectors": [
            {
                "rank": i + 1,
                "code": s.code,
                "name": s.name,
                "change_percent": s.change_percent,
                "main_inflow": s.main_inflow,
                "market_cap": s.total_market_cap
            }
            for i, s in enumerate(sectors)
        ]
    }

@app.get("/sectors/{sector_code}/stocks")
def get_sector_stocks(sector_code: str):
    """获取板块成分股"""
    analyzer = SectorAnalyzer()
    stocks = analyzer.fetch_sector_stocks(sector_code, top_n=30)
    return {
        "sector_code": sector_code,
        "timestamp": datetime.now().isoformat(),
        "stocks": stocks
    }

@app.get("/watchlist")
def get_watchlist():
    """获取自选股列表"""
    return {
        "stocks": [
            {"code": code, "name": name}
            for code, name in STOCK_WATCHLIST.items()
        ],
        "count": len(STOCK_WATCHLIST)
    }

@app.get("/batch/analysis")
def batch_analysis():
    """批量分析所有自选股"""
    results = []
    for code in STOCK_WATCHLIST.keys():
        try:
            report = qinglong_engine.analyze_stock(code)
            results.append({
                "code": code,
                "name": report.stock_data.name,
                "price": report.stock_data.price,
                "change_percent": report.stock_data.change_percent,
                "qinglong_score": report.qinglong_score,
                "flow_score": report.capital_flow.flow_score,
                "flow_level": report.capital_flow.flow_level,
                "sentiment_level": report.sentiment.sentiment_level,
                "sector_level": report.sector_analysis.sector_level,
                "is_sector_leader": report.sector_analysis.is_sector_leader,
                "recommendation": report.recommendation
            })
        except Exception as e:
            results.append({
                "code": code,
                "error": str(e)
            })

    # 按青龙分数排序
    results.sort(key=lambda x: x.get("qinglong_score", 0), reverse=True)

    return {
        "timestamp": datetime.now().isoformat(),
        "total": len(STOCK_WATCHLIST),
        "analyzed": len([r for r in results if "error" not in r]),
        "ranking": results
    }


# ==================== 历史回测API ====================

@app.post("/history/save/{code}")
def save_analysis_history(code: str):
    """保存当前分析到历史记录"""
    try:
        report = qinglong_engine.analyze_stock(code)

        record = HistoricalRecord(
            code=code,
            name=report.stock_data.name,
            timestamp=datetime.now().isoformat(),
            price=report.stock_data.price,
            change_percent=report.stock_data.change_percent,
            qinglong_score=report.qinglong_score,
            tech_score=50,  # 简化处理
            sentiment_score=report.sentiment.overall_score,
            flow_score=report.capital_flow.flow_score,
            sector_score=report.sector_analysis.sector_score,
            fund_score=50,  # 简化处理
            main_inflow=report.capital_flow.main_inflow,
            main_inflow_percent=report.capital_flow.main_inflow_percent,
            northbound_hold_percent=report.capital_flow.northbound_hold_percent,
            sector_name=report.sector_analysis.best_sector,
            sector_rank=report.sector_analysis.sector_rank,
            is_sector_leader=report.sector_analysis.is_sector_leader,
            recommendation=report.recommendation
        )

        record_id = history_db.save_record(record)

        return {
            "success": True,
            "record_id": record_id,
            "code": code,
            "timestamp": record.timestamp
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/history/{code}")
def get_analysis_history(code: str, limit: int = 100):
    """获取股票历史分析记录"""
    records = history_db.get_records(code=code, limit=limit)
    return {
        "code": code,
        "count": len(records),
        "records": [
            {
                "id": r.id,
                "timestamp": r.timestamp,
                "price": r.price,
                "qinglong_score": r.qinglong_score,
                "recommendation": r.recommendation,
                "future_1d_return": r.future_1d_return,
                "future_5d_return": r.future_5d_return
            }
            for r in records
        ]
    }


@app.get("/backtest/{code}")
def get_backtest_report(code: str, days: int = 30, min_score: float = 60):
    """获取回测报告"""
    result = backtest_engine.calculate_backtest(
        code=code,
        min_score=min_score,
        days=days
    )

    return {
        "code": code,
        "days": days,
        "min_score": min_score,
        "total_signals": result.total_signals,
        "win_rates": {
            "1d": result.win_rate_1d,
            "3d": result.win_rate_3d,
            "5d": result.win_rate_5d,
            "10d": result.win_rate_10d
        },
        "avg_returns": {
            "1d": result.avg_return_1d,
            "3d": result.avg_return_3d,
            "5d": result.avg_return_5d,
            "10d": result.avg_return_10d
        },
        "max_drawdowns": {
            "1d": result.max_drawdown_1d,
            "3d": result.max_drawdown_3d,
            "5d": result.max_drawdown_5d,
            "10d": result.max_drawdown_10d
        },
        "score_accuracy": result.score_accuracy,
        "recommendation_win_rates": {
            "strong_buy": result.strong_buy_win_rate,
            "buy": result.buy_win_rate,
            "neutral": result.neutral_win_rate,
            "sell": result.sell_win_rate
        }
    }


# ==================== 预警系统API ====================

@app.get("/alerts/rules")
def get_alert_rules(code: str = None, enabled_only: bool = True):
    """获取预警规则列表"""
    rules = alert_engine.get_rules(code=code, enabled_only=enabled_only)
    return {
        "count": len(rules),
        "rules": [
            {
                "id": r.id,
                "name": r.name,
                "code": r.code,
                "alert_type": r.alert_type.value,
                "level": r.level.value,
                "threshold_value": r.threshold_value,
                "threshold_direction": r.threshold_direction,
                "enabled": r.enabled,
                "cooldown_minutes": r.cooldown_minutes,
                "trigger_count": r.trigger_count,
                "last_triggered": r.last_triggered
            }
            for r in rules
        ]
    }


@app.post("/alerts/rules")
def create_alert_rule(rule: dict):
    """创建预警规则"""
    try:
        new_rule = AlertRule(
            id=rule.get("id", f"rule_{datetime.now().timestamp()}"),
            name=rule.get("name", ""),
            code=rule.get("code", ""),
            alert_type=AlertType(rule.get("alert_type", "price_change")),
            level=AlertLevel(rule.get("level", "warning")),
            threshold_value=rule.get("threshold_value", 0),
            threshold_direction=rule.get("threshold_direction", "above"),
            cooldown_minutes=rule.get("cooldown_minutes", 60),
            enabled=rule.get("enabled", True),
            description=rule.get("description", "")
        )

        rule_id = alert_engine.add_rule(new_rule)
        return {"success": True, "rule_id": rule_id}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.delete("/alerts/rules/{rule_id}")
def delete_alert_rule(rule_id: str):
    """删除预警规则"""
    success = alert_engine.remove_rule(rule_id)
    return {"success": success}


@app.get("/alerts/events")
def get_alert_events(code: str = None, limit: int = 100):
    """获取预警事件历史"""
    events = alert_engine.get_events(code=code, limit=limit)
    return {
        "count": len(events),
        "events": [
            {
                "id": e.id,
                "rule_id": e.rule_id,
                "code": e.code,
                "name": e.name,
                "alert_type": e.alert_type.value,
                "level": e.level.value,
                "message": e.message,
                "trigger_value": e.trigger_value,
                "timestamp": e.timestamp
            }
            for e in events
        ]
    }


@app.post("/alerts/check/{code}")
def check_alerts(code: str):
    """手动检查预警（用于测试）"""
    try:
        # 获取股票分析数据
        report = qinglong_engine.analyze_stock(code)

        # 构建检测数据
        data = {
            "name": report.stock_data.name,
            "price": report.stock_data.price,
            "change_percent": report.stock_data.change_percent,
            "volume": report.stock_data.volume,
            "sentiment_score": report.sentiment.overall_score,
            "flow_score": report.capital_flow.flow_score,
            "sector_rank": report.sector_analysis.sector_rank,
            "qinglong_score": report.qinglong_score,
            "rsi": report.technical.rsi
        }

        # 检查预警
        events = alert_engine.check_alerts(code, data)

        return {
            "code": code,
            "checked_at": datetime.now().isoformat(),
            "alerts_triggered": len(events),
            "events": [
                {
                    "type": e.alert_type.value,
                    "level": e.level.value,
                    "message": e.message
                }
                for e in events
            ]
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==================== 主程序 ====================

if __name__ == "__main__":
    print("🐉 青龙 Stock MCP Server v4.4.0 启动中...")
    print("功能: 实时行情 | 技术分析 | 舆情情绪分析 | 资金流向分析 | 板块联动分析 | 历史回测 | 预警系统 | 青龙评分")
    uvicorn.run(app, host="0.0.0.0", port=8000)
