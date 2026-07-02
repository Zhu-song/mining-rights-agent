import json
import os
from datetime import datetime

from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from .state import ReportState

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
USE_LOCAL_MODE = not ANTHROPIC_API_KEY or ANTHROPIC_API_KEY == "test-key-for-development"

MCP_SERVERS = {
    "news": {"command": "python", "args": ["servers/news_server.py"], "transport": "stdio"},
    "reserves": {"command": "python", "args": ["servers/reserves_server.py"], "transport": "stdio"},
    "price": {"command": "python", "args": ["servers/price_server.py"], "transport": "stdio"}
}

COMPANY_MAPPING = {
    "pilbara": "Pilbara Minerals",
    "pilbara minerals": "Pilbara Minerals",
    "newmont": "Newmont",
    "barrick": "Barrick Gold",
    "barrick gold": "Barrick Gold"
}

MINERAL_MAPPING = {
    "锂": "lithium",
    "锂矿": "lithium",
    "gold": "gold",
    "金": "gold",
    "copper": "copper",
    "铜": "copper",
    "iron": "iron_ore",
    "铁矿石": "iron_ore"
}

COUNTRY_MAPPING = {
    "australia": "Australia",
    "澳大利亚": "Australia",
    "canada": "Canada",
    "加拿大": "Canada",
    "china": "China",
    "中国": "China"
}


def extract_mcp_text(result):
    if isinstance(result, list) and len(result) > 0:
        for item in result:
            if isinstance(item, dict) and "text" in item:
                return item["text"]
    return str(result)


def parse_query_local(query):
    query_lower = query.lower()
    company = "Pilbara Minerals"
    for key, value in COMPANY_MAPPING.items():
        if key in query_lower:
            company = value
            break
    mineral = "lithium"
    for key, value in MINERAL_MAPPING.items():
        if key in query_lower:
            mineral = value
            break
    country = "Australia"
    for key, value in COUNTRY_MAPPING.items():
        if key in query_lower:
            country = value
            break
    return {"company_name": company, "mineral_type": mineral, "country": country}


async def parse_query_node(state):
    user_query = state["user_query"]
    if USE_LOCAL_MODE:
        result = parse_query_local(user_query)
    else:
        from langchain_anthropic import ChatAnthropic
        MODEL = ChatAnthropic(model="claude-3-5-sonnet-20241022", api_key=ANTHROPIC_API_KEY, temperature=0.7)
        prompt = "分析用户查询，提取信息：company_name, mineral_type, country。用户查询: %s" % user_query
        response = await MODEL.ainvoke([HumanMessage(content=prompt)])
        try:
            result = json.loads(response.content)
        except:
            result = parse_query_local(user_query)
    return {
        **state,
        "company_name": result.get("company_name", "Pilbara Minerals"),
        "mineral_type": result.get("mineral_type", "lithium"),
        "country": result.get("country", "Australia"),
        "steps_completed": state["steps_completed"] + ["parse_query"]
    }


async def fetch_news_node(state):
    company_name = state["company_name"]
    country = state["country"]
    mineral_type = state["mineral_type"]
    client = MultiServerMCPClient({"news": MCP_SERVERS["news"]})
    async with client.session("news") as session:
        tools = await load_mcp_tools(session)
        news_tool = None
        policy_tool = None
        for tool in tools:
            if tool.name == "fetch_mining_news":
                news_tool = tool
            elif tool.name == "search_policy_updates":
                policy_tool = tool
        news_result = ""
        if news_tool:
            raw_result = await news_tool.ainvoke({"company": company_name, "days": 7})
            news_result = extract_mcp_text(raw_result)
        policy_result = ""
        if policy_tool:
            raw_result = await policy_tool.ainvoke({"country": country, "mineral": mineral_type})
            policy_result = extract_mcp_text(raw_result)
    return {
        **state,
        "news_data": json.dumps({"company_news": news_result, "policy_updates": policy_result}, ensure_ascii=False),
        "steps_completed": state["steps_completed"] + ["fetch_news"]
    }


async def fetch_reserves_node(state):
    company_name = state["company_name"]
    mineral_type = state["mineral_type"]
    client = MultiServerMCPClient({"reserves": MCP_SERVERS["reserves"]})
    async with client.session("reserves") as session:
        tools = await load_mcp_tools(session)
        reserves_tool = None
        report_tool = None
        for tool in tools:
            if tool.name == "get_reserves_data":
                reserves_tool = tool
            elif tool.name == "get_resource_report":
                report_tool = tool
        reserves_result = ""
        if reserves_tool:
            raw_result = await reserves_tool.ainvoke({"company": company_name, "mineral": mineral_type})
            reserves_result = extract_mcp_text(raw_result)
        report_result = ""
        if report_tool:
            raw_result = await report_tool.ainvoke({"company": company_name})
            report_result = extract_mcp_text(raw_result)
    return {
        **state,
        "reserves_data": json.dumps({"reserves": reserves_result, "resource_report": report_result}, ensure_ascii=False),
        "steps_completed": state["steps_completed"] + ["fetch_reserves"]
    }


async def fetch_price_node(state):
    mineral_type = state["mineral_type"]
    client = MultiServerMCPClient({"price": MCP_SERVERS["price"]})
    async with client.session("price") as session:
        tools = await load_mcp_tools(session)
        price_tool = None
        for tool in tools:
            if tool.name == "get_price_trend":
                price_tool = tool
        price_result = ""
        if price_tool:
            raw_result = await price_tool.ainvoke({"mineral": mineral_type, "days": 30})
            price_result = extract_mcp_text(raw_result)
    return {
        **state,
        "price_data": price_result,
        "steps_completed": state["steps_completed"] + ["fetch_price"]
    }


async def analyze_risk_node(state):
    mineral_type = state["mineral_type"]
    country = state["country"]
    if USE_LOCAL_MODE:
        risk_factors = [
            mineral_type + "价格波动风险",
            country + "政策变化风险",
            "供应链中断风险",
            "汇率波动风险",
            "地缘政治风险"
        ]
    else:
        from langchain_anthropic import ChatAnthropic
        MODEL = ChatAnthropic(model="claude-3-5-sonnet-20241022", api_key=ANTHROPIC_API_KEY, temperature=0.7)
        prompt = "分析矿业投资风险因素，矿种: %s, 国家: %s" % (mineral_type, country)
        response = await MODEL.ainvoke([HumanMessage(content=prompt)])
        try:
            result = json.loads(response.content)
            risk_factors = result.get("risk_factors", [])
        except:
            risk_factors = [mineral_type + "价格波动风险", country + "政策变化风险"]
    return {
        **state,
        "risk_factors": risk_factors,
        "steps_completed": state["steps_completed"] + ["analyze_risk"]
    }


async def generate_report_node(state):
    company_name = state["company_name"]
    mineral_type = state["mineral_type"]
    news_data = state["news_data"]
    reserves_data = state["reserves_data"]
    price_data = state["price_data"]
    risk_factors = state["risk_factors"]

    if USE_LOCAL_MODE:
        news_items = []
        policy_items = []
        reserves_info = {}
        report_info = {}
        price_info = {}

        try:
            news_json = json.loads(news_data)
            if news_json.get("company_news"):
                company_news = json.loads(news_json["company_news"])
                news_items = company_news.get("news", [])
            if news_json.get("policy_updates"):
                policy_updates = json.loads(news_json["policy_updates"])
                policy_items = policy_updates.get("policies", [])
        except:
            pass

        try:
            reserves_json = json.loads(reserves_data)
            if reserves_json.get("reserves"):
                reserves_info = json.loads(reserves_json["reserves"])
            if reserves_json.get("resource_report"):
                report_info = json.loads(reserves_json["resource_report"])
        except:
            pass

        try:
            if price_data:
                price_info = json.loads(price_data)
        except:
            pass

        news_section = "## News Summary\n"
        if news_items:
            for news in news_items[:3]:
                title = news.get("title", "")
                source = news.get("source", "")
                summary = news.get("summary", "")[:100]
                news_section += "- [%s](%s) - %s...\n" % (title, source, summary)
        elif policy_items:
            for policy in policy_items[:2]:
                title = policy.get("title", "")
                source = policy.get("source", "")
                summary = policy.get("summary", "")[:100]
                news_section += "- [%s](%s) - %s...\n" % (title, source, summary)
        else:
            news_section += "- No recent news\n"

        reserves_section = "## Reserves Data\n"
        if reserves_info:
            reserves = reserves_info.get("reserves", {})
            total = reserves.get("total_reserves", {})
            if total:
                ore_mt = total.get("ore_mt", "N/A")
                reserves_section += "- Ore: %s Mt\n" % ore_mt
                if "grade_pct" in total:
                    grade = total.get("grade_pct", "N/A")
                    reserves_section += "- Grade: %s %%\n" % grade
                elif "grade_gpt" in total:
                    grade = total.get("grade_gpt", "N/A")
                    reserves_section += "- Grade: %s g/t\n" % grade
                metal = total.get("metal_t", total.get("metal_oz", "N/A"))
                unit = total.get("unit", "")
                reserves_section += "- Metal: %s %s\n" % (metal, unit)
        elif report_info:
            report = report_info.get("report", {})
            report_title = report.get("report_title", "N/A")
            report_date = report.get("latest_report_date", "N/A")
            reserves_section += "- Latest Report: %s\n" % report_title
            reserves_section += "- Report Date: %s\n" % report_date
            if report.get("highlights"):
                highlights = "; ".join(report["highlights"][:2])
                reserves_section += "- Highlights: %s\n" % highlights
        else:
            reserves_section += "- No reserves data\n"

        price_section = "## Price Trend\n"
        if price_info:
            current_price = price_info.get("current_price", "N/A")
            unit = price_info.get("unit", "")
            trend = price_info.get("trend", "N/A")
            change_pct = price_info.get("overall_change_pct", "N/A")
            price_section += "- Current Price: %s %s\n" % (current_price, unit)
            price_section += "- Trend: %s\n" % trend
            price_section += "- 30-day Change: %s%%\n" % change_pct
        else:
            price_section += "- No price data\n"

        risk_section = "## Risk Factors\n"
        for i, risk in enumerate(risk_factors[:5], 1):
            risk_section += "%d. %s\n" % (i, risk)

        sources_section = "## Sources\n"
        if news_items:
            seen_sources = set()
            for news in news_items:
                source = news.get("source", "")
                if source and source not in seen_sources:
                    sources_section += "- [Source](%s)\n" % source
                    seen_sources.add(source)
        elif report_info:
            report = report_info.get("report", {})
            source = report.get("source", "")
            if source:
                sources_section += "- [Company Report](%s)\n" % source
        else:
            sources_section += "- [Mining Data Platform](https://example.com)\n"

        final_report = (
            "# %s Daily Brief\n\n"
            "%s"
            "%s"
            "%s"
            "%s"
            "%s"
            "---\n"
            "*Generated at: %s*\n"
        ) % (company_name, news_section, reserves_section, price_section, risk_section, sources_section, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    else:
        from langchain_anthropic import ChatAnthropic
        MODEL = ChatAnthropic(model="claude-3-5-sonnet-20241022", api_key=ANTHROPIC_API_KEY, temperature=0.7)
        prompt = "请为矿业公司 %s 生成简报，矿种: %s" % (company_name, mineral_type)
        response = await MODEL.ainvoke([HumanMessage(content=prompt)])
        final_report = response.content

    return {
        **state,
        "final_report": final_report,
        "steps_completed": state["steps_completed"] + ["generate_report"]
    }


def build_workflow():
    workflow = StateGraph(ReportState)
    workflow.add_node("parse_query", parse_query_node)
    workflow.add_node("fetch_news", fetch_news_node)
    workflow.add_node("fetch_reserves", fetch_reserves_node)
    workflow.add_node("fetch_price", fetch_price_node)
    workflow.add_node("analyze_risk", analyze_risk_node)
    workflow.add_node("generate_report", generate_report_node)
    workflow.add_edge("parse_query", "fetch_news")
    workflow.add_edge("fetch_news", "fetch_reserves")
    workflow.add_edge("fetch_reserves", "fetch_price")
    workflow.add_edge("fetch_price", "analyze_risk")
    workflow.add_edge("analyze_risk", "generate_report")
    workflow.add_edge("generate_report", END)
    workflow.set_entry_point("parse_query")
    return workflow


workflow = build_workflow()
app = workflow.compile()
