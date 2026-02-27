#!/usr/bin/env python3
"""
Jina Reader 集成模块
用于增强网页抓取能力，替代/补充 web_fetch

Jina Reader 优势：
- 免费使用
- 自动将网页转为 Markdown（LLM-friendly）
- 支持自定义 Cookie（可绕过登录限制）
- 成功率高于直接请求

API: https://r.jina.ai/http://URL
文档: https://jina.ai/reader/
"""

import requests
import time
from typing import Optional, Dict


def fetch_with_jina(url: str, timeout: int = 30, cookie: Optional[str] = None) -> Dict:
    """
    使用 Jina Reader 获取网页内容
    
    Args:
        url: 目标网页 URL
        timeout: 超时时间（秒）
        cookie: 可选的 Cookie 字符串（用于绕过登录）
    
    Returns:
        Dict: 包含 content, status, url 的字典
    """
    try:
        # Jina Reader API 格式
        jina_url = f"https://r.jina.ai/http://{url.replace('https://', '').replace('http://', '')}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; OpenClaw/1.0)"
        }
        
        # 如果有 Cookie，添加到请求头
        if cookie:
            headers["x-with-cookie"] = cookie
        
        # 发送请求
        response = requests.get(jina_url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        return {
            "success": True,
            "content": response.text,
            "url": url,
            "source": "jina_reader",
            "status_code": response.status_code
        }
        
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Request timeout",
            "url": url,
            "source": "jina_reader"
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": str(e),
            "url": url,
            "source": "jina_reader"
        }


def fetch_with_fallback(url: str, timeout: int = 30, max_retries: int = 2) -> Dict:
    """
    智能抓取：先尝试 web_fetch，失败后用 Jina Reader
    
    Args:
        url: 目标网页 URL
        timeout: 超时时间
        max_retries: 重试次数
    
    Returns:
        Dict: 抓取结果
    """
    # 尝试 1：直接请求（最快）
    try:
        response = requests.get(url, timeout=timeout, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        if response.status_code == 200:
            return {
                "success": True,
                "content": response.text,
                "url": url,
                "source": "direct",
                "status_code": 200
            }
    except:
        pass
    
    # 尝试 2：Jina Reader（更稳定）
    for i in range(max_retries):
        result = fetch_with_jina(url, timeout)
        if result["success"]:
            return result
        time.sleep(1)  # 失败后等待 1 秒重试
    
    # 都失败了
    return {
        "success": False,
        "error": "All fetch methods failed",
        "url": url
    }


def extract_video_subtitle(url: str) -> Dict:
    """
    提取视频字幕（YouTube/B站等）
    使用 yt-dlp 或 Jina 的视频支持
    
    注意：这需要 yt-dlp 已安装
    """
    try:
        import subprocess
        import json
        
        # 使用 yt-dlp 提取字幕
        cmd = [
            "yt-dlp",
            "--dump-json",
            "--write-auto-sub",
            "--skip-download",
            url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            data = json.loads(result.stdout.split('\n')[0])
            return {
                "success": True,
                "title": data.get("title"),
                "description": data.get("description"),
                "subtitles": data.get("subtitles", {}),
                "automatic_captions": data.get("automatic_captions", {}),
                "url": url,
                "source": "yt-dlp"
            }
        else:
            return {
                "success": False,
                "error": result.stderr,
                "url": url
            }
            
    except FileNotFoundError:
        return {
            "success": False,
            "error": "yt-dlp not installed. Install with: pip install yt-dlp",
            "url": url
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "url": url
        }


# 简单测试
if __name__ == "__main__":
    # 测试网页抓取
    test_url = "https://github.com/Panniantong/Agent-Reach"
    result = fetch_with_jina(test_url)
    
    if result["success"]:
        print(f"✅ 成功获取: {result['url']}")
        print(f"📄 内容长度: {len(result['content'])} 字符")
        print(f"🔧 来源: {result['source']}")
        print("\n--- 前 500 字符预览 ---")
        print(result["content"][:500])
    else:
        print(f"❌ 失败: {result.get('error')}")
