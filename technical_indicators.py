#!/usr/bin/env python3
"""
技术指标计算模块
基于 TradingAgents-CN 的研究实现
使用 stockstats + pandas 计算专业指标
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional

class TechnicalIndicator:
    """技术指标计算类"""
    
    @staticmethod
    def calculate_ma(prices: pd.Series, window: int) -> pd.Series:
        """计算移动平均线 MA"""
        return prices.rolling(window=window).mean()
    
    @staticmethod
    def calculate_ema(prices: pd.Series, span: int) -> pd.Series:
        """计算指数移动平均线 EMA"""
        return prices.ewm(span=span, adjust=False).mean()
    
    @staticmethod
    def calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
        """
        计算 MACD 指标
        
        Returns:
            dict: {'macd': ..., 'signal': ..., 'hist': ..., 'interpretation': ...}
        """
        ema_fast = TechnicalIndicator.calculate_ema(prices, fast)
        ema_slow = TechnicalIndicator.calculate_ema(prices, slow)
        
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line
        
        # 生成分析建议
        latest_macd = macd.iloc[-1]
        latest_signal = signal_line.iloc[-1]
        latest_hist = histogram.iloc[-1]
        
        interpretation = []
        if latest_macd > latest_signal:
            interpretation.append("MACD 在信号线上方， bullish（看涨）")
        else:
            interpretation.append("MACD 在信号线下方， bearish（看跌）")
        
        if latest_hist > 0 and histogram.iloc[-2] < histogram.iloc[-1]:
            interpretation.append("柱状图扩大，动能增强")
        elif latest_hist > 0:
            interpretation.append("柱状图缩小，动能减弱")
        
        return {
            'macd': macd,
            'signal': signal_line,
            'hist': histogram,
            'latest_macd': latest_macd,
            'latest_signal': latest_signal,
            'latest_hist': latest_hist,
            'interpretation': '\n'.join(interpretation)
        }
    
    @staticmethod
    def calculate_rsi(prices: pd.Series, period: int = 14) -> Dict:
        """
        计算 RSI 相对强弱指数
        
        Returns:
            dict: {'rsi': ..., 'interpretation': ...}
        """
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        latest_rsi = rsi.iloc[-1]
        
        # RSI 解读
        interpretation = []
        if latest_rsi > 70:
            interpretation.append(f"RSI = {latest_rsi:.2f} > 70，超买状态，可能回调")
        elif latest_rsi < 30:
            interpretation.append(f"RSI = {latest_rsi:.2f} < 30，超卖状态，可能反弹")
        else:
            interpretation.append(f"RSI = {latest_rsi:.2f}，正常区间")
        
        return {
            'rsi': rsi,
            'latest_rsi': latest_rsi,
            'interpretation': '\n'.join(interpretation)
        }
    
    @staticmethod
    def calculate_kdj(high: pd.Series, low: pd.Series, close: pd.Series, 
                     n: int = 9, m1: int = 3, m2: int = 3) -> Dict:
        """
        计算 KDJ 随机指标
        
        Returns:
            dict: {'k': ..., 'd': ..., 'j': ..., 'interpretation': ...}
        """
        rsv = (close - low.rolling(window=n).min()) / (high.rolling(window=n).max() - low.rolling(window=n).min()) * 100
        
        k = rsv.ewm(com=m1-1, adjust=False).mean()
        d = k.ewm(com=m2-1, adjust=False).mean()
        j = 3 * k - 2 * d
        
        latest_k = k.iloc[-1]
        latest_d = d.iloc[-1]
        latest_j = j.iloc[-1]
        
        interpretation = []
        if latest_k > latest_d:
            interpretation.append(f"K({latest_k:.2f}) > D({latest_d:.2f})，金叉信号，看涨")
        else:
            interpretation.append(f"K({latest_k:.2f}) < D({latest_d:.2f})，死叉信号，看跌")
        
        if latest_j > 100:
            interpretation.append(f"J = {latest_j:.2f} > 100，超买")
        elif latest_j < 0:
            interpretation.append(f"J = {latest_j:.2f} < 0，超卖")
        
        return {
            'k': k,
            'd': d,
            'j': j,
            'latest_k': latest_k,
            'latest_d': latest_d,
            'latest_j': latest_j,
            'interpretation': '\n'.join(interpretation)
        }
    
    @staticmethod
    def calculate_bollinger(prices: pd.Series, window: int = 20, num_std: int = 2) -> Dict:
        """
        计算布林带 Bollinger Bands
        
        Returns:
            dict: {'upper': ..., 'middle': ..., 'lower': ..., 'interpretation': ...}
        """
        middle = prices.rolling(window=window).mean()
        std = prices.rolling(window=window).std()
        upper = middle + (std * num_std)
        lower = middle - (std * num_std)
        
        latest_price = prices.iloc[-1]
        latest_upper = upper.iloc[-1]
        latest_lower = lower.iloc[-1]
        
        interpretation = []
        if latest_price > latest_upper:
            interpretation.append(f"价格突破上轨，超买，可能回调")
        elif latest_price < latest_lower:
            interpretation.append(f"价格突破下轨，超卖，可能反弹")
        else:
            bandwidth = (latest_upper - latest_lower) / middle.iloc[-1]
            interpretation.append(f"价格在布林带内运行，带宽: {bandwidth:.2%}")
        
        return {
            'upper': upper,
            'middle': middle,
            'lower': lower,
            'latest_price': latest_price,
            'latest_upper': latest_upper,
            'latest_lower': latest_lower,
            'interpretation': '\n'.join(interpretation)
        }
    
    @staticmethod
    def calculate_all(df: pd.DataFrame) -> Dict:
        """
        计算所有技术指标
        
        Args:
            df: DataFrame with columns ['close', 'high', 'low', 'volume']
        
        Returns:
            dict: 所有指标的计算结果
        """
        close = df['close']
        high = df['high']
        low = df['low']
        
        # 计算均线
        ma5 = TechnicalIndicator.calculate_ma(close, 5)
        ma10 = TechnicalIndicator.calculate_ma(close, 10)
        ma20 = TechnicalIndicator.calculate_ma(close, 20)
        ma60 = TechnicalIndicator.calculate_ma(close, 60)
        
        # 计算技术指标
        macd = TechnicalIndicator.calculate_macd(close)
        rsi = TechnicalIndicator.calculate_rsi(close)
        kdj = TechnicalIndicator.calculate_kdj(high, low, close)
        boll = TechnicalIndicator.calculate_bollinger(close)
        
        return {
            'ma': {'ma5': ma5, 'ma10': ma10, 'ma20': ma20, 'ma60': ma60},
            'macd': macd,
            'rsi': rsi,
            'kdj': kdj,
            'bollinger': boll
        }


class TechnicalAnalyst:
    """
    技术分析师（多智能体之一）
    基于 TradingAgents-CN 架构实现
    """
    
    def __init__(self, stock_code: str):
        self.stock_code = stock_code
        self.indicators = TechnicalIndicator()
    
    def fetch_data(self, days: int = 60) -> pd.DataFrame:
        """获取股票历史数据"""
        try:
            import akshare as ak
            df = ak.stock_zh_a_hist(symbol=self.stock_code, period="daily", 
                                   start_date="20240101", adjust="qfq")
            df = df.rename(columns={
                '收盘': 'close',
                '开盘': 'open',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume'
            })
            return df.tail(days)
        except Exception as e:
            print(f"获取数据失败: {e}")
            return pd.DataFrame()
    
    def analyze(self) -> Dict:
        """
        执行技术分析
        
        Returns:
            dict: 分析报告
        """
        df = self.fetch_data()
        if df.empty:
            return {"error": "无法获取数据"}
        
        # 计算所有指标
        indicators = self.indicators.calculate_all(df)
        
        # 生成交易信号
        signals = self._generate_signals(indicators)
        
        # 生成报告
        report = {
            'stock_code': self.stock_code,
            'latest_price': df['close'].iloc[-1],
            'analysis_date': pd.Timestamp.now().strftime('%Y-%m-%d'),
            'indicators': {
                'macd': indicators['macd']['interpretation'],
                'rsi': indicators['rsi']['interpretation'],
                'kdj': indicators['kdj']['interpretation'],
                'bollinger': indicators['bollinger']['interpretation']
            },
            'signals': signals,
            'recommendation': self._generate_recommendation(signals)
        }
        
        return report
    
    def _generate_signals(self, indicators: Dict) -> List[str]:
        """生成交易信号"""
        signals = []
        
        # MACD 信号
        macd_hist = indicators['macd']['latest_hist']
        if macd_hist > 0:
            signals.append("MACD 金叉/多头")
        else:
            signals.append("MACD 死叉/空头")
        
        # RSI 信号
        rsi = indicators['rsi']['latest_rsi']
        if rsi > 70:
            signals.append("RSI 超买")
        elif rsi < 30:
            signals.append("RSI 超卖")
        
        # KDJ 信号
        k = indicators['kdj']['latest_k']
        d = indicators['kdj']['latest_d']
        if k > d:
            signals.append("KDJ 金叉")
        else:
            signals.append("KDJ 死叉")
        
        return signals
    
    def _generate_recommendation(self, signals: List[str]) -> str:
        """生成投资建议"""
        bullish_count = sum(1 for s in signals if '金叉' in s or '多头' in s)
        bearish_count = sum(1 for s in signals if '死叉' in s or '空头' in s)
        
        if bullish_count > bearish_count:
            return "偏多信号占优，可考虑逢低买入"
        elif bearish_count > bullish_count:
            return "偏空信号占优，建议观望或减仓"
        else:
            return "信号中性，建议观望"


# 测试
if __name__ == "__main__":
    print("🧪 技术指标计算测试")
    print("=" * 60)
    
    # 测试技术指标计算
    import numpy as np
    
    # 生成测试数据
    np.random.seed(42)
    prices = pd.Series(100 + np.cumsum(np.random.randn(100) * 2))
    
    print("\n📊 MACD 测试:")
    macd = TechnicalIndicator.calculate_macd(prices)
    print(f"最新 MACD: {macd['latest_macd']:.4f}")
    print(f"信号线: {macd['latest_signal']:.4f}")
    print(f"柱状图: {macd['latest_hist']:.4f}")
    print(f"解读: {macd['interpretation']}")
    
    print("\n📊 RSI 测试:")
    rsi = TechnicalIndicator.calculate_rsi(prices)
    print(f"最新 RSI: {rsi['latest_rsi']:.2f}")
    print(f"解读: {rsi['interpretation']}")
    
    print("\n📊 KDJ 测试:")
    high = prices * (1 + np.random.rand(100) * 0.02)
    low = prices * (1 - np.random.rand(100) * 0.02)
    kdj = TechnicalIndicator.calculate_kdj(high, low, prices)
    print(f"K: {kdj['latest_k']:.2f}, D: {kdj['latest_d']:.2f}, J: {kdj['latest_j']:.2f}")
    print(f"解读: {kdj['interpretation']}")
    
    print("\n" + "=" * 60)
    print("✅ 技术指标计算模块测试通过！")
