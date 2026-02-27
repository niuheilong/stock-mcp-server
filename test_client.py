#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stock MCP Server - 测试客户端
用于测试所有工具功能
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_health():
    """测试健康检查"""
    print("=" * 60)
    print("测试 1: 健康检查")
    print("=" * 60)
    try:
        resp = requests.get(f"{BASE_URL}/health")
        print(f"状态: {resp.status_code}")
        print(f"响应: {resp.json()}")
        return resp.status_code == 200
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_list_tools():
    """测试列出工具"""
    print("\n" + "=" * 60)
    print("测试 2: 列出所有工具")
    print("=" * 60)
    try:
        resp = requests.get(f"{BASE_URL}/mcp/tools")
        data = resp.json()
        print(f"状态: {resp.status_code}")
        print(f"工具数量: {len(data['tools'])}")
        for tool in data['tools']:
            print(f"  - {tool['name']}: {tool['description']}")
        return True
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_get_stock_price(symbol):
    """测试获取股价"""
    print("\n" + "=" * 60)
    print(f"测试 3: 获取股价 - {symbol}")
    print("=" * 60)
    try:
        resp = requests.post(
            f"{BASE_URL}/mcp/call",
            json={"tool": "get_stock_price", "args": {"symbol": symbol}}
        )
        data = resp.json()
        result = data.get('result', {})
        
        if 'error' in result:
            print(f"❌ 错误: {result['error']}")
            return False
        
        print(f"股票: {result['name']} ({result['symbol']})")
        print(f"当前价: {result['price']}")
        print(f"涨跌: {result['change']} ({result['change_percent']}%)")
        print(f"成交量: {result['volume']}")
        print(f"成交额: {result['turnover']} 亿")
        print(f"市值: {result['market_cap']} 亿")
        print(f"PE: {result['pe_ratio']}")
        print(f"PB: {result['pb_ratio']}")
        return True
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_search_stock(keyword):
    """测试搜索股票"""
    print("\n" + "=" * 60)
    print(f"测试 4: 搜索股票 - {keyword}")
    print("=" * 60)
    try:
        resp = requests.post(
            f"{BASE_URL}/mcp/call",
            json={"tool": "search_stock", "args": {"keyword": keyword, "limit": 5}}
        )
        data = resp.json()
        result = data.get('result', {})
        
        if 'error' in result:
            print(f"❌ 错误: {result['error']}")
            return False
        
        print(f"关键词: {result['keyword']}")
        print(f"找到 {result['count']} 只股票:")
        for stock in result['results']:
            print(f"  - {stock['symbol']} {stock['name']}: {stock['price']} ({stock['change_percent']}%)")
        return True
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_get_stock_info(symbol):
    """测试获取股票信息"""
    print("\n" + "=" * 60)
    print(f"测试 5: 获取股票信息 - {symbol}")
    print("=" * 60)
    try:
        resp = requests.post(
            f"{BASE_URL}/mcp/call",
            json={"tool": "get_stock_info", "args": {"symbol": symbol}}
        )
        data = resp.json()
        result = data.get('result', {})
        
        if 'error' in result:
            print(f"❌ 错误: {result['error']}")
            return False
        
        print(f"股票: {result['name']} ({result['symbol']})")
        print(f"行业: {result['industry']}")
        print(f"市值: {result['market_cap']} 亿")
        print(f"PE: {result['pe_ratio']}")
        print(f"PB: {result['pb_ratio']}")
        print(f"换手率: {result['turnover_rate']}%")
        return True
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_get_stock_kline(symbol):
    """测试获取K线数据"""
    print("\n" + "=" * 60)
    print(f"测试 6: 获取K线数据 - {symbol}")
    print("=" * 60)
    try:
        resp = requests.post(
            f"{BASE_URL}/mcp/call",
            json={"tool": "get_stock_kline", "args": {"symbol": symbol, "days": 5}}
        )
        data = resp.json()
        result = data.get('result', {})
        
        if 'error' in result:
            print(f"❌ 错误: {result['error']}")
            return False
        
        print(f"股票: {result['symbol']}")
        print(f"周期: {result['period']}")
        print(f"数据条数: {result['count']}")
        print("最近5天数据:")
        for k in result['data'][-5:]:
            print(f"  {k['date']}: 开{k['open']:.2f} 收{k['close']:.2f} 高{k['high']:.2f} 低{k['low']:.2f} 量{k['volume']}")
        return True
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def main():
    """运行所有测试"""
    print("🧪 Stock MCP Server 测试客户端")
    print("=" * 60)
    print(f"服务地址: {BASE_URL}")
    print("=" * 60)
    
    results = []
    
    # 测试1: 健康检查
    results.append(("健康检查", test_health()))
    
    # 测试2: 列出工具
    results.append(("列出工具", test_list_tools()))
    
    # 测试3: 获取股价（茅台）
    results.append(("获取股价(600519)", test_get_stock_price("600519")))
    
    # 测试4: 搜索股票
    results.append(("搜索股票(平安)", test_search_stock("平安")))
    
    # 测试5: 获取股票信息
    results.append(("获取信息(000001)", test_get_stock_info("000001")))
    
    # 测试6: 获取K线
    results.append(("获取K线(600519)", test_get_stock_kline("600519")))
    
    # 总结
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    passed = sum(1 for _, r in results if r)
    total = len(results)
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status}: {name}")
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！")
    else:
        print("⚠️ 部分测试失败，请检查日志")

if __name__ == "__main__":
    main()