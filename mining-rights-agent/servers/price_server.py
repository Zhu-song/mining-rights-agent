import json
from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("PriceServer", json_response=True)

MINERAL_PRICES = {
    "lithium": {
        "unit": "USD/tonne",
        "current_price": 78500,
        "price_history": []
    },
    "gold": {
        "unit": "USD/ounce",
        "current_price": 2345.50,
        "price_history": []
    },
    "copper": {
        "unit": "USD/tonne",
        "current_price": 8230,
        "price_history": []
    },
    "iron_ore": {
        "unit": "USD/tonne",
        "current_price": 128.50,
        "price_history": []
    }
}

BASE_DATE = datetime.now()
for mineral, data in MINERAL_PRICES.items():
    prices = []
    if mineral == "lithium":
        base_price = 82000
        for i in range(30):
            date = (BASE_DATE - timedelta(days=i)).strftime("%Y-%m-%d")
            volatility = (i % 7) * 500 - 1500
            price = base_price - (i * 120) + volatility
            prices.append({
                "date": date,
                "price": round(price, 2),
                "change": round((price - base_price) / base_price * 100, 2)
            })
    elif mineral == "gold":
        base_price = 2280
        for i in range(30):
            date = (BASE_DATE - timedelta(days=i)).strftime("%Y-%m-%d")
            volatility = (i % 5) * 15 - 35
            price = base_price + (i * 2.2) + volatility
            prices.append({
                "date": date,
                "price": round(price, 2),
                "change": round((price - base_price) / base_price * 100, 2)
            })
    elif mineral == "copper":
        base_price = 7950
        for i in range(30):
            date = (BASE_DATE - timedelta(days=i)).strftime("%Y-%m-%d")
            volatility = (i % 6) * 80 - 200
            price = base_price + (i * 9) + volatility
            prices.append({
                "date": date,
                "price": round(price, 2),
                "change": round((price - base_price) / base_price * 100, 2)
            })
    elif mineral == "iron_ore":
        base_price = 135
        for i in range(30):
            date = (BASE_DATE - timedelta(days=i)).strftime("%Y-%m-%d")
            volatility = (i % 7) * 3 - 10
            price = base_price - (i * 0.25) + volatility
            prices.append({
                "date": date,
                "price": round(price, 2),
                "change": round((price - base_price) / base_price * 100, 2)
            })
    prices.reverse()
    data["price_history"] = prices
    if prices:
        data["current_price"] = prices[-1]["price"]


@mcp.tool()
def get_price_trend(mineral: str, days: int = 30) -> str:
    """
    获取矿产品价格走势
    
    Args:
        mineral: 矿种名称，如 "lithium", "gold", "copper", "iron_ore"
        days: 获取过去多少天的价格数据，默认30天
        
    Returns:
        JSON格式的价格走势数据，包含日期、价格、涨跌幅等信息
    """
    mineral_data = MINERAL_PRICES.get(mineral, None)
    
    if not mineral_data:
        return json.dumps({
            "error": f"No price data found for {mineral}",
            "available_minerals": list(MINERAL_PRICES.keys())
        }, ensure_ascii=False, indent=2)
    
    history = mineral_data["price_history"][-days:] if days <= len(mineral_data["price_history"]) else mineral_data["price_history"]
    
    if history:
        first_price = history[0]["price"]
        last_price = history[-1]["price"]
        overall_change = (last_price - first_price) / first_price * 100
        trend = "up" if overall_change > 2 else ("down" if overall_change < -2 else "stable")
    else:
        overall_change = 0
        trend = "stable"
    
    return json.dumps({
        "mineral": mineral,
        "unit": mineral_data["unit"],
        "current_price": mineral_data["current_price"],
        "days": len(history),
        "trend": trend,
        "overall_change_pct": round(overall_change, 2),
        "price_history": history
    }, ensure_ascii=False, indent=2)


@mcp.tool()
def get_price_comparison(minerals: list) -> str:
    """
    对比多种矿产品价格
    
    Args:
        minerals: 矿种名称列表，如 ["lithium", "gold", "copper"]
        
    Returns:
        JSON格式的价格对比数据，包含各矿种当前价格和走势
    """
    comparison = []
    
    for mineral in minerals:
        mineral_data = MINERAL_PRICES.get(mineral, None)
        if mineral_data:
            history = mineral_data["price_history"]
            if history:
                first_price = history[0]["price"]
                last_price = history[-1]["price"]
                change_pct = round((last_price - first_price) / first_price * 100, 2)
                trend = "up" if change_pct > 2 else ("down" if change_pct < -2 else "stable")
            else:
                change_pct = 0
                trend = "stable"
            
            comparison.append({
                "mineral": mineral,
                "unit": mineral_data["unit"],
                "current_price": mineral_data["current_price"],
                "trend": trend,
                "change_pct": change_pct
            })
    
    return json.dumps({
        "minerals": minerals,
        "comparison": comparison,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    mcp.run(transport="stdio")
