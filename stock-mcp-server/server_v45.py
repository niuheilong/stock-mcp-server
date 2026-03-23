#!/usr/bin/env python3
"""
青龙 Stock MCP Server v4.5.0 - Chrome MCP 集成版
实时A股股票数据 + Chrome MCP 抓取 + 多源数据融合
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
import requests
import json
import sqlite3
import subprocess
import time
from datetime import datetime, timedelta
import asyncio
import re
from dataclasses import dataclass
from enum import Enum
import websocket
import threading
import os

# 导入其他模块
from capital_flow import CapitalFlowAnalyzer
from sector_analysis import SectorAnalyzer
from backtest import HistoryDatabase
from alert_system import AlertEngine, AlertRule

app = FastAPI(title="青龙 Stock MCP Server", version="4.5.0")

# ==================== 配置 ====================
CHROME_DEBUG_PORT = 9222
CHROME_USER_DATA = "/tmp/chrome-mcp-qinglong"
DB_PATH = "qinglong_stock_data.db"

# ==================== Chrome MCP 管理器 ====================

class ChromeMCPManager:
    """Chrome MCP 管理器 - 自动启动和管理 Chrome"""
    
    def __init__(self, port: int = CHROME_DEBUG_PORT):
        self.port = port
        self.chrome_process = None
        self.is_running = False
        self.base_url = f"http://localhost:{port}"
        
    def start_chrome(self) -> bool:
        """启动 Chrome 远程调试模式"""
        if self.is_running:
            return True
            
        try:
            # 清理旧的 Chrome 进程
            self._kill_existing_chrome()
            
            # 创建用户数据目录
            os.makedirs(CHROME_USER_DATA, exist_ok=True)
            
            # 启动 Chrome
            cmd = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                f"--remote-debugging-port={self.port}",
                f"--user-data-dir={CHROME_USER_DATA}",
                "--no-first-run",
                "--no-default-browser-check",
                "--headless=new",  # 新版 headless
                "--disable-gpu",
                "--disable-dev-shm-usage",
                "--disable-setuid-sandbox",
                "--no-sandbox"
            ]
            
            self.chrome_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # 等待 Chrome 启动
            time.sleep(3)
            
            # 检查是否成功
            if self._check_chrome():
                self.is_running = True
                print(f"✅ Chrome MCP 已启动 (端口 {self.port})")
                return True
            else:
                print("❌ Chrome MCP 启动失败")
                return False
                
        except Exception as e:
            print(f"❌ 启动 Chrome 失败: {e}")
            return False
    
    def stop_chrome(self):
        """停止 Chrome"""
        if self.chrome_process:
            self.chrome_process.terminate()
            self.chrome_process.wait()
            self.chrome_process = None
            self.is_running = False
            print("✅ Chrome MCP 已停止")
    
    def _kill_existing_chrome(self):
        """清理现有的 Chrome 进程"""
        try:
            subprocess.run(
                ["pkill", "-f", f"remote-debugging-port={self.port}"],
                capture_output=True
            )
            time.sleep(1)
        except:
            pass
    
    def _check_chrome(self) -> bool:
        """检查 Chrome 是否响应"""
        try:
            resp = requests.get(f"{self.base_url}/json/version", timeout=5)
            return resp.status_code == 200
        except:
            return False
    
    def fetch_stock_from_web(self, code: str) -> Optional[Dict]:
        """使用 Chrome MCP 从网页抓取股票数据"""
        if not self.is_running:
            if not self.start_chrome():
                return None
        
        try:
            # 构建东方财富 URL
            prefix = "1" if code.startswith("sh") or code.startswith("6") else "0"
            stock_num = code.replace("sh", "").replace("sz", "")
            url = f"https://quote.eastmoney.com/unify/r/{prefix}.{stock_num}"
            
            # 创建页面
            resp = requests.put(
                f"{self.base_url}/json/new?{url}",
                timeout=10
            )
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
                const match = title.match(/(.+?)\\s+(\\d+\\.?\\d*)\\s+([\\-\\+]?\\d+\\.?\\d*)\\s*\\(([\\-\\+]?\\d+\\.?\\d*)%\\)/);
                if (match) {
                    data.name = match[1];
                    data.price = parseFloat(match[2]);
                    data.change = parseFloat(match[3]);
                    data.change_percent = parseFloat(match[4]);
                }
                
                // 尝试获取更多数据
                const priceElement = document.querySelector('.price');
                if (priceElement) {
                    data.price = parseFloat(priceElement.textContent);
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
            
            # 关闭页面
            requests.delete(f"{self.base_url}/json/close/{page_id}")
            
            if 'result' in result and 'result' in result['result']:
                value = result['result']['result'].get('value', {})
                value['code'] = code
                value['source'] = 'chrome_mcp'
                return value
                
        except Exception as e:
            print(f"Chrome MCP 抓取失败 {code}: {e}")
        
        return None

# ==================== 数据融合引擎 ====================

class DataFusionEngine:
    """多源数据融合引擎"""
    
    def __init__(self):
        self.chrome_manager = ChromeMCPManager()
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL,
                name TEXT,
                price REAL,
                change REAL,
                change_percent REAL,
                volume INTEGER,
                turnover REAL,
                market_cap REAL,
                pe_ratio REAL,
                pb_ratio REAL,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_code_time 
            ON stock_data(code, created_at)
        ''')
        
        conn.commit()
        conn.close()
    
    def fetch_stock_data(self, code: str, use_chrome: bool = True) -> Optional[Dict]:
        """
        融合多源数据获取股票信息
        
        优先级:
        1. 腾讯 API (实时、快速)
        2. Chrome MCP (补充、验证)
        3. 本地缓存 (备用)
        """
        data = None
        sources_used = []
        
        # 1. 尝试腾讯 API
        try:
            data = self._fetch_from_tencent(code)
            if data:
                sources_used.append("tencent")
        except Exception as e:
            print(f"腾讯 API 失败: {e}")
        
        # 2. 尝试 Chrome MCP (用于验证或补充)
        if use_chrome and (not data or not data.get('market_cap')):
            try:
                chrome_data = self.chrome_manager.fetch_stock_from_web(code)
                if chrome_data:
                    if not data:
                        data = chrome_data
                        sources_used.append("chrome_mcp")
                    else:
                        # 数据融合 - 用 Chrome 数据补充
                        if not data.get('name') and chrome_data.get('name'):
                            data['name'] = chrome_data['name']
                        sources_used.append("chrome_mcp_supplement")
            except Exception as e:
                print(f"Chrome MCP 失败: {e}")
        
        # 3. 保存到数据库
        if data:
            data['sources'] = sources_used
            self._save_to_db(data)
        
        return data
    
    def _fetch_from_tencent(self, code: str) -> Optional[Dict]:
        """从腾讯财经获取数据"""
        if code.startswith("sh"):
            tencent_code = code
        elif code.startswith("sz"):
            tencent_code = code
        else:
            return None
        
        url = f"http://qt.gtimg.cn/q={tencent_code}"
        response = requests.get(url, timeout=10)
        response.encoding = 'gbk'
        
        if response.status_code == 200:
            data = response.text
            match = re.search(r'v_{}="([^"]+)"'.format(tencent_code), data)
            if match:
                fields = match.group(1).split('~')
                if len(fields) >= 45:
                    return {
                        "name": fields[1],
                        "code": code,
                        "price": float(fields[3]),
                        "change": float(fields[4]),
                        "change_percent": float(fields[5]),
                        "volume": int(fields[6]),
                        "turnover": float(fields[7]),
                        "market_cap": float(fields[14]) if fields[14] else None,
                        "pe_ratio": float(fields[39]) if fields[39] else None,
                        "pb_ratio": float(fields[46]) if len(fields) > 46 and fields[46] else None,
                        "source": "tencent"
                    }
        return None
    
    def _save_to_db(self, data: Dict):
        """保存数据到数据库"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO stock_data 
            (code, name, price, change, change_percent, volume, turnover, 
             market_cap, pe_ratio, pb_ratio, source)
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
            data.get('pe_ratio'),
            data.get('pb_ratio'),
            ','.join(data.get('sources', []))
        ))
        
        conn.commit()
        conn.close()
    
    def get_historical_data(self, code: str, days: int = 30) -> List[Dict]:
        """获取历史数据"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM stock_data 
            WHERE code = ? 
            AND created_at > datetime('now', '-{} days')
            ORDER BY created_at DESC
        '''.format(days), (code,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]

# ==================== 全局实例 ====================

fusion_engine = DataFusionEngine()

# ==================== API 路由 ====================

@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "青龙 Stock MCP Server",
        "version": "4.5.0",
        "features": [
            "腾讯 API 实时数据",
            "Chrome MCP 网页抓取",
            "多源数据融合",
            "本地数据库存储"
        ]
    }

@app.get("/stock/{code}")
async def get_stock(code: str, use_chrome: bool = True):
    """获取股票数据"""
    data = fusion_engine.fetch_stock_data(code, use_chrome=use_chrome)
    
    if not data:
        raise HTTPException(status_code=404, detail=f"无法获取股票 {code} 的数据")
    
    return data

@app.get("/stock/{code}/history")
async def get_stock_history(code: str, days: int = 30):
    """获取股票历史数据"""
    data = fusion_engine.get_historical_data(code, days)
    return {
        "code": code,
        "days": days,
        "count": len(data),
        "data": data
    }

@app.post("/chrome/start")
async def start_chrome():
    """手动启动 Chrome MCP"""
    success = fusion_engine.chrome_manager.start_chrome()
    return {"success": success, "status": "running" if success else "failed"}

@app.post("/chrome/stop")
async def stop_chrome():
    """手动停止 Chrome MCP"""
    fusion_engine.chrome_manager.stop_chrome()
    return {"success": True, "status": "stopped"}

@app.get("/chrome/status")
async def chrome_status():
    """检查 Chrome MCP 状态"""
    return {
        "is_running": fusion_engine.chrome_manager.is_running,
        "port": fusion_engine.chrome_manager.port
    }

# ==================== 启动 ====================

@app.on_event("startup")
async def startup_event():
    """启动时自动启动 Chrome MCP"""
    print("🐉 青龙 Stock MCP Server v4.5.0 启动中...")
    print("🚀 正在启动 Chrome MCP...")
    fusion_engine.chrome_manager.start_chrome()

@app.on_event("shutdown")
async def shutdown_event():
    """关闭时停止 Chrome MCP"""
    print("🛑 正在停止 Chrome MCP...")
    fusion_engine.chrome_manager.stop_chrome()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
