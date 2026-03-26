#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票数据获取 - 腾讯财经接口（增强版，集成反爬功能）
版本: 2.0
更新: 2026-03-26 - 集成 AntiCrawler
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from typing import Dict, Optional
import logging

# 导入反爬模块
try:
    from anti_crawler import get_anti_crawler, fetch_with_protection
    ANTI_CRAWLER_AVAILABLE = True
except ImportError:
    ANTI_CRAWLER_AVAILABLE = False
    logging.warning("AntiCrawler not available, falling back to standard requests")

logger = logging.getLogger(__name__)


def get_qq_stock_price_enhanced(symbol: str, use_anti_crawler: bool = True) -> Dict:
    """
    从腾讯财经获取实时股价（增强版，支持反爬）
    
    Args:
        symbol: 股票代码，如 600519, 000001
        use_anti_crawler: 是否使用反爬功能（默认开启）
        
    Returns:
        包含股票信息的字典
    """
    try:
        # 沪市股票前缀为 sh，深市为 sz
        prefix = "sh" if symbol.startswith("6") else "sz"
        qq_symbol = f"{prefix}{symbol}"
        
        # 腾讯财经接口
        url = f"http://qt.gtimg.cn/q={qq_symbol}"
        
        # 使用反爬功能或标准请求
        if use_anti_crawler and ANTI_CRAWLER_AVAILABLE:
            logger.debug(f"Using AntiCrawler for {symbol}")
            resp = fetch_with_protection(url, timeout=10)
        else:
            import requests
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": "https://stock.finance.qq.com",
            }
            resp = requests.get(url, headers=headers, timeout=10)
        
        resp.encoding = 'gb2312'
        
        text = resp.text
        if not text or 'v_' not in text:
            return {"error": "无法获取数据"}
        
        # 腾讯返回格式: v_sh600519="1~贵州茅台~600519~1745.00~...";
        data_str = text.split('"')[1]
        fields = data_str.split("~")
        
        # 字段含义（腾讯接口）
        # 0: 未知
        # 1: 股票名称
        # 2: 股票代码
        # 3: 当前价格
        # 4: 昨收
        # 5: 今开
        # 6: 成交量（手）
        # 7: 外盘
        # 8: 内盘
        # 9: 买一
        # 10-18: 买一~买五价格和数量
        # 19-27: 卖一~卖五价格和数量
        # 28: 最近逐笔成交
        # 29: 时间
        # 30: 涨跌
        # 31: 涨跌幅
        # 32: 最高
        # 33: 最低
        # 34: 价格/成交量（手）/成交额
        # 35: 成交量（手）
        # 36: 成交额（万）
        # 37: 换手率
        # 38: 市盈率
        # 39: 未知
        # 40: 最高
        # 41: 最低
        # 42: 振幅
        # 43: 流通市值
        # 44: 总市值
        # 45: 市净率
        # 46: 涨停价
        # 47: 跌停价
        
        if len(fields) < 45:
            return {"error": "数据格式异常"}
        
        return {
            "source": "tencent",
            "symbol": symbol,
            "name": fields[1],
            "price": fields[3],
            "change": fields[30],
            "change_percent": fields[31],
            "open": fields[5],
            "high": fields[32],
            "low": fields[33],
            "volume": fields[35],
            "turnover": fields[36],
            "turnover_rate": fields[37],
            "pe": fields[38],
            "pb": fields[45],
            "market_cap": fields[44],
            "float_cap": fields[43],
            "anti_crawler_used": use_anti_crawler and ANTI_CRAWLER_AVAILABLE,
        }
        
    except Exception as e:
        logger.error(f"获取股票数据失败: {e}")
        return {"error": f"获取失败: {str(e)}"}


# 保持向后兼容 - 原函数名仍然可用
def get_qq_stock_price(symbol: str) -> Dict:
    """
    从腾讯财经获取实时股价（兼容旧版）
    
    Args:
        symbol: 股票代码
        
    Returns:
        股票信息字典
    """
    return get_qq_stock_price_enhanced(symbol, use_anti_crawler=True)


if __name__ == "__main__":
    # 测试
    logging.basicConfig(level=logging.DEBUG)
    
    test_symbols = ["600519", "000001", "000858"]
    
    print("测试增强版腾讯股票API（集成反爬）:\n")
    
    for symbol in test_symbols:
        print(f"查询: {symbol}")
        result = get_qq_stock_price(symbol)
        
        if "error" in result:
            print(f"  ❌ 错误: {result['error']}")
        else:
            print(f"  ✅ {result['name']} ({result['symbol']})")
            print(f"     价格: {result['price']}")
            print(f"     涨跌: {result['change']} ({result['change_percent']}%)")
            print(f"     反爬: {'✅' if result.get('anti_crawler_used') else '❌'}")
        print()
