"""
青龙 Stock MCP Server - 反爬策略模块
版本: 1.0
创建时间: 2026-03-26
用途: 增强数据获取稳定性，降低被封风险
"""

import random
import time
import logging
from typing import Dict, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class AntiCrawler:
    """
    反爬策略类
    
    功能:
    - User-Agent 轮换
    - 请求头模拟
    - 随机延迟
    - 会话管理
    - 自动重试
    """
    
    # User-Agent 池
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]
    
    # 接受语言
    ACCEPT_LANGUAGES = [
        "zh-CN,zh;q=0.9,en;q=0.8",
        "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        "zh-TW,zh;q=0.9,en;q=0.8",
    ]
    
    def __init__(self, min_delay: float = 0.5, max_delay: float = 2.0):
        """
        初始化反爬策略
        
        Args:
            min_delay: 最小延迟（秒）
            max_delay: 最大延迟（秒）
        """
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.request_count = 0
        self.last_request_time = 0
        self.session = self._create_session()
        
        logger.info(f"AntiCrawler initialized with delay: {min_delay}-{max_delay}s")
    
    def _create_session(self) -> requests.Session:
        """创建带重试机制的会话"""
        session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=3,                    # 总重试次数
            backoff_factor=1,           # 重试间隔倍数
            status_forcelist=[429, 500, 502, 503, 504],  # 需要重试的HTTP状态码
        )
        
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,        # 连接池大小
            pool_maxsize=10,           # 最大连接数
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def get_headers(self, referer: Optional[str] = None) -> Dict[str, str]:
        """
        获取随机请求头
        
        Args:
            referer: 来源页面
            
        Returns:
            请求头字典
        """
        headers = {
            "User-Agent": random.choice(self.USER_AGENTS),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": random.choice(self.ACCEPT_LANGUAGES),
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Cache-Control": "max-age=0",
        }
        
        if referer:
            headers["Referer"] = referer
        
        return headers
    
    def rate_limit(self):
        """速率限制 - 随机延迟"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        
        if elapsed < self.min_delay:
            # 计算需要延迟的时间
            delay = random.uniform(self.min_delay - elapsed, self.max_delay - elapsed)
            if delay > 0:
                logger.debug(f"Rate limiting: sleeping for {delay:.2f}s")
                time.sleep(delay)
        
        self.last_request_time = time.time()
    
    def get(self, url: str, **kwargs) -> requests.Response:
        """
        带反爬策略的 GET 请求
        
        Args:
            url: 请求URL
            **kwargs: 其他请求参数
            
        Returns:
            Response对象
        """
        # 速率限制
        self.rate_limit()
        
        # 获取请求头
        headers = self.get_headers(kwargs.pop("referer", None))
        headers.update(kwargs.pop("headers", {}))
        
        try:
            response = self.session.get(url, headers=headers, **kwargs)
            self.request_count += 1
            
            logger.debug(f"Request #{self.request_count}: {url} - Status: {response.status_code}")
            
            # 如果返回429（Too Many Requests），增加延迟后重试
            if response.status_code == 429:
                logger.warning(f"Rate limited (429), increasing delay...")
                time.sleep(random.uniform(5.0, 10.0))
                return self.get(url, **kwargs)
            
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            # 失败后增加延迟
            time.sleep(random.uniform(2.0, 5.0))
            raise
    
    def post(self, url: str, **kwargs) -> requests.Response:
        """
        带反爬策略的 POST 请求
        
        Args:
            url: 请求URL
            **kwargs: 其他请求参数
            
        Returns:
            Response对象
        """
        self.rate_limit()
        
        headers = self.get_headers(kwargs.pop("referer", None))
        headers.update(kwargs.pop("headers", {}))
        
        try:
            response = self.session.post(url, headers=headers, **kwargs)
            self.request_count += 1
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            time.sleep(random.uniform(2.0, 5.0))
            raise
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "request_count": self.request_count,
            "min_delay": self.min_delay,
            "max_delay": self.max_delay,
        }
    
    def reset_session(self):
        """重置会话（用于长时间运行后）"""
        self.session.close()
        self.session = self._create_session()
        logger.info("Session reset")


# 全局实例（单例模式）
_anti_crawler_instance: Optional[AntiCrawler] = None


def get_anti_crawler(min_delay: float = 0.5, max_delay: float = 2.0) -> AntiCrawler:
    """
    获取 AntiCrawler 实例（单例）
    
    Args:
        min_delay: 最小延迟
        max_delay: 最大延迟
        
    Returns:
        AntiCrawler 实例
    """
    global _anti_crawler_instance
    
    if _anti_crawler_instance is None:
        _anti_crawler_instance = AntiCrawler(min_delay, max_delay)
    
    return _anti_crawler_instance


def reset_anti_crawler():
    """重置 AntiCrawler 实例"""
    global _anti_crawler_instance
    
    if _anti_crawler_instance:
        _anti_crawler_instance.reset_session()


# 便捷函数
def fetch_with_protection(url: str, **kwargs) -> requests.Response:
    """
    使用反爬策略获取数据
    
    Args:
        url: 请求URL
        **kwargs: 其他参数
        
    Returns:
        Response对象
    """
    crawler = get_anti_crawler()
    return crawler.get(url, **kwargs)


if __name__ == "__main__":
    # 测试
    logging.basicConfig(level=logging.DEBUG)
    
    print("Testing AntiCrawler...")
    
    crawler = AntiCrawler(min_delay=1.0, max_delay=2.0)
    
    # 测试请求
    test_urls = [
        "https://httpbin.org/get",
    ]
    
    for url in test_urls:
        try:
            print(f"\nFetching: {url}")
            response = crawler.get(url)
            print(f"Status: {response.status_code}")
            print(f"Headers sent: {response.request.headers.get('User-Agent', 'N/A')[:50]}...")
        except Exception as e:
            print(f"Error: {e}")
    
    print(f"\nStats: {crawler.get_stats()}")
