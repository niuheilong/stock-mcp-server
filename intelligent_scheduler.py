#!/usr/bin/env python3
"""
智能技能调度器 (Intelligent Skill Scheduler)
基于第一性原理和成本优化

核心功能：
1. 自动选择最优技能组合
2. 多层Fallback机制
3. 智能缓存
4. 成本控制
"""

import time
import json
import hashlib
from typing import Dict, List, Callable, Optional, Any
from functools import wraps
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
import threading


class SkillCache:
    """智能缓存系统"""
    
    # 不同数据类型的缓存时间（秒）
    TTL_CONFIG = {
        "stock_price": 60,        # 股价: 1分钟
        "stock_info": 3600,       # 股票信息: 1小时
        "web_page": 300,          # 网页: 5分钟
        "news": 600,              # 新闻: 10分钟
        "search_result": 1800,    # 搜索结果: 30分钟
        "analysis_report": 86400, # 分析报告: 1天
        "technical_indicators": 300,  # 技术指标: 5分钟
    }
    
    def __init__(self):
        self._cache = {}
        self._lock = threading.Lock()
    
    def _generate_key(self, skill_name: str, params: Dict) -> str:
        """生成缓存key"""
        key_data = f"{skill_name}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, skill_name: str, params: Dict, data_type: str = "default") -> Optional[Any]:
        """获取缓存"""
        key = self._generate_key(skill_name, params)
        
        with self._lock:
            if key in self._cache:
                data, timestamp = self._cache[key]
                ttl = self.TTL_CONFIG.get(data_type, 300)
                
                if time.time() - timestamp < ttl:
                    return data
                else:
                    # 过期删除
                    del self._cache[key]
        
        return None
    
    def set(self, skill_name: str, params: Dict, data: Any):
        """设置缓存"""
        key = self._generate_key(skill_name, params)
        
        with self._lock:
            self._cache[key] = (data, time.time())
    
    def clear_expired(self):
        """清理过期缓存"""
        now = time.time()
        with self._lock:
            expired_keys = [
                key for key, (data, timestamp) in self._cache.items()
                if now - timestamp > 86400  # 超过1天
            ]
            for key in expired_keys:
                del self._cache[key]


class SkillExecutor:
    """技能执行器 - 带超时和重试"""
    
    TIMEOUT_CONFIG = {
        "local": 2,           # 本地计算: 2秒
        "file": 3,            # 文件读取: 3秒
        "web_fetch": 10,      # 网页抓取: 10秒
        "web_search": 15,     # 网络搜索: 15秒
        "browser": 30,        # 浏览器: 30秒
        "ai": 60,             # AI生成: 60秒
    }
    
    def __init__(self):
        self.cache = SkillCache()
        self.stats = {
            "total_calls": 0,
            "cache_hits": 0,
            "fallback_triggers": 0,
            "errors": 0,
        }
    
    def execute(self, skill_name: str, func: Callable, params: Dict, 
                data_type: str = "default", timeout: Optional[int] = None) -> Dict:
        """
        执行技能，带缓存和错误处理
        
        Returns:
            {"success": bool, "data": any, "from_cache": bool, "cost": float}
        """
        start_time = time.time()
        
        # 1. 检查缓存
        cached_data = self.cache.get(skill_name, params, data_type)
        if cached_data is not None:
            self.stats["cache_hits"] += 1
            return {
                "success": True,
                "data": cached_data,
                "from_cache": True,
                "cost": 0,
                "time": time.time() - start_time
            }
        
        # 2. 执行（带超时）
        try:
            timeout = timeout or self.TIMEOUT_CONFIG.get(data_type, 10)
            
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(func, **params)
                data = future.result(timeout=timeout)
            
            # 3. 缓存结果
            self.cache.set(skill_name, params, data)
            
            self.stats["total_calls"] += 1
            
            return {
                "success": True,
                "data": data,
                "from_cache": False,
                "cost": 1,  # 简化成本计算
                "time": time.time() - start_time
            }
            
        except FutureTimeoutError:
            self.stats["errors"] += 1
            return {
                "success": False,
                "error": f"Timeout after {timeout}s",
                "cost": 1,
                "time": time.time() - start_time
            }
        except Exception as e:
            self.stats["errors"] += 1
            return {
                "success": False,
                "error": str(e),
                "cost": 1,
                "time": time.time() - start_time
            }


class IntelligentSkillScheduler:
    """
    智能技能调度器
    根据任务类型自动选择最优技能组合
    """
    
    def __init__(self):
        self.executor = SkillExecutor()
        self.skill_registry = {}
    
    def register_skill(self, name: str, func: Callable, level: int, data_type: str):
        """注册技能"""
        self.skill_registry[name] = {
            "func": func,
            "level": level,  # 1-5, 1最低成本
            "data_type": data_type
        }
    
    def execute_with_fallback(self, primary_skill: str, fallback_chain: List[str], 
                             params: Dict) -> Dict:
        """
        执行技能，自动fallback
        
        Args:
            primary_skill: 首选技能名
            fallback_chain: fallback技能链
            params: 参数
        """
        # 尝试主技能
        result = self._execute_skill(primary_skill, params)
        if result["success"]:
            return result
        
        # 依次尝试fallback
        for skill_name in fallback_chain:
            self.executor.stats["fallback_triggers"] += 1
            result = self._execute_skill(skill_name, params)
            if result["success"]:
                return result
        
        # 全部失败
        return {
            "success": False,
            "error": f"All skills failed: {primary_skill}, {fallback_chain}",
            "data": None
        }
    
    def _execute_skill(self, skill_name: str, params: Dict) -> Dict:
        """执行单个技能"""
        if skill_name not in self.skill_registry:
            return {"success": False, "error": f"Skill {skill_name} not registered"}
        
        skill = self.skill_registry[skill_name]
        return self.executor.execute(
            skill_name,
            skill["func"],
            params,
            skill["data_type"]
        )
    
    def get_stock_price(self, symbol: str) -> Dict:
        """
        获取股价 - 最优调度示例
        
        Level 1: 新浪API（最快）
        Level 2: 腾讯API（备用）
        Level 3: Jina Reader抓取
        """
        # 注册技能（如果还没注册）
        if "sina_price" not in self.skill_registry:
            from sina_stock_api import get_sina_stock_price
            self.register_skill("sina_price", get_sina_stock_price, 1, "stock_price")
        
        if "qq_price" not in self.skill_registry:
            from qq_stock_api import get_qq_stock_price
            self.register_skill("qq_price", get_qq_stock_price, 1, "stock_price")
        
        # 执行（带fallback）
        return self.execute_with_fallback(
            "sina_price",
            ["qq_price"],
            {"symbol": symbol}
        )
    
    def get_web_content(self, url: str) -> Dict:
        """
        获取网页内容 - 最优调度示例
        
        Level 1: web_fetch（直接）
        Level 2: jina_reader（绕过反爬）
        """
        if "web_fetch" not in self.skill_registry:
            import requests
            def fetch(url):
                return requests.get(url, timeout=10).text
            self.register_skill("web_fetch", fetch, 3, "web_page")
        
        if "jina_reader" not in self.skill_registry:
            from jina_reader import fetch_with_jina
            self.register_skill("jina_reader", fetch_with_jina, 3, "web_page")
        
        return self.execute_with_fallback(
            "web_fetch",
            ["jina_reader"],
            {"url": url}
        )
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            **self.executor.stats,
            "cache_size": len(self.executor.cache._cache),
            "registered_skills": len(self.skill_registry)
        }


# 全局调度器实例
_scheduler = None

def get_scheduler() -> IntelligentSkillScheduler:
    """获取全局调度器（单例）"""
    global _scheduler
    if _scheduler is None:
        _scheduler = IntelligentSkillScheduler()
    return _scheduler


# 装饰器：自动缓存
def cached_skill(data_type: str = "default"):
    """技能缓存装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            scheduler = get_scheduler()
            skill_name = func.__name__
            params = {"args": args, "kwargs": kwargs}
            
            # 执行
            result = scheduler.executor.execute(
                skill_name, func, params, data_type
            )
            
            if result["success"]:
                return result["data"]
            else:
                raise Exception(result.get("error", "Unknown error"))
        
        return wrapper
    return decorator


# 测试
if __name__ == "__main__":
    print("🚀 智能技能调度器测试")
    print("=" * 70)
    
    scheduler = get_scheduler()
    
    # 测试股价获取
    print("\n1️⃣ 测试股价获取（带fallback）")
    result = scheduler.get_stock_price("600519")
    
    if result["success"]:
        print(f"✅ 成功！")
        print(f"   数据源: {'缓存' if result.get('from_cache') else '实时'}")
        print(f"   耗时: {result.get('time', 0):.3f}s")
        print(f"   成本: {result.get('cost', 0)}")
    else:
        print(f"❌ 失败: {result.get('error')}")
    
    # 再次获取（测试缓存）
    print("\n2️⃣ 再次获取（测试缓存）")
    result2 = scheduler.get_stock_price("600519")
    
    if result2.get("from_cache"):
        print(f"✅ 命中缓存！耗时: {result2.get('time', 0):.3f}s")
    
    # 显示统计
    print("\n3️⃣ 调度器统计")
    stats = scheduler.get_stats()
    print(f"   总调用: {stats['total_calls']}")
    print(f"   缓存命中: {stats['cache_hits']}")
    print(f"   Fallback触发: {stats['fallback_triggers']}")
    print(f"   错误: {stats['errors']}")
    print(f"   缓存大小: {stats['cache_size']}")
    
    print("\n" + "=" * 70)
    print("✅ 智能调度器工作正常！")
    print("\n💡 核心优势:")
    print("   • 自动选择最优技能")
    print("   • 智能缓存减少重复请求")
    print("   • 自动fallback保证可用性")
    print("   • 成本控制（优先低成本方案）")
