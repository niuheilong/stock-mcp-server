#!/usr/bin/env python3
"""
青龙历史回测框架 v4.3.0
数据存储 + 回测计算 + 评分验证
"""

import sqlite3
import json
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import statistics


@dataclass
class HistoricalRecord:
    """历史分析记录"""
    id: Optional[int] = None
    code: str = ""
    name: str = ""
    timestamp: str = ""
    price: float = 0.0
    change_percent: float = 0.0
    
    # 各维度评分
    qinglong_score: float = 0.0
    tech_score: float = 0.0
    sentiment_score: float = 0.0
    flow_score: float = 0.0
    sector_score: float = 0.0
    fund_score: float = 0.0
    
    # 资金流向
    main_inflow: float = 0.0
    main_inflow_percent: float = 0.0
    northbound_hold_percent: Optional[float] = None
    
    # 板块信息
    sector_name: str = ""
    sector_rank: int = 0
    is_sector_leader: bool = False
    
    # 建议
    recommendation: str = ""
    
    # 后续表现 (用于回测验证)
    future_1d_return: Optional[float] = None
    future_3d_return: Optional[float] = None
    future_5d_return: Optional[float] = None
    future_10d_return: Optional[float] = None


@dataclass
class BacktestResult:
    """回测结果"""
    code: str = ""
    name: str = ""
    total_signals: int = 0
    
    # 胜率统计
    win_rate_1d: float = 0.0
    win_rate_3d: float = 0.0
    win_rate_5d: float = 0.0
    win_rate_10d: float = 0.0
    
    # 收益统计
    avg_return_1d: float = 0.0
    avg_return_3d: float = 0.0
    avg_return_5d: float = 0.0
    avg_return_10d: float = 0.0
    
    # 最大回撤
    max_drawdown_1d: float = 0.0
    max_drawdown_3d: float = 0.0
    max_drawdown_5d: float = 0.0
    max_drawdown_10d: float = 0.0
    
    # 评分准确性
    score_accuracy: float = 0.0  # 评分与实际收益的相关性
    
    # 建议有效性
    strong_buy_win_rate: float = 0.0
    buy_win_rate: float = 0.0
    neutral_win_rate: float = 0.0
    sell_win_rate: float = 0.0


class HistoryDatabase:
    """历史数据数据库"""
    
    def __init__(self, db_path: str = "qinglong_history.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建历史记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL,
                name TEXT,
                timestamp TEXT NOT NULL,
                price REAL,
                change_percent REAL,
                qinglong_score REAL,
                tech_score REAL,
                sentiment_score REAL,
                flow_score REAL,
                sector_score REAL,
                fund_score REAL,
                main_inflow REAL,
                main_inflow_percent REAL,
                northbound_hold_percent REAL,
                sector_name TEXT,
                sector_rank INTEGER,
                is_sector_leader INTEGER,
                recommendation TEXT,
                future_1d_return REAL,
                future_3d_return REAL,
                future_5d_return REAL,
                future_10d_return REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建索引
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_code_timestamp 
            ON analysis_history(code, timestamp)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON analysis_history(timestamp)
        ''')
        
        conn.commit()
        conn.close()
    
    def save_record(self, record: HistoricalRecord) -> int:
        """保存分析记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO analysis_history (
                code, name, timestamp, price, change_percent,
                qinglong_score, tech_score, sentiment_score, flow_score, sector_score, fund_score,
                main_inflow, main_inflow_percent, northbound_hold_percent,
                sector_name, sector_rank, is_sector_leader,
                recommendation,
                future_1d_return, future_3d_return, future_5d_return, future_10d_return
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            record.code, record.name, record.timestamp, record.price, record.change_percent,
            record.qinglong_score, record.tech_score, record.sentiment_score, 
            record.flow_score, record.sector_score, record.fund_score,
            record.main_inflow, record.main_inflow_percent, record.northbound_hold_percent,
            record.sector_name, record.sector_rank, 1 if record.is_sector_leader else 0,
            record.recommendation,
            record.future_1d_return, record.future_3d_return, 
            record.future_5d_return, record.future_10d_return
        ))
        
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return record_id
    
    def get_records(self, code: str = None, start_date: str = None, 
                    end_date: str = None, limit: int = 100) -> List[HistoricalRecord]:
        """查询历史记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM analysis_history WHERE 1=1"
        params = []
        
        if code:
            query += " AND code = ?"
            params.append(code)
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        records = []
        for row in rows:
            record = HistoricalRecord(
                id=row[0],
                code=row[1],
                name=row[2],
                timestamp=row[3],
                price=row[4],
                change_percent=row[5],
                qinglong_score=row[6],
                tech_score=row[7],
                sentiment_score=row[8],
                flow_score=row[9],
                sector_score=row[10],
                fund_score=row[11],
                main_inflow=row[12],
                main_inflow_percent=row[13],
                northbound_hold_percent=row[14],
                sector_name=row[15],
                sector_rank=row[16],
                is_sector_leader=bool(row[17]),
                recommendation=row[18],
                future_1d_return=row[19],
                future_3d_return=row[20],
                future_5d_return=row[21],
                future_10d_return=row[22]
            )
            records.append(record)
        
        return records
    
    def update_future_returns(self, record_id: int, returns: Dict[str, float]):
        """更新未来收益数据（用于回测验证）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE analysis_history SET
                future_1d_return = ?,
                future_3d_return = ?,
                future_5d_return = ?,
                future_10d_return = ?
            WHERE id = ?
        ''', (
            returns.get('1d'),
            returns.get('3d'),
            returns.get('5d'),
            returns.get('10d'),
            record_id
        ))
        
        conn.commit()
        conn.close()


class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, db: HistoryDatabase):
        self.db = db
    
    def calculate_backtest(self, code: str = None, min_score: float = 60,
                          days: int = 30) -> BacktestResult:
        """计算回测结果"""
        # 获取历史记录
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        records = self.db.get_records(code=code, start_date=start_date)
        
        if not records:
            return BacktestResult(code=code or "ALL", total_signals=0)
        
        # 筛选符合条件的信号（如评分>=60）
        signals = [r for r in records if r.qinglong_score >= min_score]
        
        if not signals:
            return BacktestResult(code=code or "ALL", total_signals=0)
        
        result = BacktestResult(
            code=code or "ALL",
            name=signals[0].name if signals else "",
            total_signals=len(signals)
        )
        
        # 计算各时间周期的胜率和收益
        for period in ['1d', '3d', '5d', '10d']:
            returns = []
            wins = 0
            max_dd = 0
            
            attr_name = f'future_{period}_return'
            
            for signal in signals:
                ret = getattr(signal, attr_name)
                if ret is not None:
                    returns.append(ret)
                    if ret > 0:
                        wins += 1
                    if ret < max_dd:
                        max_dd = ret
            
            if returns:
                win_rate = wins / len(returns) * 100
                avg_return = statistics.mean(returns)
                
                setattr(result, f'win_rate_{period}', round(win_rate, 2))
                setattr(result, f'avg_return_{period}', round(avg_return, 2))
                setattr(result, f'max_drawdown_{period}', round(max_dd, 2))
        
        # 计算评分准确性（评分与实际收益的相关性）
        scores = [s.qinglong_score for s in signals]
        returns_1d = [s.future_1d_return for s in signals if s.future_1d_return is not None]
        
        if len(scores) > 1 and len(returns_1d) > 1:
            try:
                # 简单相关性计算
                mean_score = statistics.mean(scores[:len(returns_1d)])
                mean_ret = statistics.mean(returns_1d)
                
                numerator = sum((s - mean_score) * (r - mean_ret) 
                              for s, r in zip(scores[:len(returns_1d)], returns_1d))
                denom_score = sum((s - mean_score) ** 2 for s in scores[:len(returns_1d)])
                denom_ret = sum((r - mean_ret) ** 2 for r in returns_1d)
                
                if denom_score > 0 and denom_ret > 0:
                    correlation = numerator / (denom_score ** 0.5 * denom_ret ** 0.5)
                    result.score_accuracy = round(correlation, 2)
            except:
                result.score_accuracy = 0.0
        
        # 按建议类型统计胜率
        rec_groups = {
            '强烈推荐': [],
            '推荐': [],
            '中性': [],
            '谨慎': [],
            '回避': []
        }
        
        for signal in signals:
            rec = signal.recommendation
            if '强烈推荐' in rec:
                rec_groups['强烈推荐'].append(signal)
            elif '推荐' in rec and '强烈推荐' not in rec:
                rec_groups['推荐'].append(signal)
            elif '中性' in rec:
                rec_groups['中性'].append(signal)
            elif '谨慎' in rec:
                rec_groups['谨慎'].append(signal)
            elif '回避' in rec:
                rec_groups['回避'].append(signal)
        
        for rec_type, rec_signals in rec_groups.items():
            if rec_signals:
                wins = sum(1 for s in rec_signals 
                          if s.future_1d_return is not None and s.future_1d_return > 0)
                total = sum(1 for s in rec_signals if s.future_1d_return is not None)
                win_rate = wins / total * 100 if total > 0 else 0
                
                attr_name = {
                    '强烈推荐': 'strong_buy_win_rate',
                    '推荐': 'buy_win_rate',
                    '中性': 'neutral_win_rate',
                    '谨慎': 'sell_win_rate',
                    '回避': 'sell_win_rate'
                }.get(rec_type, '')
                
                if attr_name and hasattr(result, attr_name):
                    setattr(result, attr_name, round(win_rate, 2))
        
        return result
    
    def generate_report(self, backtest: BacktestResult) -> str:
        """生成回测报告"""
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║                 青龙回测报告                                  ║
╠══════════════════════════════════════════════════════════════╣
  股票代码: {backtest.code}
  股票名称: {backtest.name}
  信号总数: {backtest.total_signals}
╠══════════════════════════════════════════════════════════════╣
  胜率统计:
    1日胜率: {backtest.win_rate_1d}% (平均收益: {backtest.avg_return_1d}%)
    3日胜率: {backtest.win_rate_3d}% (平均收益: {backtest.avg_return_3d}%)
    5日胜率: {backtest.win_rate_5d}% (平均收益: {backtest.avg_return_5d}%)
   10日胜率: {backtest.win_rate_10d}% (平均收益: {backtest.avg_return_10d}%)
╠══════════════════════════════════════════════════════════════╣
  最大回撤:
    1日最大回撤: {backtest.max_drawdown_1d}%
    3日最大回撤: {backtest.max_drawdown_3d}%
    5日最大回撤: {backtest.max_drawdown_5d}%
   10日最大回撤: {backtest.max_drawdown_10d}%
╠══════════════════════════════════════════════════════════════╣
  评分准确性: {backtest.score_accuracy}
╠══════════════════════════════════════════════════════════════╣
  建议有效性 (1日胜率):
    强烈推荐: {backtest.strong_buy_win_rate}%
    推荐: {backtest.buy_win_rate}%
    中性: {backtest.neutral_win_rate}%
    谨慎/回避: {backtest.sell_win_rate}%
╚══════════════════════════════════════════════════════════════╝
"""
        return report


# 测试代码
if __name__ == "__main__":
    print("=" * 60)
    print("测试: 历史回测框架")
    print("=" * 60)
    
    # 初始化数据库
    db = HistoryDatabase("test_history.db")
    
    # 保存测试记录
    test_record = HistoricalRecord(
        code="sh600410",
        name="华胜天成",
        timestamp=datetime.now().isoformat(),
        price=26.60,
        change_percent=-6.6,
        qinglong_score=85.5,
        tech_score=70.0,
        sentiment_score=80.0,
        flow_score=90.0,
        sector_score=75.0,
        fund_score=60.0,
        main_inflow=2570059760,
        main_inflow_percent=40.63,
        northbound_hold_percent=11.86,
        sector_name="电子",
        sector_rank=3,
        is_sector_leader=False,
        recommendation="强烈推荐",
        future_1d_return=2.5,
        future_3d_return=5.0,
        future_5d_return=8.0
    )
    
    record_id = db.save_record(test_record)
    print(f"✅ 保存测试记录，ID: {record_id}")
    
    # 查询记录
    records = db.get_records(code="sh600410")
    print(f"✅ 查询到 {len(records)} 条记录")
    
    # 回测计算
    engine = BacktestEngine(db)
    result = engine.calculate_backtest(code="sh600410", min_score=60, days=30)
    
    print("\n" + engine.generate_report(result))
    
    print("=" * 60)
    print("测试完成!")
    print("=" * 60)
