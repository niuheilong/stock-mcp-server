#!/usr/bin/env python3
"""
青龙板块联动分析模块 v4.2.0
东方财富API集成 - 板块热度、个股联动、龙头识别
"""

import requests
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict


@dataclass
class SectorData:
    """板块数据"""
    code: str  # 板块代码，如 BK1201
    name: str  # 板块名称，如 "电子"
    change_percent: float  # 涨跌幅
    main_inflow: float  # 主力净流入
    total_market_cap: float  # 总市值
    stock_count: int  # 成分股数量
    leading_stocks: List[Dict] = field(default_factory=list)  # 领涨股


@dataclass
class StockSectorInfo:
    """个股板块信息"""
    code: str  # 股票代码
    name: str  # 股票名称
    industry: str  # 所属行业
    region: str  # 所属地区
    concepts: List[str]  # 概念题材
    sector_codes: List[str]  # 关联板块代码


@dataclass
class SectorLinkage:
    """板块联动分析"""
    target_code: str  # 目标股票代码
    target_name: str  # 目标股票名称
    sector_code: str  # 板块代码
    sector_name: str  # 板块名称
    sector_change: float  # 板块涨跌幅
    sector_rank: int  # 板块排名
    peer_stocks: List[Dict]  # 同板块其他股票
    leading_stock: Optional[Dict]  # 板块龙头股
    following_stocks: List[Dict]  # 跟风股
    correlation_score: float  # 联动相关性得分
    is_leader: bool  # 目标股是否为龙头
    is_follower: bool  # 目标股是否为跟风


class SectorAnalyzer:
    """板块分析器"""
    
    BASE_URL = "http://push2.eastmoney.com/api/qt/clist/get"
    
    # 板块类型映射
    SECTOR_TYPES = {
        "industry": "m:90+t:2",  # 行业板块
        "concept": "m:90+t:3",   # 概念板块
        "region": "m:90+t:1",    # 地区板块
    }
    
    def __init__(self):
        self.sector_cache = {}  # 板块缓存
        self.stock_sector_cache = {}  # 个股板块缓存
    
    def fetch_sectors(self, sector_type: str = "industry", top_n: int = 20) -> List[SectorData]:
        """获取板块列表（按热度排名）"""
        try:
            fs = self.SECTOR_TYPES.get(sector_type, "m:90+t:2")
            url = f"{self.BASE_URL}?pn=1&pz={top_n}&po=1&np=1&fltt=2&invt=2&fid=f20&fs={fs}&fields=f12,f14,f20,f22,f62"
            
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data.get("rc") != 0 or not data.get("data"):
                return []
            
            sectors = []
            for i, item in enumerate(data["data"].get("diff", [])):
                sector = SectorData(
                    code=item.get("f12", ""),
                    name=item.get("f14", ""),
                    change_percent=float(item.get("f22", 0) or 0),
                    main_inflow=float(item.get("f62", 0) or 0),
                    total_market_cap=float(item.get("f20", 0) or 0),
                    stock_count=0  # 需要另外获取
                )
                sectors.append(sector)
            
            return sectors
        except Exception as e:
            print(f"Error fetching sectors: {e}")
            return []
    
    def fetch_sector_stocks(self, sector_code: str, top_n: int = 30) -> List[Dict]:
        """获取板块成分股（按涨幅排名）"""
        try:
            url = f"{self.BASE_URL}?pn=1&pz={top_n}&po=1&np=1&fltt=2&invt=2&fid=f22&fs=b:{sector_code}&fields=f12,f13,f14,f20,f22,f62"
            
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data.get("rc") != 0 or not data.get("data"):
                return []
            
            stocks = []
            for item in data["data"].get("diff", []):
                stock = {
                    "code": item.get("f12", ""),
                    "market": item.get("f13", 0),  # 0=深证, 1=上证
                    "name": item.get("f14", ""),
                    "market_cap": float(item.get("f20", 0) or 0),
                    "change_percent": float(item.get("f22", 0) or 0),
                    "main_inflow": float(item.get("f62", 0) or 0),
                }
                stocks.append(stock)
            
            return stocks
        except Exception as e:
            print(f"Error fetching sector stocks: {e}")
            return []
    
    def get_stock_sector_info(self, code: str, raw_data: Dict = None) -> Optional[StockSectorInfo]:
        """获取个股板块信息"""
        if code in self.stock_sector_cache:
            return self.stock_sector_cache[code]
        
        if not raw_data:
            # 需要从外部获取原始数据
            return None
        
        # 从东方财富原始数据解析
        # f127=行业, f128=地区, f129=概念
        industry = raw_data.get("f127", "未知行业")
        region = raw_data.get("f128", "未知地区")
        concepts_str = raw_data.get("f129", "")
        concepts = [c.strip() for c in concepts_str.split(",") if c.strip()]
        name = raw_data.get("f58", "")
        
        info = StockSectorInfo(
            code=code,
            name=name,
            industry=industry,
            region=region,
            concepts=concepts,
            sector_codes=[]  # 需要映射
        )
        
        self.stock_sector_cache[code] = info
        return info
    
    def analyze_sector_linkage(self, code: str, raw_data: Dict = None) -> List[SectorLinkage]:
        """分析个股板块联动关系"""
        # 获取个股板块信息
        stock_info = self.get_stock_sector_info(code, raw_data)
        if not stock_info:
            return []
        
        linkages = []
        
        # 1. 分析行业板块联动
        industry_sectors = self.fetch_sectors("industry", top_n=50)
        
        for rank, sector in enumerate(industry_sectors, 1):
            # 获取板块成分股
            sector_stocks = self.fetch_sector_stocks(sector.code, top_n=50)
            
            # 检查目标股票是否在该板块
            stock_in_sector = any(
                s["code"] == code.replace("sh", "").replace("sz", "").replace("bj", "")
                for s in sector_stocks
            )
            
            if not stock_in_sector:
                continue
            
            # 识别龙头和跟风
            leading_stock = sector_stocks[0] if sector_stocks else None
            target_stock = next(
                (s for s in sector_stocks if s["code"] == code.replace("sh", "").replace("sz", "").replace("bj", "")),
                None
            )
            
            # 计算相关性得分
            correlation_score = 50  # 基础分
            
            # 如果板块涨幅高，相关性加分
            if sector.change_percent > 2:
                correlation_score += 20
            elif sector.change_percent > 0:
                correlation_score += 10
            
            # 如果主力流入，加分
            if sector.main_inflow > 0:
                correlation_score += 15
            
            # 判断龙头/跟风
            is_leader = False
            is_follower = False
            
            if target_stock:
                target_rank = next(
                    (i for i, s in enumerate(sector_stocks) if s["code"] == target_stock["code"]),
                    len(sector_stocks)
                )
                
                if target_rank == 0:
                    is_leader = True
                    correlation_score += 15
                elif target_rank <= 3:
                    correlation_score += 10
                elif target_rank <= 10:
                    is_follower = True
                else:
                    correlation_score -= 10
            
            # 跟风股（涨幅滞后于板块）
            following_stocks = [
                s for s in sector_stocks[5:15]
                if s["change_percent"] < sector.change_percent
            ]
            
            linkage = SectorLinkage(
                target_code=code,
                target_name=stock_info.name,
                sector_code=sector.code,
                sector_name=sector.name,
                sector_change=sector.change_percent,
                sector_rank=rank,
                peer_stocks=sector_stocks[:10],
                leading_stock=leading_stock,
                following_stocks=following_stocks,
                correlation_score=min(100, correlation_score),
                is_leader=is_leader,
                is_follower=is_follower
            )
            
            linkages.append(linkage)
        
        return linkages
    
    def calculate_sector_score(self, linkages: List[SectorLinkage]) -> Dict:
        """计算板块联动得分"""
        if not linkages:
            return {
                "score": 50,
                "level": "中性",
                "description": "暂无板块联动数据"
            }
        
        # 取最高相关性的板块
        best_linkage = max(linkages, key=lambda x: x.correlation_score)
        
        score = best_linkage.correlation_score
        
        # 根据板块排名调整
        if best_linkage.sector_rank <= 5:
            score += 10
        elif best_linkage.sector_rank <= 10:
            score += 5
        elif best_linkage.sector_rank > 30:
            score -= 10
        
        score = min(100, max(0, score))
        
        # 确定等级
        if score >= 80:
            level = "板块强势"
            description = f"所属{best_linkage.sector_name}板块排名第{best_linkage.sector_rank}，表现强势"
        elif score >= 60:
            level = "板块良好"
            description = f"所属{best_linkage.sector_name}板块表现良好"
        elif score >= 40:
            level = "板块中性"
            description = f"所属{best_linkage.sector_name}板块表现一般"
        else:
            level = "板块弱势"
            description = f"所属{best_linkage.sector_name}板块表现弱势"
        
        if best_linkage.is_leader:
            description += "，该股为板块龙头"
        elif best_linkage.is_follower:
            description += "，该股为跟风股"
        
        return {
            "score": round(score, 1),
            "level": level,
            "description": description,
            "best_sector": best_linkage.sector_name,
            "sector_rank": best_linkage.sector_rank,
            "is_leader": best_linkage.is_leader,
            "is_follower": best_linkage.is_follower
        }


# 测试代码
if __name__ == "__main__":
    analyzer = SectorAnalyzer()
    
    print("=" * 60)
    print("测试1: 获取热门板块")
    print("=" * 60)
    
    sectors = analyzer.fetch_sectors("industry", top_n=10)
    for i, sector in enumerate(sectors[:5], 1):
        print(f"{i}. {sector.name}: {sector.change_percent:+.2f}% (主力: {sector.main_inflow/1e8:.1f}亿)")
    
    print("\n" + "=" * 60)
    print("测试2: 获取板块成分股 (电子板块 BK1201)")
    print("=" * 60)
    
    stocks = analyzer.fetch_sector_stocks("BK1201", top_n=10)
    for i, stock in enumerate(stocks[:5], 1):
        print(f"{i}. {stock['name']}({stock['code']}): {stock['change_percent']:+.2f}%")
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)
