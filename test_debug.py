#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stock MCP Server - 调试测试客户端
"""

import requests
import json

# 尝试 5001 和 5001 两个端口
PORTS = [5001, 5001]
BASE_URL = None

# 自动寻找可用端口
for port in PORTS:
    try:
        resp = requests.get(f"http://localhost:{port}/health", timeout=2)
        if resp.status_code == 200:
            BASE_URL = f"http://localhost:{port}"
            print(f"✅ 找到服务器: {BASE_URL}")
            break
    except:
        pass

if not BASE_URL:
    print("❌ 错误: 无法连接到服务器")
    print("请确保服务器已启动: python3 stock_mcp_server.py")
    exit(1)

def test_health():
    """测试健康检查"""
    print("=" * 60)
    print("测试 1: 健康检查")
    print("=" * 60)
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"状态: {resp.status_code}")
        print(f"响应: {resp.text}")
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
        resp = requests.get(f"{BASE_URL}/mcp/tools", timeout=5)
        print(f"状态: {resp.status_code}")
        data = resp.json()
        print(f"工具数量: {len(data.get('tools', []))}")
        for tool in data.get('tools', [])[:3]:
            print(f"  - {tool['name']}: {tool['description'][:50]}...")
        return True
    except Exception as e:
        print(f"❌ 错误: {e}")
        print(f"响应内容: {resp.text[:200] if 'resp' in locals() else 'N/A'}")
        return False

def test_get_stock_price(symbol):
    """测试获取股价"""
    print("\n" + "=" * 60)
    print(f"测试 3: 获取股价 - {symbol}")
    print("=" * 60)
    try:
        resp = requests.post(
            f"{BASE_URL}/mcp/call",
            json={"tool": "get_stock_price", "args": {"symbol": symbol}},
            timeout=10
        )
        print(f"状态: {resp.status_code}")
        data = resp.json()
        result = data.get('result', {})
        
        if 'error' in result:
            print(f"❌ 错误: {result['error']}")
            return False
        
        print(f"✅ 成功!")
        print(f"  股票: {result.get('name')} ({result.get('symbol')})")
        print(f"  当前价: {result.get('price')}")
        print(f"  涨跌: {result.get('change')} ({result.get('change_percent')}%)")
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
            json={"tool": "search_stock", "args": {"keyword": keyword, "limit": 5}},
            timeout=10
        )
        data = resp.json()
        result = data.get('result', {})
        
        if 'error' in result:
            print(f"❌ 错误: {result['error']}")
            return False
        
        print(f"✅ 找到 {result.get('count', 0)} 只股票:")
        for stock in result.get('results', [])[:3]:
            print(f"  - {stock.get('symbol')} {stock.get('name')}: {stock.get('price')}")
        return True
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def main():
    """运行所有测试"""
    print("🧪 Stock MCP Server 调试测试")
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
    results.append(("搜索股票(茅台)", test_search_stock("茅台")))
    
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
        print("⚠️ 部分测试失败")
        print("\n排查建议:")
        print("1. 检查服务器是否还在运行")
        print("2. 查看服务器日志是否有错误")
        print("3. 确认端口 5001 或 5001 可访问")

if __name__ == "__main__":
    main()