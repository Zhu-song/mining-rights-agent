import json
from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("NewsServer", json_response=True)

MINING_NEWS_DATA = {
    "Pilbara Minerals": [
        {
            "title": "Pilbara Minerals Announces Record Quarterly Lithium Production",
            "summary": "Pilbara Minerals Limited (ASX: PLS) has reported record quarterly lithium concentrate production of 188,434 tonnes during the March 2026 quarter, representing a 15% increase from the previous quarter.",
            "source": "https://www.pilbaraminerals.com.au/news",
            "date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
            "category": "production"
        },
        {
            "title": "Pilbara Signs New Supply Agreement with Chinese Battery Maker",
            "summary": "The company has entered into a five-year lithium concentrate supply agreement with a major Chinese battery manufacturer, securing long-term off-take for its future production.",
            "source": "https://www.pilbaraminerals.com.au/news",
            "date": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
            "category": "agreement"
        },
        {
            "title": "Pilbara Minerals Expands Pilgangoora Operations",
            "summary": "Expansion works at the Pilgangoora project are progressing well, with first ore expected from the new production line in Q3 2026.",
            "source": "https://www.pilbaraminerals.com.au/news",
            "date": (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d"),
            "category": "expansion"
        }
    ],
    "Newmont": [
        {
            "title": "Newmont Reports Strong Q1 2026 Gold Production",
            "summary": "Newmont Corporation (NYSE: NEM) produced 1.4 million ounces of gold in Q1 2026, meeting its guidance range of 1.3-1.5 million ounces.",
            "source": "https://www.newmont.com/news",
            "date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
            "category": "production"
        },
        {
            "title": "Newmont Acquires Additional Stake in Peru Copper Project",
            "summary": "Newmont has acquired an additional 10% stake in the Yanacocha copper project in Peru, increasing its ownership to 60%.",
            "source": "https://www.newmont.com/news",
            "date": (datetime.now() - timedelta(days=8)).strftime("%Y-%m-%d"),
            "category": "acquisition"
        }
    ],
    "Barrick Gold": [
        {
            "title": "Barrick Gold Achieves Production Milestone at Carlin",
            "summary": "Barrick Gold Corporation (NYSE: GOLD) has achieved a significant production milestone at its Carlin operations in Nevada.",
            "source": "https://www.barrick.com/news",
            "date": (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d"),
            "category": "production"
        }
    ]
}

POLICY_DATA = {
    "Australia": {
        "lithium": [
            {
                "title": "Australia Introduces New Lithium Export Regulations",
                "summary": "The Australian government has introduced new regulations aimed at ensuring sustainable lithium exports while protecting domestic supply chains.",
                "source": "https://www.industry.gov.au",
                "date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
            },
            {
                "title": "Federal Funding for Lithium Processing Infrastructure",
                "summary": "The Australian federal government has announced $500 million in funding for lithium processing infrastructure to support the domestic battery manufacturing industry.",
                "source": "https://www.industry.gov.au",
                "date": (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d")
            }
        ],
        "gold": [
            {
                "title": "Australia Updates Mining Taxation Framework",
                "summary": "The government has updated the mining taxation framework to ensure larger mining companies pay their fair share of taxes.",
                "source": "https://www.treasury.gov.au",
                "date": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            }
        ]
    },
    "Canada": {
        "lithium": [
            {
                "title": "Canada Approves New Lithium Mining Projects",
                "summary": "The Canadian government has approved several new lithium mining projects in Quebec, aiming to become a major player in the global lithium supply chain.",
                "source": "https://www.nrcan.gc.ca",
                "date": (datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d")
            }
        ]
    }
}


@mcp.tool()
def fetch_mining_news(company: str, days: int = 7) -> str:
    """
    获取指定矿业公司的最新新闻摘要
    
    Args:
        company: 矿业公司名称，如 "Pilbara Minerals", "Newmont", "Barrick Gold"
        days: 过去多少天的新闻，默认7天
        
    Returns:
        JSON格式的新闻列表，包含标题、摘要、来源、日期等信息
    """
    company_news = MINING_NEWS_DATA.get(company, MINING_NEWS_DATA.get("Pilbara Minerals", []))
    
    cutoff_date = datetime.now() - timedelta(days=days)
    filtered_news = [
        news for news in company_news 
        if datetime.strptime(news["date"], "%Y-%m-%d") >= cutoff_date
    ]
    
    return json.dumps({
        "company": company,
        "news_count": len(filtered_news),
        "news": filtered_news
    }, ensure_ascii=False, indent=2)


@mcp.tool()
def search_policy_updates(country: str, mineral: str) -> str:
    """
    搜索指定国家和矿种的政策更新
    
    Args:
        country: 国家名称，如 "Australia", "Canada", "China"
        mineral: 矿种名称，如 "lithium", "gold", "copper"
        
    Returns:
        JSON格式的政策更新列表，包含标题、摘要、来源、日期等信息
    """
    country_policies = POLICY_DATA.get(country, {})
    mineral_policies = country_policies.get(mineral, [])
    
    return json.dumps({
        "country": country,
        "mineral": mineral,
        "policy_count": len(mineral_policies),
        "policies": mineral_policies
    }, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    mcp.run(transport="stdio")
