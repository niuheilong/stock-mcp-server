#!/usr/bin/env python3
"""
青龙资源管理器 v1.0
自动清理浏览器、压缩文件、释放缓存
"""

import os
import gc
import time
import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import threading


class ResourceManager:
    """资源管理器"""
    
    def __init__(self, workspace_dir: str = None):
        self.workspace_dir = workspace_dir or os.path.expanduser("~/.openclaw/workspace")
        self.running = False
        self.cleanup_thread = None
        
        # 阈值配置
        self.thresholds = {
            "memory_check_interval": 300,  # 5分钟检查一次
            "browser_max_idle": 600,       # 浏览器最大空闲10分钟
            "file_size_threshold": 10 * 1024 * 1024,  # 10MB压缩
            "cache_max_age": 3600,         # 缓存1小时
            "log_max_age": 7 * 24 * 3600,  # 日志7天
        }
        
        # 状态追踪
        self.browser_last_used = None
        self.last_cleanup = datetime.now()
        
    def start_monitor(self):
        """启动资源监控线程"""
        self.running = True
        self.cleanup_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.cleanup_thread.start()
        print(f"✅ 资源管理器已启动 - 工作区: {self.workspace_dir}")
        
    def stop_monitor(self):
        """停止资源监控"""
        self.running = False
        if self.cleanup_thread:
            self.cleanup_thread.join(timeout=5)
        print("✅ 资源管理器已停止")
        
    def _monitor_loop(self):
        """监控循环"""
        while self.running:
            try:
                self._check_browser_idle()
                self._compress_large_files()
                self._cleanup_cache()
                self._cleanup_logs()
                gc.collect()  # Python垃圾回收
                
                time.sleep(self.thresholds["memory_check_interval"])
            except Exception as e:
                print(f"⚠️ 资源监控错误: {e}")
                time.sleep(60)
                
    def _check_browser_idle(self):
        """检查浏览器空闲状态"""
        if self.browser_last_used:
            idle_time = (datetime.now() - self.browser_last_used).total_seconds()
            if idle_time > self.thresholds["browser_max_idle"]:
                print(f"🌐 浏览器空闲 {idle_time:.0f}秒，建议关闭")
                # 这里可以调用浏览器关闭逻辑
                
    def _compress_large_files(self):
        """压缩大文件"""
        compressed_count = 0
        
        for root, dirs, files in os.walk(self.workspace_dir):
            # 跳过已压缩的目录
            if '.compressed' in root or 'backups' in root:
                continue
                
            for file in files:
                if file.endswith(('.gz', '.zip', '.tar.gz')):
                    continue
                    
                file_path = os.path.join(root, file)
                try:
                    size = os.path.getsize(file_path)
                    
                    # 大于阈值且是日志/数据文件
                    if size > self.thresholds["file_size_threshold"]:
                        if any(ext in file for ext in ['.log', '.db', '.json', '.txt', '.md']):
                            self._compress_file(file_path)
                            compressed_count += 1
                            
                except Exception as e:
                    continue
                    
        if compressed_count > 0:
            print(f"📦 压缩了 {compressed_count} 个大文件")
            
    def _compress_file(self, file_path: str):
        """压缩单个文件"""
        try:
            compressed_path = f"{file_path}.gz"
            
            with open(file_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
                    
            # 验证压缩成功后再删除原文件
            if os.path.exists(compressed_path):
                original_size = os.path.getsize(file_path)
                compressed_size = os.path.getsize(compressed_path)
                
                if compressed_size < original_size * 0.9:  # 压缩率>10%
                    os.remove(file_path)
                    print(f"  ✓ {os.path.basename(file_path)}: {original_size/1024/1024:.1f}MB → {compressed_size/1024/1024:.1f}MB")
                    
        except Exception as e:
            print(f"  ✗ 压缩失败 {file_path}: {e}")
            
    def _cleanup_cache(self):
        """清理缓存文件"""
        cache_dirs = [
            os.path.join(self.workspace_dir, '.cache'),
            os.path.join(self.workspace_dir, 'temp'),
            '/tmp/openclaw_*',
        ]
        
        cleaned = 0
        for pattern in cache_dirs:
            if '*' in pattern:
                import glob
                paths = glob.glob(pattern)
            else:
                paths = [pattern] if os.path.exists(pattern) else []
                
            for path in paths:
                try:
                    if os.path.isfile(path):
                        age = time.time() - os.path.getmtime(path)
                        if age > self.thresholds["cache_max_age"]:
                            os.remove(path)
                            cleaned += 1
                    elif os.path.isdir(path):
                        for item in os.listdir(path):
                            item_path = os.path.join(path, item)
                            age = time.time() - os.path.getmtime(item_path)
                            if age > self.thresholds["cache_max_age"]:
                                if os.path.isfile(item_path):
                                    os.remove(item_path)
                                else:
                                    shutil.rmtree(item_path)
                                cleaned += 1
                except Exception as e:
                    continue
                    
        if cleaned > 0:
            print(f"🧹 清理了 {cleaned} 个缓存文件")
            
    def _cleanup_logs(self):
        """清理旧日志"""
        log_dirs = [
            os.path.join(self.workspace_dir, 'logs'),
            os.path.join(self.workspace_dir, 'memory'),
        ]
        
        cleaned = 0
        for log_dir in log_dirs:
            if not os.path.exists(log_dir):
                continue
                
            for file in os.listdir(log_dir):
                if file.endswith(('.log', '.md')):
                    file_path = os.path.join(log_dir, file)
                    try:
                        age = time.time() - os.path.getmtime(file_path)
                        if age > self.thresholds["log_max_age"]:
                            # 先压缩再删除
                            if not file.endswith('.gz'):
                                self._compress_file(file_path)
                            else:
                                os.remove(file_path)
                            cleaned += 1
                    except Exception as e:
                        continue
                        
        if cleaned > 0:
            print(f"📝 归档了 {cleaned} 个旧日志")
            
    def report_status(self) -> dict:
        """报告资源状态"""
        status = {
            "workspace_size": self._get_dir_size(self.workspace_dir),
            "browser_idle": self._get_browser_idle_time(),
            "last_cleanup": self.last_cleanup.isoformat(),
            "large_files": self._find_large_files(),
        }
        return status
        
    def _get_dir_size(self, path: str) -> int:
        """获取目录大小"""
        total = 0
        try:
            for entry in os.scandir(path):
                if entry.is_file():
                    total += entry.stat().st_size
                elif entry.is_dir():
                    total += self._get_dir_size(entry.path)
        except:
            pass
        return total
        
    def _get_browser_idle_time(self) -> float:
        """获取浏览器空闲时间"""
        if self.browser_last_used:
            return (datetime.now() - self.browser_last_used).total_seconds()
        return 0
        
    def _find_large_files(self, threshold_mb: int = 10) -> list:
        """查找大文件"""
        large_files = []
        threshold = threshold_mb * 1024 * 1024
        
        for root, dirs, files in os.walk(self.workspace_dir):
            for file in files:
                if file.endswith('.gz'):
                    continue
                file_path = os.path.join(root, file)
                try:
                    size = os.path.getsize(file_path)
                    if size > threshold:
                        large_files.append({
                            "path": file_path,
                            "size_mb": size / 1024 / 1024
                        })
                except:
                    continue
                    
        return sorted(large_files, key=lambda x: x["size_mb"], reverse=True)[:10]
        
    def force_cleanup(self):
        """强制清理所有资源"""
        print("🧹 强制清理资源...")
        self._compress_large_files()
        self._cleanup_cache()
        self._cleanup_logs()
        gc.collect()
        self.last_cleanup = datetime.now()
        print("✅ 强制清理完成")


# 使用示例
if __name__ == "__main__":
    manager = ResourceManager()
    
    # 启动监控
    manager.start_monitor()
    
    try:
        # 运行一段时间
        print("资源管理器运行中，按 Ctrl+C 停止")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # 停止监控
        manager.stop_monitor()
        
        # 报告状态
        status = manager.report_status()
        print("\n资源状态报告:")
        print(f"  工作区大小: {status['workspace_size']/1024/1024:.1f}MB")
        print(f"  浏览器空闲: {status['browser_idle']:.0f}秒")
        print(f"  上次清理: {status['last_cleanup']}")
        print(f"  大文件数量: {len(status['large_files'])}")
