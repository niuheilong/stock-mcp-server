"""
青龙工具库 - 通用工具集合

使用示例:
    from tools import AntiCrawler, fetch_with_protection
    
    # 使用反爬功能
    crawler = AntiCrawler()
    response = crawler.get("https://example.com")
"""

from .anti_crawler import AntiCrawler, get_anti_crawler, fetch_with_protection

__all__ = [
    "AntiCrawler",
    "get_anti_crawler", 
    "fetch_with_protection",
]

__version__ = "1.0.0"
