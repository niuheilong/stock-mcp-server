"""
青龙 Stock MCP Server - 智能数据获取模块
版本: 2.0
设计原则: Chrome MCP 优先，反爬备用，缓存兜底
"""

import logging
from typing import Dict, Optional, Callable
from datetime import datetime, time
import json

logger = logging.getLogger(__name__)


class SmartDataFetcher:
    """
    智能数据获取器
    
    优先级:
    1. Chrome MCP (第一选择) - 零Token消耗，实时准确
    2. 反爬模块 (备用) - Chrome MCP 失败时使用
    3. 缓存数据 (兜底) - 所有实时获取失败时
    """
    
    def __init__(self, chrome_mcp_func: Optional[Callable] = None):
        """
        初始化
        
        Args:
            chrome_mcp_func: Chrome MCP 获取数据的函数
        """
        self.chrome_mcp_func = chrome_mcp_func
        self.anti_crawler = None
        
        # 延迟加载反爬模块（避免不必要的导入）
        try:
            from anti_crawler import get_anti_crawler
            self.anti_crawler = get_anti_crawler()
            logger.info("AntiCrawler loaded successfully")
        except ImportError:
            logger.warning("AntiCrawler not available")
    
    def fetch_stock_price(self, symbol: str) -> Dict:
        """
        获取股票价格（智能选择数据源）
        
        Args:
            symbol: 股票代码
            
        Returns:
            股票数据字典
        """
        result = {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "source": None,
            "data": None,
            "error": None,
        }
        
        # 方法1: Chrome MCP (第一选择)
        if self.chrome_mcp_func:
            try:
                logger.debug(f"Trying Chrome MCP for {symbol}")
                data = self.chrome_mcp_func(symbol)
                if data and not data.get("error"):
                    result["source"] = "chrome_mcp"
                    result["data"] = data
                    logger.info(f"✅ Chrome MCP success for {symbol}")
                    return result
            except Exception as e:
                logger.warning(f"Chrome MCP failed: {e}")
        
        # 方法2: 反爬模块 (备用)
        if self.anti_crawler:
            try:
                logger.debug(f"Trying AntiCrawler for {symbol}")
                data = self._fetch_with_anti_crawler(symbol)
                if data and not data.get("error"):
                    result["source"] = "anti_crawler"
                    result["data"] = data
                    logger.info(f"✅ AntiCrawler success for {symbol}")
                    return result
            except Exception as e:
                logger.warning(f"AntiCrawler failed: {e}")
        
        # 方法3: 缓存数据 (兜底)
        try:
            logger.debug(f"Trying cache for {symbol}")
            data = self._fetch_from_cache(symbol)
            if data:
                result["source"] = "cache"
                result["data"] = data
                logger.info(f"✅ Cache hit for {symbol}")
                return result
        except Exception as e:
            logger.warning(f"Cache failed: {e}")
        
        # 所有方法都失败
        result["error"] = "All data sources failed"
        logger.error(f"❌ All sources failed for {symbol}")
        return result
    
    def _fetch_with_anti_crawler(self, symbol: str) -> Dict:
        """使用反爬模块获取数据"""
        from qq_stock_api_enhanced import get_qq_stock_price
        return get_qq_stock_price(symbol)
    
    def _fetch_from_cache(self, symbol: str) -> Optional[Dict]:
        """从缓存获取数据"""
        # TODO: 实现缓存逻辑
        return None
    
    def is_trading_time(self) -> bool:
        """判断是否在交易时间"""
        now = datetime.now()
        
        # 周末
        if now.weekday() >= 5:
            return False
        
        current_time = now.time()
        
        # 上午交易时间: 9:30 - 11:30
        morning_start = time(9, 30)
        morning_end = time(11, 30)
        
        # 下午交易时间: 13:00 - 15:00
        afternoon_start = time(13, 0)
        afternoon_end = time(15, 0)
        
        return (morning_start <= current_time <= morning_end) or \
               (afternoon_start <= current_time <= afternoon_end)
    
    def get_recommended_source(self) -> str:
        """获取推荐的数据源"""
        if self.is_trading_time():
            return "chrome_mcp"  # 交易时间优先使用 Chrome MCP
        else:
            return "cache"  # 非交易时间优先使用缓存


# 便捷函数
def fetch_stock_price_smart(symbol: str, chrome_mcp_func: Optional[Callable] = None) -> Dict:
    """
    智能获取股票价格
    
    Args:
        symbol: 股票代码
        chrome_mcp_func: Chrome MCP 函数（可选）
        
    Returns:
        股票数据
    """
    fetcher = SmartDataFetcher(chrome_mcp_func)
    return fetcher.fetch_stock_price(symbol)


if __name__ == "__main__":
    # 测试
    logging.basicConfig(level=logging.DEBUG)
    
    print("测试智能数据获取器:\n")
    
    # 定义模拟的 Chrome MCP 函数
    def mock_chrome_mcp(symbol):
        # 模拟 Chrome MCP 成功
        return {
            "name": "贵州茅台",
            "price": "1410.27",
            "change": "+40.27",
            "change_percent": "+2.94%",
        }
    
    fetcher = SmartDataFetcher(chrome_mcp_func=mock_chrome_mcp)
    
    # 测试
    result = fetcher.fetch_stock_price("600519")
    
    print(f"股票: {result['symbol']}")
    print(f"数据源: {result['source']}")
    print(f"数据: {json.dumps(result['data'], ensure_ascii=False, indent=2)}")
    print(f"交易时间: {fetcher.is_trading_time()}")
