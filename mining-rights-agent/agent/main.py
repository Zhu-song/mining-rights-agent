import asyncio
import sys
from .workflow import app

async def run_agent(query: str) -> str:
    initial_state = {
        "messages": [],
        "user_query": query,
        "company_name": "",
        "mineral_type": "",
        "country": "",
        "news_data": None,
        "reserves_data": None,
        "price_data": None,
        "risk_factors": [],
        "final_report": None,
        "steps_completed": []
    }
    
    result = await app.ainvoke(initial_state)
    
    return result.get("final_report", "无法生成简报")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "给我生成一份关于 Pilbara 锂矿的今日简报"
    
    print(f"正在处理查询: {query}")
    print("=" * 60)
    
    report = asyncio.run(run_agent(query))
    
    print("\n生成的简报:")
    print("=" * 60)
    print(report)
