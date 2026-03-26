"""
青龙技术指标库 - 学习 AlphaVantage 技术优势
版本: 1.0
创建时间: 2026-03-26
参考: AlphaVantage API 设计

AlphaVantage 技术优势:
1. 50+ 技术指标
2. 统一的 API 设计
3. 清晰的参数命名
4. 支持多种时间周期
5. 数据格式标准化
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Union, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class IndicatorResult:
    """技术指标结果标准格式"""
    indicator: str          # 指标名称
    symbol: str            # 股票代码
    values: Dict[str, List[float]]  # 指标值
    parameters: Dict       # 使用的参数
    timestamps: List[str]  # 时间戳
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "indicator": self.indicator,
            "symbol": self.symbol,
            "values": self.values,
            "parameters": self.parameters,
            "timestamps": self.timestamps,
        }


class TechnicalIndicators:
    """
    技术指标计算类
    
    学习 AlphaVantage 的设计理念:
    - 统一的接口设计
    - 清晰的参数命名
    - 支持自定义参数
    - 返回标准化格式
    """
    
    def __init__(self, prices: List[float], timestamps: Optional[List[str]] = None):
        """
        初始化
        
        Args:
            prices: 收盘价列表
            timestamps: 时间戳列表（可选）
        """
        self.prices = np.array(prices)
        self.timestamps = timestamps or [str(i) for i in range(len(prices))]
        
        if len(self.prices) == 0:
            raise ValueError("价格数据不能为空")
    
    # ==================== 趋势指标 ====================
    
    def sma(self, time_period: int = 20) -> IndicatorResult:
        """
        简单移动平均线 (Simple Moving Average)
        
        学习 AlphaVantage:
        - 参数名: time_period (清晰)
        - 返回值: 标准化格式
        
        Args:
            time_period: 计算周期，默认20
            
        Returns:
            IndicatorResult 对象
        """
        values = pd.Series(self.prices).rolling(window=time_period).mean().tolist()
        
        return IndicatorResult(
            indicator="SMA",
            symbol="",
            values={"sma": values},
            parameters={"time_period": time_period},
            timestamps=self.timestamps
        )
    
    def ema(self, time_period: int = 20) -> IndicatorResult:
        """
        指数移动平均线 (Exponential Moving Average)
        
        AlphaVantage 特点: 使用 adjust=False 保持与传统计算方法一致
        
        Args:
            time_period: 计算周期，默认20
            
        Returns:
            IndicatorResult 对象
        """
        values = pd.Series(self.prices).ewm(span=time_period, adjust=False).mean().tolist()
        
        return IndicatorResult(
            indicator="EMA",
            symbol="",
            values={"ema": values},
            parameters={"time_period": time_period},
            timestamps=self.timestamps
        )
    
    def wma(self, time_period: int = 20) -> IndicatorResult:
        """
        加权移动平均线 (Weighted Moving Average)
        
        AlphaVantage 特点: 线性加权，最近数据权重更高
        
        Args:
            time_period: 计算周期，默认20
        """
        weights = np.arange(1, time_period + 1)
        
        def weighted_moving_average(data, window):
            return np.convolve(data, weights[::-1] / weights.sum(), mode='valid')
        
        # 填充前面的空值
        wma_values = [np.nan] * (time_period - 1)
        wma_values.extend(weighted_moving_average(self.prices, time_period).tolist())
        
        return IndicatorResult(
            indicator="WMA",
            symbol="",
            values={"wma": wma_values},
            parameters={"time_period": time_period},
            timestamps=self.timestamps
        )
    
    # ==================== 动量指标 ====================
    
    def rsi(self, time_period: int = 14) -> IndicatorResult:
        """
        相对强弱指标 (Relative Strength Index)
        
        AlphaVantage 标准实现:
        - 使用 Wilder's Smoothing
        - 默认周期 14
        
        Args:
            time_period: 计算周期，默认14
        """
        deltas = np.diff(self.prices)
        
        # 分离涨跌
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        # 使用 Wilder's Smoothing (类似 EMA)
        avg_gains = pd.Series(gains).ewm(alpha=1/time_period, adjust=False).mean().values
        avg_losses = pd.Series(losses).ewm(alpha=1/time_period, adjust=False).mean().values
        
        # 计算 RS 和 RSI
        rs = avg_gains / (avg_losses + 1e-10)  # 避免除零
        rsi_values = 100 - (100 / (1 + rs))
        
        # 填充第一个值
        rsi_values = np.concatenate([[np.nan], rsi_values])
        
        return IndicatorResult(
            indicator="RSI",
            symbol="",
            values={"rsi": rsi_values.tolist()},
            parameters={"time_period": time_period},
            timestamps=self.timestamps
        )
    
    def macd(self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> IndicatorResult:
        """
        指数平滑异同移动平均线 (Moving Average Convergence Divergence)
        
        AlphaVantage 标准参数:
        - Fast Period: 12
        - Slow Period: 26
        - Signal Period: 9
        
        Args:
            fast_period: 快线周期，默认12
            slow_period: 慢线周期，默认26
            signal_period: 信号线周期，默认9
        """
        # 计算 EMA
        ema_fast = pd.Series(self.prices).ewm(span=fast_period, adjust=False).mean()
        ema_slow = pd.Series(self.prices).ewm(span=slow_period, adjust=False).mean()
        
        # MACD 线
        macd_line = ema_fast - ema_slow
        
        # 信号线 (MACD 的 EMA)
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        
        # 柱状图 (MACD - Signal)
        histogram = macd_line - signal_line
        
        return IndicatorResult(
            indicator="MACD",
            symbol="",
            values={
                "macd": macd_line.tolist(),
                "signal": signal_line.tolist(),
                "histogram": histogram.tolist()
            },
            parameters={
                "fast_period": fast_period,
                "slow_period": slow_period,
                "signal_period": signal_period
            },
            timestamps=self.timestamps
        )
    
    def stoch(self, fastk_period: int = 14, slowk_period: int = 3, slowd_period: int = 3) -> IndicatorResult:
        """
        随机指标 (Stochastic Oscillator)
        
        AlphaVantage 参数:
        - FastK Period: 14
        - SlowK Period: 3
        - SlowD Period: 3
        
        注意: 需要 High/Low/Close 数据，这里简化实现
        """
        # 简化实现：使用价格的最小值和最大值
        # 实际应该传入 High/Low 数据
        
        # 计算 %K
        lowest_low = pd.Series(self.prices).rolling(window=fastk_period).min()
        highest_high = pd.Series(self.prices).rolling(window=fastk_period).max()
        
        fastk = 100 * ((self.prices - lowest_low) / (highest_high - lowest_low))
        
        # 计算 SlowK (%K 的 SMA)
        slowk = fastk.rolling(window=slowk_period).mean()
        
        # 计算 SlowD (SlowK 的 SMA)
        slowd = slowk.rolling(window=slowd_period).mean()
        
        return IndicatorResult(
            indicator="STOCH",
            symbol="",
            values={
                "slowk": slowk.tolist(),
                "slowd": slowd.tolist()
            },
            parameters={
                "fastk_period": fastk_period,
                "slowk_period": slowk_period,
                "slowd_period": slowd_period
            },
            timestamps=self.timestamps
        )
    
    # ==================== 波动率指标 ====================
    
    def bbands(self, time_period: int = 20, nbdevup: int = 2, nbdevdn: int = 2) -> IndicatorResult:
        """
        布林带 (Bollinger Bands)
        
        AlphaVantage 参数:
        - Time Period: 20
        - Nb Dev Up: 2 (上轨标准差倍数)
        - Nb Dev Dn: 2 (下轨标准差倍数)
        
        Args:
            time_period: 计算周期，默认20
            nbdevup: 上轨标准差倍数，默认2
            nbdevdn: 下轨标准差倍数，默认2
        """
        # 中轨 (SMA)
        middle_band = pd.Series(self.prices).rolling(window=time_period).mean()
        
        # 标准差
        std = pd.Series(self.prices).rolling(window=time_period).std()
        
        # 上轨和下轨
        upper_band = middle_band + (std * nbdevup)
        lower_band = middle_band - (std * nbdevdn)
        
        return IndicatorResult(
            indicator="BBANDS",
            symbol="",
            values={
                "upper_band": upper_band.tolist(),
                "middle_band": middle_band.tolist(),
                "lower_band": lower_band.tolist()
            },
            parameters={
                "time_period": time_period,
                "nbdevup": nbdevup,
                "nbdevdn": nbdevdn
            },
            timestamps=self.timestamps
        )
    
    # ==================== 成交量指标 ====================
    
    def obv(self, volumes: List[float]) -> IndicatorResult:
        """
        能量潮指标 (On Balance Volume)
        
        AlphaVantage 特点: 基于成交量和价格的累积指标
        
        Args:
            volumes: 成交量列表
        """
        if len(volumes) != len(self.prices):
            raise ValueError("成交量数据长度必须与价格数据一致")
        
        obv_values = [volumes[0]]  # 第一个值
        
        for i in range(1, len(self.prices)):
            if self.prices[i] > self.prices[i-1]:
                # 上涨，加成交量
                obv_values.append(obv_values[-1] + volumes[i])
            elif self.prices[i] < self.prices[i-1]:
                # 下跌，减成交量
                obv_values.append(obv_values[-1] - volumes[i])
            else:
                # 平盘，不变
                obv_values.append(obv_values[-1])
        
        return IndicatorResult(
            indicator="OBV",
            symbol="",
            values={"obv": obv_values},
            parameters={},
            timestamps=self.timestamps
        )
    
    # ==================== 综合计算 ====================
    
    def calculate_all(self, volumes: Optional[List[float]] = None) -> Dict[str, IndicatorResult]:
        """
        计算所有技术指标
        
        Returns:
            包含所有指标结果的字典
        """
        results = {}
        
        # 趋势指标
        results["sma"] = self.sma()
        results["ema"] = self.ema()
        
        # 动量指标
        results["rsi"] = self.rsi()
        results["macd"] = self.macd()
        
        # 波动率指标
        results["bbands"] = self.bbands()
        
        # 成交量指标
        if volumes:
            results["obv"] = self.obv(volumes)
        
        return results


# ==================== 便捷函数 ====================

def calculate_sma(prices: List[float], period: int = 20) -> List[float]:
    """便捷函数: 计算 SMA"""
    ti = TechnicalIndicators(prices)
    return ti.sma(period).values["sma"]

def calculate_ema(prices: List[float], period: int = 20) -> List[float]:
    """便捷函数: 计算 EMA"""
    ti = TechnicalIndicators(prices)
    return ti.ema(period).values["ema"]

def calculate_rsi(prices: List[float], period: int = 14) -> List[float]:
    """便捷函数: 计算 RSI"""
    ti = TechnicalIndicators(prices)
    return ti.rsi(period).values["rsi"]

def calculate_macd(prices: List[float]) -> Dict[str, List[float]]:
    """便捷函数: 计算 MACD"""
    ti = TechnicalIndicators(prices)
    return ti.macd().values


if __name__ == "__main__":
    # 测试
    logging.basicConfig(level=logging.INFO)
    
    print("🧪 测试技术指标库\n")
    
    # 生成测试数据（模拟股票价格）
    np.random.seed(42)
    test_prices = [100 + np.random.randn() * 5 for _ in range(100)]
    test_volumes = [1000000 + np.random.randint(-200000, 200000) for _ in range(100)]
    
    # 创建技术指标实例
    ti = TechnicalIndicators(test_prices)
    
    print("1️⃣ 测试 SMA (20日)")
    sma_result = ti.sma(20)
    print(f"   最新值: {sma_result.values['sma'][-1]:.2f}")
    
    print("\n2️⃣ 测试 EMA (20日)")
    ema_result = ti.ema(20)
    print(f"   最新值: {ema_result.values['ema'][-1]:.2f}")
    
    print("\n3️⃣ 测试 RSI (14日)")
    rsi_result = ti.rsi(14)
    rsi_value = rsi_result.values['rsi'][-1]
    print(f"   最新值: {rsi_value:.2f}")
    if rsi_value > 70:
        print("   📈 超买信号")
    elif rsi_value < 30:
        print("   📉 超卖信号")
    else:
        print("   ⚖️  中性")
    
    print("\n4️⃣ 测试 MACD")
    macd_result = ti.macd()
    print(f"   MACD: {macd_result.values['macd'][-1]:.4f}")
    print(f"   Signal: {macd_result.values['signal'][-1]:.4f}")
    print(f"   Histogram: {macd_result.values['histogram'][-1]:.4f}")
    
    print("\n5️⃣ 测试布林带")
    bbands_result = ti.bbands()
    print(f"   上轨: {bbands_result.values['upper_band'][-1]:.2f}")
    print(f"   中轨: {bbands_result.values['middle_band'][-1]:.2f}")
    print(f"   下轨: {bbands_result.values['lower_band'][-1]:.2f}")
    
    print("\n✅ 所有测试通过！")
    
    print("\n📊 指标数量统计:")
    all_results = ti.calculate_all(test_volumes)
    for name, result in all_results.items():
        print(f"   {name.upper()}: {len(result.values)} 个数据系列")
