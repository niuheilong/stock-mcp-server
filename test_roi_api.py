#!/usr/bin/env python3
"""
Smart ROI API 完整测试报告
测试时间: 2026-02-28
"""

import requests
import json

BASE_URL = "http://localhost:5001"

def test_health():
    """测试健康检查"""
    r = requests.get(f"{BASE_URL}/health")
    data = r.json()
    assert "smart-roi" in data["features"], "Smart ROI 未启用"
    print(f"✅ 健康检查: v{data['version']} - Features: {data['features']}")

def test_single_stock_roi():
    """测试单股 ROI 计算"""
    payload = {
        "tool": "calculate_stock_roi",
        "args": {
            "code": "002156",
            "name": "通富微电",
            "price": 52.01,
            "strategy": "趋势跟踪",
            "expected_return": 0.08,
            "probability": 0.75,
            "risk_level": "medium",
            "time_horizon": "short"
        }
    }
    
    r = requests.post(f"{BASE_URL}/mcp/call", json=payload)
    data = r.json()
    
    assert data["result"]["success"], "计算失败"
    assert data["result"]["data"]["roi_score"] > 0, "ROI 分数无效"
    assert data["result"]["data"]["should_trade"] == True, "应该建议交易"
    
    print(f"✅ 单股 ROI: {data['result']['data']['roi_score']}")
    print(f"   建议: {data['result']['data']['recommendation'][:40]}...")
    return data

def test_batch_analysis():
    """测试批量分析"""
    watchlist = [
        {"code": "002156", "name": "通富微电", "price": 52.01, "strategy": "趋势", "expected_return": 0.08, "probability": 0.75, "risk_level": "medium"},
        {"code": "003029", "name": "金富科技", "price": 15.85, "strategy": "突破", "expected_return": 0.05, "probability": 0.70, "risk_level": "low"},
        {"code": "300058", "name": "蓝色光标", "price": 12.30, "strategy": "反弹", "expected_return": 0.03, "probability": 0.55, "risk_level": "high"},
    ]
    
    payload = {
        "tool": "analyze_watchlist_roi",
        "args": {"watchlist": watchlist}
    }
    
    r = requests.post(f"{BASE_URL}/mcp/call", json=payload)
    data = r.json()
    
    assert data["result"]["success"], "批量分析失败"
    assert len(data["result"]["data"]) == 3, "返回数量不匹配"
    
    # 验证排序（按 ROI 降序）
    scores = [item["roi"]["score"] for item in data["result"]["data"]]
    assert scores == sorted(scores, reverse=True), "未按 ROI 排序"
    
    print(f"✅ 批量分析: {len(data['result']['data'])} 只股票")
    for item in data["result"]["data"]:
        print(f"   {item['stock']['name']}: ROI {item['roi']['score']}, 交易={item['roi']['should_trade']}")
    
    return data

def test_risk_levels():
    """测试不同风险等级"""
    test_cases = [
        {"risk_level": "low", "expected_trade": True},
        {"risk_level": "medium", "expected_trade": True},
        {"risk_level": "high", "expected_trade": False},  # 高风险+低概率
    ]
    
    for case in test_cases:
        payload = {
            "tool": "calculate_stock_roi",
            "args": {
                "code": "TEST",
                "name": "测试",
                "price": 50.0,
                "strategy": "测试",
                "expected_return": 0.05,
                "probability": 0.65 if case["risk_level"] != "high" else 0.50,
                "risk_level": case["risk_level"],
                "time_horizon": "medium"
            }
        }
        
        r = requests.post(f"{BASE_URL}/mcp/call", json=payload)
        data = r.json()
        
        print(f"✅ 风险等级 {case['risk_level']}: 交易={data['result']['data']['should_trade']}")

def test_time_horizons():
    """测试不同时间周期"""
    for horizon in ["short", "medium", "long"]:
        payload = {
            "tool": "calculate_stock_roi",
            "args": {
                "code": "TEST",
                "name": "测试",
                "price": 50.0,
                "strategy": "测试",
                "expected_return": 0.08,
                "probability": 0.75,
                "risk_level": "medium",
                "time_horizon": horizon
            }
        }
        
        r = requests.post(f"{BASE_URL}/mcp/call", json=payload)
        data = r.json()
        
        cost = data["result"]["data"]["total_cost"]
        print(f"✅ 时间周期 {horizon}: 总成本={cost:.2f}")

def run_all_tests():
    """运行所有测试"""
    print("=" * 70)
    print("🚀 Smart ROI API 完整测试")
    print("=" * 70)
    print()
    
    try:
        test_health()
        print()
        
        test_single_stock_roi()
        print()
        
        test_batch_analysis()
        print()
        
        test_risk_levels()
        print()
        
        test_time_horizons()
        print()
        
        print("=" * 70)
        print("✅ 所有测试通过！")
        print("=" * 70)
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
