#!/usr/bin/env python3
"""
青龙 Chrome DevTools MCP 自动化工作流
实时股票数据抓取 + 分析 + 存储
"""

import websocket
import json
import time
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
import requests


class ChromeMCPClient:
    """Chrome DevTools MCP 客户端"""
    
    def __init__(self, port: int = 9222):
        self.port = port
        self.base_url = f"http://localhost:{port}"
        self.ws_url = None
        self.page_id = None
        self.ws = None
        
    def connect(self) -> bool:
        """连接到 Chrome DevTools"""
        try:
            # 检查 Chrome 是否运行
            response = requests.get(f"{self.base_url}/json/version", timeout=5)
            if response.status_code != 200:
                print("❌ Chrome DevTools 未响应")
                return False
            
            version = response.json()
            print(f"✅ 已连接到 Chrome {version.get('Browser', 'Unknown')}")
            return True
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False
    
    def create_page(self, url: str) -> Optional[str]:
        """创建新页面"""
        try:
            response = requests.put(f"{self.base_url}/json/new?{url}", timeout=10)
            data = response.json()
            self.page_id = data.get('id')
            self.ws_url = data.get('webSocketDebuggerUrl')
            print(f"✅ 页面已创建: {self.page_id[:8]}...")
            return self.page_id
        except Exception as e:
            print(f"❌ 创建页面失败: {e}")
            return None
    
    def connect_websocket(self) -> bool:
        """连接 WebSocket"""
        if not self.ws_url:
            return False
        try:
            self.ws = websocket.create_connection(self.ws_url, timeout=10)
            print("✅ WebSocket 已连接")
            return True
        except Exception as e:
            print(f"❌ WebSocket 连接失败: {e}")
            return False
    
    def execute_js(self, script: str) -> Dict:
        """执行 JavaScript"""
        if not self.ws:
            return {}
        
        data = {
            'id': int(time.time() * 1000),
            'method': 'Runtime.evaluate',
            'params': {
                'expression': script,
                'returnByValue': True
            }
        }
        
        try:
            self.ws.send(json.dumps(data))
            result = self.ws.recv()
            return json.loads(result)
        except Exception as e:
            print(f"❌ 执行 JS 失败: {e}")
            return {}
    
    def close(self):
        """关闭连接"""
        if self.ws:
            self.ws.close()
            print("✅ WebSocket 已关闭")


class StockDataScraper:
    """股票数据抓取器"""
    
    def __init__(self, chrome_client: ChromeMCPClient):
        self.chrome = chrome_client
        
    def scrape_stock(self, code: str) -> Dict:
        """抓取单只股票数据"""
        # 构建 URL
        prefix = "1" if code.startswith("sh") or code.startswith("6") else "0"
        url = f"https://quote.eastmoney.com/unify/r/{prefix}.{code.replace('sh', '').replace('sz', '')}"
        
        print(f"\n📊 抓取股票: {code}")
        print(f"   URL: {url}")
        
        # 创建页面
        page_id = self.chrome.create_page(url)
        if not page_id:
            return {}
        
        # 等待页面加载
        time.sleep(3)
        
        # 连接 WebSocket
        if not self.chrome.connect_websocket():
            return {}
        
        # 执行 JavaScript 抓取数据
        js_code = r"""
(() => {
    const data = {};
    
    // 获取标题
    data.title = document.title;
    data.url = window.location.href;
    
    // 尝试从标题解析数据
    const titleText = document.title;
    const parts = titleText.split(' ');
    if (parts.length >= 2) {
        data.name = parts[0];
        const priceMatch = parts[1].match(/(\d+\.?\d*)/);
        if (priceMatch) data.price = parseFloat(priceMatch[1]);
    }
    
    // 获取所有表格文本
    const tables = document.querySelectorAll('table');
    let tableText = '';
    tables.forEach((t, i) => {
        if (i < 2) tableText += t.innerText + ' ';
    });
    data.table_summary = tableText.substring(0, 500);
    
    // 获取时间
    data.timestamp = new Date().toISOString();
    
    return data;
})()
"""
        
        result = self.chrome.execute_js(js_code)
        
        # 解析结果
        try:
            if 'result' in result and 'result' in result['result']:
                value = result['result']['result'].get('value', {})
                if value:
                    value['code'] = code
                    value['url'] = url
                    # 从标题解析价格
                    title = value.get('title', '')
                    import re
                    title_match = re.search(r'(\d+\.?\d*)\s+([\-\+]?\d+\.?\d*)\s*\(([\-\+]?\d+\.?\d*)%\)', title)
                    if title_match:
                        value['price'] = float(title_match.group(1))
                        value['change'] = float(title_match.group(2))
                        value['change_percent'] = float(title_match.group(3))
                    return value
        except Exception as e:
            print(f"   解析错误: {e}")
        
        return {}


class StockDatabase:
    """股票数据库"""
    
    def __init__(self, db_path: str = "stock_data.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL,
                name TEXT,
                price REAL,
                change REAL,
                change_percent REAL,
                volume TEXT,
                turnover TEXT,
                market_cap TEXT,
                turnover_rate TEXT,
                timestamp TEXT,
                url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"✅ 数据库已初始化: {self.db_path}")
    
    def save(self, data: Dict):
        """保存数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO stock_data 
            (code, name, price, change, change_percent, volume, turnover, market_cap, turnover_rate, timestamp, url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('code'),
            data.get('name'),
            data.get('price'),
            data.get('change'),
            data.get('change_percent'),
            data.get('volume'),
            data.get('turnover'),
            data.get('market_cap'),
            data.get('turnover_rate'),
            data.get('timestamp'),
            data.get('url')
        ))
        
        conn.commit()
        conn.close()
        print(f"✅ 数据已保存: {data.get('code')}")


def main():
    """主函数"""
    print("=" * 60)
    print("🐉 青龙 Chrome DevTools MCP 股票抓取工作流")
    print("=" * 60)
    
    # 初始化组件
    chrome = ChromeMCPClient(port=9222)
    db = StockDatabase("qinglong_stock_data.db")
    
    # 检查 Chrome 连接
    if not chrome.connect():
        print("\n❌ 请确保 Chrome 已启动:")
        print("   /Applications/Google\\ Chrome\\ Canary.app/Contents/MacOS/Google\\ Chrome\\ Canary \\")
        print("   --remote-debugging-port=9222 --remote-allow-origins='*' \\")
        print("   --enable-features=WebMCPTesting --user-data-dir=/tmp/chrome-mcp-profile")
        return
    
    # 股票列表
    stocks = [
        "sh600410",  # 华胜天成
        "sh600620",  # 天宸股份
        "sh603986",  # 兆易创新
        "sz002261",  # 拓维信息
        "sh688629",  # 华丰科技
    ]
    
    # 抓取数据
    results = []
    for code in stocks:
        scraper = StockDataScraper(chrome)
        data = scraper.scrape_stock(code)
        
        if data:
            print(f"\n✅ {code} 抓取成功:")
            print(f"   名称: {data.get('name')}")
            print(f"   价格: {data.get('price')}")
            print(f"   涨跌: {data.get('change')} ({data.get('change_percent')}%)")
            
            # 保存到数据库
            db.save(data)
            results.append(data)
        else:
            print(f"\n❌ {code} 抓取失败")
        
        # 关闭当前页面连接
        chrome.close()
        
        # 间隔避免请求过快
        time.sleep(2)
    
    # 总结
    print("\n" + "=" * 60)
    print(f"📊 抓取完成: {len(results)}/{len(stocks)} 只股票")
    print("=" * 60)


if __name__ == "__main__":
    main()
