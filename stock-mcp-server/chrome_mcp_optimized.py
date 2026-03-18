#!/usr/bin/env python3
"""
青龙 Token 优化版 Chrome MCP 工作流
目标: 低成本 + 高效 + 准确
"""

import websocket
import json
import time
import sqlite3
import hashlib
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Dict, List, Optional
import requests


class TokenOptimizedCache:
    """Token 优化缓存系统"""
    
    def __init__(self, db_path: str = "token_optimized_cache.db"):
        self.db_path = db_path
        self.memory_cache = {}
        self.init_db()
    
    def init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                data TEXT,
                created_at TIMESTAMP,
                expires_at TIMESTAMP,
                access_count INTEGER DEFAULT 1
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get(self, key: str, ttl: int = 60) -> Optional[Dict]:
        """获取缓存 - 优先内存，其次数据库"""
        # 1. 检查内存缓存
        if key in self.memory_cache:
            data, expires = self.memory_cache[key]
            if time.time() < expires:
                return data
            else:
                del self.memory_cache[key]
        
        # 2. 检查数据库缓存
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT data, expires_at FROM cache 
            WHERE key = ? AND expires_at > ?
        ''', (key, datetime.now()))
        
        row = cursor.fetchone()
        if row:
            data = json.loads(row[0])
            # 更新访问计数
            cursor.execute('''
                UPDATE cache SET access_count = access_count + 1 
                WHERE key = ?
            ''', (key,))
            conn.commit()
            conn.close()
            
            # 放入内存缓存
            self.memory_cache[key] = (data, time.time() + min(ttl, 300))
            return data
        
        conn.close()
        return None
    
    def set(self, key: str, data: Dict, ttl: int = 60):
        """设置缓存"""
        expires = datetime.now() + timedelta(seconds=ttl)
        
        # 内存缓存
        self.memory_cache[key] = (data, time.time() + min(ttl, 300))
        
        # 数据库缓存
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO cache (key, data, created_at, expires_at)
            VALUES (?, ?, ?, ?)
        ''', (key, json.dumps(data), datetime.now(), expires))
        
        conn.commit()
        conn.close()


class TokenOptimizedChromeMCP:
    """Token 优化的 Chrome MCP 客户端"""
    
    def __init__(self, port: int = 9222):
        self.port = port
        self.base_url = f"http://localhost:{port}"
        self.cache = TokenOptimizedCache()
        self.request_count = 0
        self.cache_hit_count = 0
    
    def get_stock_data(self, code: str, use_cache: bool = True) -> Dict:
        """
        获取股票数据 - Token 优化版
        
        策略:
        1. 优先从缓存获取 (0 Token)
        2. 缓存未命中才用 Chrome MCP (0 Token)
        3. 绝不使用 LLM 抓取数据
        """
        cache_key = f"stock:{code}"
        
        # 1. 检查缓存
        if use_cache:
            cached = self.cache.get(cache_key, ttl=60)
            if cached:
                self.cache_hit_count += 1
                cached['from_cache'] = True
                return cached
        
        # 2. Chrome MCP 抓取 (0 Token)
        self.request_count += 1
        data = self._fetch_from_chrome(code)
        
        # 3. 存入缓存
        if data:
            self.cache.set(cache_key, data, ttl=60)
        
        return data
    
    def _fetch_from_chrome(self, code: str) -> Dict:
        """Chrome MCP 抓取 - 零 Token 消耗"""
        try:
            # 构建 URL
            prefix = "1" if code.startswith("sh") or code.startswith("6") else "0"
            url = f"https://quote.eastmoney.com/unify/r/{prefix}.{code.replace('sh', '').replace('sz', '')}"
            
            # 创建页面
            resp = requests.put(f"{self.base_url}/json/new?{url}", timeout=10)
            page = resp.json()
            page_id = page['id']
            ws_url = page['webSocketDebuggerUrl']
            
            # 等待加载
            time.sleep(2)
            
            # WebSocket 连接
            ws = websocket.create_connection(ws_url, timeout=10)
            
            # 执行 JS 抓取数据
            js_code = """
            (() => {
                const data = {};
                data.title = document.title;
                data.url = location.href;
                
                // 从标题解析
                const title = document.title;
                const match = title.match(/(.+?)\s+(\d+\.?\d*)\s+([\-\+]?\d+\.?\d*)\s*\(([\-\+]?\d+\.?\d*)%\)/);
                if (match) {
                    data.name = match[1];
                    data.price = parseFloat(match[2]);
                    data.change = parseFloat(match[3]);
                    data.change_percent = parseFloat(match[4]);
                }
                
                data.timestamp = new Date().toISOString();
                return data;
            })()
            """
            
            ws.send(json.dumps({
                'id': 1,
                'method': 'Runtime.evaluate',
                'params': {'expression': js_code, 'returnByValue': True}
            }))
            
            result = json.loads(ws.recv())
            ws.close()
            
            if 'result' in result and 'result' in result['result']:
                value = result['result']['result'].get('value', {})
                value['code'] = code
                value['from_cache'] = False
                return value
            
        except Exception as e:
            print(f"抓取失败 {code}: {e}")
        
        return {}
    
    def batch_analyze(self, stocks_data: List[Dict]) -> str:
        """
        批量分析 - 1 次 LLM 调用替代 N 次
        
        节省: (N-1) * 500 Token
        """
        if not stocks_data:
            return "无数据"
        
        # 构建批量提示词
        stocks_text = "\n".join([
            f"{i+1}. {s['code']} - {s.get('name', 'N/A')}: "
            f"价格{s.get('price', 'N/A')}, 涨跌{s.get('change_percent', 'N/A')}%, "
            f"板块{s.get('sector', 'N/A')}"
            for i, s in enumerate(stocks_data)
        ])
        
        prompt = f"""分析以下 {len(stocks_data)} 只股票，每只给出: 趋势/支撑/阻力/建议

数据:
{stocks_text}

要求:
1. 简洁回答，每只股票不超过 50 字
2. 使用格式: [代码] 趋势|支撑|阻力|建议
3. 优先看技术指标

分析:"""
        
        # 这里应该调用 LLM，但为了不消耗 Token，先返回模拟结果
        # 实际使用时替换为真实的 LLM 调用
        return f"批量分析完成: {len(stocks_data)} 只股票 (1 次 LLM 调用)"
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "request_count": self.request_count,
            "cache_hit_count": self.cache_hit_count,
            "cache_hit_rate": self.cache_hit_count / max(self.request_count, 1),
            "token_saved": self.cache_hit_count * 500  # 估算节省的 Token
        }


def main():
    """主函数 - Token 优化版"""
    print("=" * 60)
    print("🐉 青龙 Token 优化版 Chrome MCP 工作流")
    print("=" * 60)
    print()
    
    client = TokenOptimizedChromeMCP(port=9222)
    
    # 股票列表
    stocks = ["sh600410", "sh600620", "sh603986", "sz002261", "sh688629"]
    
    print("📊 开始抓取 (Token 优化模式)...")
    print("策略: 缓存优先 + 批量处理 + 零 Token 抓取")
    print()
    
    # 第一轮抓取
    print("第一轮 (缓存未命中):")
    for code in stocks:
        data = client.get_stock_data(code)
        status = "✅" if data else "❌"
        cache_status = "缓存" if data.get('from_cache') else "抓取"
        print(f"  {status} {code}: {data.get('name', 'N/A')} "
              f"{data.get('price', 'N/A')} ({cache_status})")
    
    print()
    
    # 第二轮抓取 (测试缓存)
    print("第二轮 (测试缓存):")
    for code in stocks:
        data = client.get_stock_data(code)
        cache_status = "✅ 缓存命中" if data.get('from_cache') else "❌ 缓存未命中"
        print(f"  {code}: {cache_status}")
    
    print()
    
    # 统计信息
    stats = client.get_stats()
    print("📈 Token 优化统计:")
    print(f"  总请求: {stats['request_count']}")
    print(f"  缓存命中: {stats['cache_hit_count']}")
    print(f"  缓存命中率: {stats['cache_hit_rate']:.1%}")
    print(f"  估算节省 Token: {stats['token_saved']:,}")
    
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
