#!/usr/bin/env python3
"""
浏览器资源管理模块
自动关闭空闲浏览器，释放资源
"""

import time
from datetime import datetime, timedelta
from typing import Optional


class BrowserResourceManager:
    """浏览器资源管理器"""
    
    def __init__(self, max_idle_seconds: int = 600):
        self.max_idle_seconds = max_idle_seconds
        self.last_activity = None
        self.browser_active = False
        self.session_count = 0
        
    def mark_activity(self):
        """标记浏览器活动"""
        self.last_activity = datetime.now()
        self.browser_active = True
        
    def mark_browser_opened(self):
        """标记浏览器已打开"""
        self.browser_active = True
        self.last_activity = datetime.now()
        self.session_count += 1
        
    def mark_browser_closed(self):
        """标记浏览器已关闭"""
        self.browser_active = False
        self.last_activity = None
        
    def should_close_browser(self) -> bool:
        """检查是否应该关闭浏览器"""
        if not self.browser_active or not self.last_activity:
            return False
            
        idle_time = (datetime.now() - self.last_activity).total_seconds()
        return idle_time > self.max_idle_seconds
        
    def get_idle_time(self) -> float:
        """获取浏览器空闲时间（秒）"""
        if not self.last_activity:
            return 0
        return (datetime.now() - self.last_activity).total_seconds()
        
    def get_status(self) -> dict:
        """获取状态信息"""
        return {
            "active": self.browser_active,
            "idle_seconds": self.get_idle_time(),
            "session_count": self.session_count,
            "max_idle_seconds": self.max_idle_seconds,
            "should_close": self.should_close_browser()
        }


# 全局实例
_browser_manager = None

def get_browser_manager() -> BrowserResourceManager:
    """获取全局浏览器管理器"""
    global _browser_manager
    if _browser_manager is None:
        _browser_manager = BrowserResourceManager(max_idle_seconds=300)  # 5分钟
    return _browser_manager


# 装饰器：自动管理浏览器资源
def auto_close_browser(timeout_seconds: int = 300):
    """装饰器：自动关闭浏览器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            manager = get_browser_manager()
            
            try:
                # 标记活动
                manager.mark_activity()
                
                # 执行函数
                result = func(*args, **kwargs)
                
                # 再次标记活动
                manager.mark_activity()
                
                return result
                
            finally:
                # 检查是否需要关闭浏览器
                if manager.should_close_browser():
                    print(f"🌐 浏览器空闲超过 {timeout_seconds} 秒，自动关闭")
                    try:
                        from browser import browser as browser_tool
                        browser_tool.stop()
                        manager.mark_browser_closed()
                    except Exception as e:
                        print(f"⚠️ 关闭浏览器失败: {e}")
                        
        return wrapper
    return decorator


# 上下文管理器
class BrowserSession:
    """浏览器会话上下文管理器"""
    
    def __init__(self, auto_close: bool = True, max_idle: int = 300):
        self.auto_close = auto_close
        self.max_idle = max_idle
        self.manager = get_browser_manager()
        
    def __enter__(self):
        self.manager.mark_browser_opened()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.auto_close:
            idle_time = self.manager.get_idle_time()
            if idle_time > self.max_idle:
                print(f"🌐 会话结束，关闭浏览器（空闲 {idle_time:.0f} 秒）")
                try:
                    from browser import browser as browser_tool
                    browser_tool.stop()
                    self.manager.mark_browser_closed()
                except Exception as e:
                    print(f"⚠️ 关闭浏览器失败: {e}")
                    
    def mark_activity(self):
        """标记活动"""
        self.manager.mark_activity()


# 使用示例
if __name__ == "__main__":
    manager = get_browser_manager()
    
    # 模拟浏览器使用
    print("打开浏览器...")
    manager.mark_browser_opened()
    
    print(f"状态: {manager.get_status()}")
    
    # 模拟活动
    time.sleep(2)
    manager.mark_activity()
    print(f"2秒后状态: {manager.get_status()}")
    
    # 模拟空闲
    print("模拟空闲...")
    time.sleep(3)
    
    if manager.should_close_browser():
        print("应该关闭浏览器")
    else:
        print(f"还可以继续使用，空闲 {manager.get_idle_time():.0f} 秒")
