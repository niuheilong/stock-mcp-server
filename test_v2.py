#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stock MCP Server v2.0 - 测试脚本
使用新浪财经数据源
"""

import requests
import json

BASE_URL = "http://localhost:5001"

def test_health():
    """测试健康检查"""
    print("=" * 60)
    print("测试 1: 健康检查")
    print("=" * 60)
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✅ 状态: {resp.status_code}")
        print(f"响应: {resp.json()}")
        return True
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_list_tools():
    """测试列出工具"""
    print("\n" + "=" * 60)
    print("测试 2: 列出所有工具")
    print("=" * 60)
    try:
        resp = requests.get(f"{BASE_URL}/mcp/tools", timeout=5)
        data = resp.json()
        print(f"✅ 工具数量: {len(data['tools'])}")
        for tool in data['tools']:
            print(f"  - {tool['name']}: {tool['description'][:40]}...")
        return True
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_get_stock_price_sina():
    """测试新浪股价"""
    print("\n" + "=" * 60)
    print("测试 3: 获取股价 - 茅台 (新浪财经)")
    print("=" * 60)
    try:
        resp = requests.post(
            f"{BASE_URL}/mcp/call",
            json={"tool": "get_stock_price", "args": {"symbol": "600519", "source": "sina"}},
            timeout=15
        )
        data = resp.json()
        result = data.get('result', {})
        
        if 'error' in result:
            print(f"❌ 错误: {result['error']}")
            return False
        
        print(f"✅ 成功!")
        print(f"  股票: {result['name']} ({result['symbol']})")
        print(f"  当前价: ¥{result['price']}")
        print(f"  涨跌: {result['change']} ({result['change_percent']}%)")
        print(f"  成交量: {result['volume']} 股")
        print(f"  数据源: {result.get('source', 'unknown')}")
        return True
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_get_stock_price_qq():
    """测试腾讯股价"""
    print("\n" + "=" * 60)
    print("测试 4: 获取股价 - 平安银行 (腾讯财经)")
    print("=" * 60)
    try:
        resp = requests.post(
            f"{BASE_URL}/mcp/call",
            json={"tool": "get_stock_price", "args": {"symbol": "000001", "source": "qq"}},
            timeout=15
        )
        data = resp.json()
        result = data.get('result', {})
        
        if 'error' in result:
            print(f"❌ 错误: {result['error']}")
            return False
        
        print(f"✅ 成功!")
        print(f"  股票: {result['name']} ({result['symbol']})")
        print(f"  当前价: ¥{result['price']}")
        print(f"  涨跌: {result['change']} ({result['change_percent']}%)")
        print(f"  数据源: {result.get('source', 'unknown')}")
        return True
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_search_stock():
    """测试搜索"""
    print("\n" + "=" * 60)
    print("测试 5: 搜索股票 - 茅台")
    print("=" * 60)
    try:
        resp = requests.post(
            f"{BASE_URL}/mcp/call",
            json={"tool": "search_stock", "args": {"keyword": "茅台"}},
            timeout=15
        )
        data = resp.json()
        result = data.get('result', {})
        
        print(f"✅ 找到 {result.get('count', 0)} 只股票:")
        for stock in result.get('results', []):
            print(f"  - {stock['symbol']} {stock['name']}: ¥{stock['price']} ({stock['change_percent']}%)")
        return True
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_batch_stocks():
    """测试批量获取"""
    print("\n" + "=" * 60)
    print("测试 6: 批量获取股票")
    print("=" * 60)
    try:
        resp = requests.post(
            f"{BASE_URL}/mcp/call",
            json={"tool": "get_stock_batch", "args": {"symbols": ["600519", "000001", "000858"]}},
            timeout=20
        )
        data = resp.json()
        result = data.get('result', {})
        
        print(f"✅ 成功获取 {result.get('count', 0)} 只股票")
        for stock in result.get('stocks', []):
            print(f"  - {stock['symbol']} {stock['name']}: ¥{stock['price']}")
        return True
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def main():
    print("🧪 Stock MCP Server v2.0 测试")
    print("=" * 60)
    print(f"服务地址: {BASE_URL}")
    print("数据源: 新浪财经 + 腾讯财经")
    print("=" * 60)
    
    results = []
    
    # 运行所有测试
    results.append(("健康检查", test_health()))
    results.append(("列出工具", test_list_tools()))
    results.append(("新浪股价(茅台)", test_get_stock_price_sina()))
    results.append(("腾讯股价(平安)", test_get_stock_price_qq()))
    results.append(("搜索股票", test_search_stock()))
    results.append(("批量获取", test_batch_stocks()))
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status}: {name}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 全部测试通过！服务器工作正常！")
        print("\n下一步:")
        print("1. 发布到 GitHub")
        print("2. 发布到 EvoMap")
        print("3. 商业化！")
    else:
        print(f"\n⚠️ {total - passed} 项测试失败")
        print("请检查网络连接或查看服务器日志")

if __name__ == "__main__":
    main()