#!/usr/bin/env python3
"""
青龙 Chrome MCP 数据分析
分析抓取的股票数据，生成报告
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict


class StockAnalyzer:
    """股票数据分析器"""
    
    def __init__(self, db_path: str = "qinglong_stock_data.db"):
        self.db_path = db_path
    
    def get_latest_data(self, code: str = None, limit: int = 10) -> List[Dict]:
        """获取最新数据"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if code:
            cursor.execute('''
                SELECT * FROM stock_data 
                WHERE code = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (code, limit))
        else:
            cursor.execute('''
                SELECT * FROM stock_data 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def analyze_trend(self, code: str) -> Dict:
        """分析股票趋势"""
        data = self.get_latest_data(code, limit=20)
        
        if not data:
            return {"error": "无数据"}
        
        prices = [d['price'] for d in data if d['price']]
        changes = [d['change_percent'] for d in data if d['change_percent']]
        
        if not prices:
            return {"error": "无价格数据"}
        
        return {
            "code": code,
            "data_points": len(data),
            "latest_price": prices[0],
            "avg_price": sum(prices) / len(prices),
            "max_price": max(prices),
            "min_price": min(prices),
            "avg_change": sum(changes) / len(changes) if changes else 0,
            "trend": "上涨" if changes and changes[0] > 0 else "下跌" if changes and changes[0] < 0 else "平盘"
        }
    
    def generate_report(self) -> str:
        """生成分析报告"""
        data = self.get_latest_data(limit=50)
        
        if not data:
            return "暂无数据"
        
        report = []
        report.append("=" * 60)
        report.append("🐉 青龙 Chrome MCP 股票分析报告")
        report.append("=" * 60)
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"数据条数: {len(data)}")
        report.append("")
        
        # 按股票分组
        stocks = {}
        for item in data:
            code = item['code']
            if code not in stocks:
                stocks[code] = []
            stocks[code].append(item)
        
        report.append("📊 股票概况:")
        report.append("-" * 60)
        
        for code, items in stocks.items():
            latest = items[0]
            report.append(f"\n{code} - {latest.get('name', 'N/A')}:")
            report.append(f"  最新价: ¥{latest.get('price', 'N/A')}")
            report.append(f"  涨跌幅: {latest.get('change_percent', 'N/A')}%")
            report.append(f"  数据点: {len(items)} 条")
            
            # 趋势分析
            trend = self.analyze_trend(code)
            if 'trend' in trend:
                report.append(f"  趋势: {trend['trend']}")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)


def main():
    """主函数"""
    analyzer = StockAnalyzer()
    
    print(analyzer.generate_report())
    
    # 保存报告
    report = analyzer.generate_report()
    report_file = f"/Users/laoniu/.openclaw/workspace/stock-mcp-server/reports/stock_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    import os
    os.makedirs(os.path.dirname(report_file), exist_ok=True)
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"\n✅ 报告已保存: {report_file}")


if __name__ == "__main__":
    main()
