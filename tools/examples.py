#!/usr/bin/env python3
"""
反爬能力使用示例
展示如何在其他任务中复用 AntiCrawler
"""

import sys
import os

# 添加项目根目录到路径（如果在项目外使用）
# sys.path.insert(0, '/path/to/stock-mcp-server')

from tools import AntiCrawler, get_anti_crawler, fetch_with_protection


def example_1_basic_usage():
    """示例1: 基本使用"""
    print("=== 示例1: 基本使用 ===")
    
    # 获取全局实例
    crawler = get_anti_crawler()
    
    # 使用默认配置获取网页
    try:
        response = crawler.get("https://httpbin.org/get")
        print(f"✅ 请求成功: {response.status_code}")
        print(f"   使用的User-Agent: {response.request.headers.get('User-Agent', 'N/A')[:50]}...")
    except Exception as e:
        print(f"❌ 请求失败: {e}")


def example_2_custom_config():
    """示例2: 自定义配置"""
    print("\n=== 示例2: 自定义配置 ===")
    
    # 创建自定义配置的实例
    crawler = AntiCrawler(min_delay=1.0, max_delay=3.0)
    
    print(f"✅ 创建自定义实例")
    print(f"   最小延迟: {crawler.min_delay}s")
    print(f"   最大延迟: {crawler.max_delay}s")
    
    # 使用自定义实例
    try:
        response = crawler.get("https://httpbin.org/get")
        print(f"✅ 请求成功: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")


def example_3_convenient_function():
    """示例3: 使用便捷函数"""
    print("\n=== 示例3: 使用便捷函数 ===")
    
    # 一行代码获取数据
    try:
        response = fetch_with_protection("https://httpbin.org/get")
        print(f"✅ 便捷函数请求成功: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")


def example_4_multiple_requests():
    """示例4: 多个请求（自动延迟）"""
    print("\n=== 示例4: 多个请求（自动延迟） ===")
    
    crawler = get_anti_crawler()
    urls = [
        "https://httpbin.org/get",
        "https://httpbin.org/ip",
        "https://httpbin.org/user-agent",
    ]
    
    for i, url in enumerate(urls, 1):
        try:
            response = crawler.get(url)
            print(f"✅ 请求 {i}: {response.status_code}")
        except Exception as e:
            print(f"❌ 请求 {i} 失败: {e}")
    
    print(f"\n📊 总请求数: {crawler.get_stats()['request_count']}")


def example_5_api_scraping():
    """示例5: API数据抓取（实际应用场景）"""
    print("\n=== 示例5: API数据抓取 ===")
    
    crawler = get_anti_crawler()
    
    # 模拟抓取多个API端点
    api_endpoints = [
        "https://api.github.com",
        "https://api.github.com/users/github",
    ]
    
    for endpoint in api_endpoints:
        try:
            # 添加API特定的请求头
            headers = {
                "Accept": "application/vnd.github.v3+json",
            }
            response = crawler.get(endpoint, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {endpoint}: 成功")
                if isinstance(data, dict):
                    print(f"   返回字段: {list(data.keys())[:3]}...")
            else:
                print(f"⚠️  {endpoint}: 状态码 {response.status_code}")
                
        except Exception as e:
            print(f"❌ {endpoint}: {e}")


def example_6_web_scraping():
    """示例6: 网页抓取（实际应用场景）"""
    print("\n=== 示例6: 网页抓取 ===")
    
    crawler = get_anti_crawler()
    
    # 模拟抓取网页
    urls = [
        "https://www.example.com",
        "https://httpbin.org/html",
    ]
    
    for url in urls:
        try:
            response = crawler.get(url)
            
            if response.status_code == 200:
                # 获取内容长度
                content_length = len(response.text)
                print(f"✅ {url}: {content_length} 字符")
            else:
                print(f"⚠️  {url}: 状态码 {response.status_code}")
                
        except Exception as e:
            print(f"❌ {url}: {e}")


if __name__ == "__main__":
    print("🚀 反爬能力使用示例\n")
    print("=" * 50)
    
    # 运行所有示例
    example_1_basic_usage()
    example_2_custom_config()
    example_3_convenient_function()
    example_4_multiple_requests()
    example_5_api_scraping()
    example_6_web_scraping()
    
    print("\n" + "=" * 50)
    print("✅ 所有示例执行完成！")
    print("\n💡 提示: 可以将这些示例代码复制到其他项目中使用")
    print("   只需确保导入路径正确:")
    print("   from tools import AntiCrawler, get_anti_crawler")
