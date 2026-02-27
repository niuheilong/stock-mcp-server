# Smart ROI MCP Tool 集成
# 添加到 stock_mcp_server_enhanced.py

# 在 imports 部分添加
from smart_roi_calculator import get_roi_tool, calculate_roi, analyze_batch

# 在 tools 列表中添加
SMART_ROI_TOOLS = [
    {
        "name": "calculate_stock_roi",
        "description": "计算股票投资的Smart ROI评分，借鉴赏金猎人ROI系统",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "股票代码"},
                "name": {"type": "string", "description": "股票名称"},
                "price": {"type": "number", "description": "当前价格"},
                "strategy": {"type": "string", "description": "投资策略"},
                "expected_return": {"type": "number", "description": "预期收益率(如0.05表示5%)"},
                "probability": {"type": "number", "description": "成功概率(0-1)"},
                "risk_level": {"type": "string", "enum": ["low", "medium", "high"], "description": "风险等级"},
                "time_horizon": {"type": "string", "enum": ["short", "medium", "long"], "description": "投资周期"}
            },
            "required": ["code", "name", "price", "strategy", "expected_return", "probability", "risk_level"]
        }
    },
    {
        "name": "analyze_watchlist_roi",
        "description": "批量分析关注列表的ROI，返回按评分排序的投资建议",
        "inputSchema": {
            "type": "object",
            "properties": {
                "watchlist": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string"},
                            "name": {"type": "string"},
                            "price": {"type": "number"},
                            "strategy": {"type": "string"},
                            "expected_return": {"type": "number"},
                            "probability": {"type": "number"},
                            "risk_level": {"type": "string", "enum": ["low", "medium", "high"]},
                            "time_horizon": {"type": "string", "enum": ["short", "medium", "long"]}
                        }
                    }
                }
            },
            "required": ["watchlist"]
        }
    }
]

# 在 mcp_call 路由中添加处理逻辑
"""
if tool_name == "calculate_stock_roi":
    result = calculate_roi(**args)
    return jsonify(result)

if tool_name == "analyze_watchlist_roi":
    result = analyze_batch(args["watchlist"])
    return jsonify(result)
"""

# 使用示例
USAGE_EXAMPLE = """
# 计算单只股票 ROI
curl -X POST http://localhost:5001/mcp/call \
  -H "Content-Type: application/json" \
  -d '{
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
  }'

# 批量分析关注列表
curl -X POST http://localhost:5001/mcp/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "analyze_watchlist_roi",
    "args": {
      "watchlist": [
        {"code": "002156", "name": "通富微电", "price": 52.01, "strategy": "趋势", "expected_return": 0.08, "probability": 0.75, "risk_level": "medium"},
        {"code": "003029", "name": "金富科技", "price": 15.85, "strategy": "突破", "expected_return": 0.05, "probability": 0.70, "risk_level": "low"}
      ]
    }
  }'
"""
