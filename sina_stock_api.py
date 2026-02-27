#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票数据获取 - 新浪财经接口
绕过东方财富反爬虫，使用新浪数据源
"""

import requests
import json
from typing import Dict, Optional
import urllib3

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_sina_stock_price(symbol: str) -> Dict:
    """
    从新浪财经获取实时股价
    
    Args:
        symbol: 股票代码，如 600519, 000001
        
    Returns:
        包含股票信息的字典
    """
    try:
        # 沪市股票前缀为 sh，深市为 sz
        prefix = "sh" if symbol.startswith("6") else "sz"
        sina_symbol = f"{prefix}{symbol}"
        
        # 新浪财经接口
        url = f"https://hq.sinajs.cn/list={sina_symbol}"
        
        # 模拟浏览器请求头
        headers = {
            "Referer": "https://finance.sina.com.cn",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
        
        # 发送请求，设置超时（关闭 SSL 验证避免证书问题）
        resp = requests.get(url, headers=headers, timeout=15, verify=False)
        resp.encoding = 'gb18030'  # 新浪实际使用 GB18030 编码（从 curl 看到）
        
        # 解析返回数据
        # 格式: var hq_str_sh600519="贵州茅台,1740.00,1730.00,1745.00,1750.00,1738.00...";
        text = resp.text
        
        if not text or 'hq_str_' not in text:
            return {"error": "无法获取数据"}
        
        # 提取数据部分
        data_str = text.split('"')[1]
        if not data_str:
            return {"error": "股票不存在或已退市"}
        
        fields = data_str.split(",")
        
        # 字段含义（根据新浪财经文档）
        # 0: 股票名称
        # 1: 今日开盘价
        # 2: 昨日收盘价
        # 3: 当前价格
        # 4: 今日最高价
        # 5: 今日最低价
        # 6-7: 竞买价/竞卖价
        # 8: 成交股数
        # 9: 成交金额
        # 10-19: 买1-5价格和数量
        # 20-29: 卖1-5价格和数量
        # 30: 日期
        # 31: 时间
        
        name = fields[0]
        open_price = float(fields[1])
        prev_close = float(fields[2])
        current_price = float(fields[3])
        high = float(fields[4])
        low = float(fields[5])
        volume = int(fields[8])  # 成交量（股）
        amount = float(fields[9])  # 成交金额（元）
        
        # 计算涨跌幅
        change = current_price - prev_close
        change_percent = (change / prev_close) * 100 if prev_close > 0 else 0
        
        return {
            "symbol": symbol,
            "name": name,
            "price": current_price,
            "open": open_price,
            "prev_close": prev_close,
            "high": high,
            "low": low,
            "change": round(change, 2),
            "change_percent": round(change_percent, 2),
            "volume": volume,
            "amount": round(amount / 10000, 2),  # 转换为万元
            "source": "sina",
            "timestamp": f"{fields[30]} {fields[31]}" if len(fields) > 31 else ""
        }
        
    except requests.exceptions.Timeout:
        return {"error": "请求超时，请检查网络"}
    except requests.exceptions.ConnectionError:
        return {"error": "连接失败，无法访问新浪财经"}
    except Exception as e:
        return {"error": f"获取数据失败: {str(e)}"}

def get_sina_stock_batch(symbols: list) -> Dict:
    """
    批量获取多只股票数据
    
    Args:
        symbols: 股票代码列表，如 ["600519", "000001"]
        
    Returns:
        多只股票数据的字典
    """
    results = []
    for symbol in symbols[:10]:  # 最多10只
        data = get_sina_stock_price(symbol)
        if "error" not in data:
            results.append(data)
    
    return {
        "count": len(results),
        "stocks": results
    }

# 测试
if __name__ == "__main__":
    print("🧪 测试新浪财经接口...")
    print("-" * 60)
    
    # 测试茅台
    print("\n1. 测试茅台 (600519):")
    result = get_sina_stock_price("600519")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 测试平安银行
    print("\n2. 测试平安银行 (000001):")
    result = get_sina_stock_price("000001")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 测试批量
    print("\n3. 测试批量获取:")
    batch = get_sina_stock_batch(["600519", "000001", "000858"])
    print(json.dumps(batch, ensure_ascii=False, indent=2))