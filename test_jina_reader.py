#!/usr/bin/env python3
"""
Jina Reader 实战测试
对比 web_fetch 和 Jina Reader 的成功率
"""

import time
from jina_reader import fetch_with_jina, fetch_with_fallback

# 测试网址列表（包含可能反爬的网站）
test_urls = [
    ("GitHub", "https://github.com/microsoft/vscode"),
    ("知乎", "https://zhuanlan.zhihu.com/p/12345678"),
    ("新浪新闻", "https://news.sina.com.cn"),
    ("Reddit", "https://www.reddit.com/r/programming/"),
    ("Medium", "https://medium.com/@someuser/some-article"),
]

print("🧪 Jina Reader 实战测试")
print("=" * 60)

results = []

for name, url in test_urls:
    print(f"\n📍 测试: {name}")
    print(f"   URL: {url}")
    
    # 方法 1：直接请求
    print("   方法 1: 直接请求...", end=" ")
    try:
        import requests
        resp = requests.get(url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        })
        direct_success = resp.status_code == 200
        print(f"{'✅ 成功' if direct_success else '❌ 失败'} ({resp.status_code})")
    except Exception as e:
        direct_success = False
        print(f"❌ 失败 ({str(e)[:30]})")
    
    # 方法 2：Jina Reader
    print("   方法 2: Jina Reader...", end=" ")
    result = fetch_with_jina(url)
    jina_success = result["success"]
    if jina_success:
        content_len = len(result["content"])
        print(f"✅ 成功 ({content_len} 字符)")
    else:
        print(f"❌ 失败 ({result.get('error', 'Unknown')[:30]})")
    
    results.append({
        "name": name,
        "direct": direct_success,
        "jina": jina_success
    })
    
    time.sleep(1)  # 避免请求过快

# 汇总结果
print("\n" + "=" * 60)
print("📊 测试结果汇总")
print("=" * 60)

direct_success = sum(1 for r in results if r["direct"])
jina_success = sum(1 for r in results if r["jina"])

print(f"\n直接请求成功率: {direct_success}/{len(results)} ({direct_success/len(results)*100:.0f}%)")
print(f"Jina Reader 成功率: {jina_success}/{len(results)} ({jina_success/len(results)*100:.0f}%)")

if jina_success > direct_success:
    print(f"\n🎉 Jina Reader 提升了 {jina_success - direct_success} 个网站的成功率！")

print("\n💡 建议：对于直接请求失败的网站，使用 Jina Reader 作为备选方案")
