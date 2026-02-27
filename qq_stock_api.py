#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票数据获取 - 腾讯财经接口
备用数据源
"""

import requests
import json
from typing import Dict

def get_qq_stock_price(symbol: str) -> Dict:
    """
    从腾讯财经获取实时股价
    
    Args:
        symbol: 股票代码，如 600519, 000001
        
    Returns:
        包含股票信息的字典
    """
    try:
        # 沪市股票前缀为 sh，深市为 sz
        prefix = "sh" if symbol.startswith("6") else "sz"
        qq_symbol = f"{prefix}{symbol}"
        
        # 腾讯财经接口
        url = f"http://qt.gtimg.cn/q={qq_symbol}"
        
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
        
        # 字段含义
        # 0: 未知
        # 1: 股票名称
        # 2: 股票代码
        # 3: 当前价格
        # 4: 昨日收盘价
        # 5: 今日开盘价
        # 6: 成交量（手）
        # 7: 外盘
        # 8: 内盘
        # 9: 买一价
        # 10-18: 买二到买五价格和数量
        # 19-27: 卖一到卖五价格和数量
        # 28-31: 最近逐笔成交
        # 32: 更新时间
        # 33: 涨跌额
        # 34: 涨跌幅
        # 35: 最高价
        # 36: 最低价
        # 37-38: 成交量和成交额（不同单位）
        
        return {
            "symbol": fields[2],
            "name": fields[1],
            "price": float(fields[3]),
            "prev_close": float(fields[4]),
            "open": float(fields[5]),
            "volume": int(fields[6]) * 100,  # 手转换为股
            "change": float(fields[33]),
            "change_percent": float(fields[34]),
            "high": float(fields[35]),
            "low": float(fields[36]),
            "source": "qq",
            "timestamp": fields[32] if len(fields) > 32 else ""
        }
        
    except Exception as e:
        return {"error": f"获取数据失败: {str(e)}"}

# 测试
if __name__ == "__main__":
    print("🧪 测试腾讯财经接口...")
    print("-" * 60)
    
    result = get_qq_stock_price("600519")
    print(json.dumps(result, ensure_ascii=False, indent=2))