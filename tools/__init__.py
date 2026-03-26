"""
青龙工具库 - 通用工具集合

使用示例:
    from tools import AntiCrawler, TechnicalIndicators
    
    # 使用反爬功能
    crawler = AntiCrawler()
    response = crawler.get("https://example.com")
    
    # 使用技术指标
    ti = TechnicalIndicators(prices)
    rsi = ti.rsi()
"""

from .anti_crawler import AntiCrawler, get_anti_crawler, fetch_with_protection
from .technical_indicators import (
    TechnicalIndicators,
    IndicatorResult,
    calculate_sma,
    calculate_ema,
    calculate_rsi,
    calculate_macd,
)

__all__ = [
    # 反爬工具
    "AntiCrawler",
    "get_anti_crawler",
    "fetch_with_protection",
    # 技术指标
    "TechnicalIndicators",
    "IndicatorResult",
    "calculate_sma",
    "calculate_ema",
    "calculate_rsi",
    "calculate_macd",
]

__version__ = "1.1.0"
