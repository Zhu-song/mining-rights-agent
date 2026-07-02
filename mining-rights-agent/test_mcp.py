import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

async def test_news_server():
    client = MultiServerMCPClient({
        "news": {
            "command": "python",
            "args": ["servers/news_server.py"],
            "transport": "stdio"
        }
    })
    
    async with client.session("news") as session:
        tools = await load_mcp_tools(session)
        print("Available tools:", [t.name for t in tools])
        
        news_tool = [t for t in tools if t.name == "fetch_mining_news"][0]
        result = await news_tool.ainvoke({"company": "Pilbara Minerals", "days": 7})
        print("\nNews tool result type:", type(result))
        print("News tool result:", result)
        
        policy_tool = [t for t in tools if t.name == "search_policy_updates"][0]
        policy_result = await policy_tool.ainvoke({"country": "Australia", "mineral": "lithium"})
        print("\nPolicy tool result type:", type(policy_result))
        print("Policy tool result:", policy_result)

async def test_reserves_server():
    client = MultiServerMCPClient({
        "reserves": {
            "command": "python",
            "args": ["servers/reserves_server.py"],
            "transport": "stdio"
        }
    })
    
    async with client.session("reserves") as session:
        tools = await load_mcp_tools(session)
        print("\nReserves tools:", [t.name for t in tools])
        
        reserves_tool = [t for t in tools if t.name == "get_reserves_data"][0]
        result = await reserves_tool.ainvoke({"company": "Pilbara Minerals", "mineral": "lithium"})
        print("\nReserves tool result type:", type(result))
        print("Reserves tool result:", result)

async def test_price_server():
    client = MultiServerMCPClient({
        "price": {
            "command": "python",
            "args": ["servers/price_server.py"],
            "transport": "stdio"
        }
    })
    
    async with client.session("price") as session:
        tools = await load_mcp_tools(session)
        print("\nPrice tools:", [t.name for t in tools])
        
        price_tool = [t for t in tools if t.name == "get_price_trend"][0]
        result = await price_tool.ainvoke({"mineral": "lithium", "days": 30})
        print("\nPrice tool result type:", type(result))
        print("Price tool result:", result)

if __name__ == "__main__":
    asyncio.run(test_news_server())
    asyncio.run(test_reserves_server())
    asyncio.run(test_price_server())
