import json
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ReservesServer", json_response=True)

RESERVES_DATA = {
    "Pilbara Minerals": {
        "lithium": {
            "indicated_resources": {
                "ore_mt": 279.5,
                "grade_pct": 1.32,
                "metal_t": 3709400,
                "unit": "Li2O"
            },
            "inferred_resources": {
                "ore_mt": 146.2,
                "grade_pct": 1.28,
                "metal_t": 1871360,
                "unit": "Li2O"
            },
            "total_reserves": {
                "ore_mt": 425.7,
                "grade_pct": 1.30,
                "metal_t": 5580760,
                "unit": "Li2O"
            }
        }
    },
    "Newmont": {
        "gold": {
            "indicated_resources": {
                "ore_mt": 1250,
                "grade_gpt": 1.14,
                "metal_oz": 45600000,
                "unit": "Au"
            },
            "inferred_resources": {
                "ore_mt": 890,
                "grade_gpt": 1.02,
                "metal_oz": 29100000,
                "unit": "Au"
            },
            "total_reserves": {
                "ore_mt": 2140,
                "grade_gpt": 1.09,
                "metal_oz": 74700000,
                "unit": "Au"
            }
        },
        "copper": {
            "indicated_resources": {
                "ore_mt": 620,
                "grade_pct": 0.52,
                "metal_t": 3224000,
                "unit": "Cu"
            },
            "inferred_resources": {
                "ore_mt": 380,
                "grade_pct": 0.48,
                "metal_t": 1824000,
                "unit": "Cu"
            },
            "total_reserves": {
                "ore_mt": 1000,
                "grade_pct": 0.51,
                "metal_t": 5048000,
                "unit": "Cu"
            }
        }
    },
    "Barrick Gold": {
        "gold": {
            "indicated_resources": {
                "ore_mt": 980,
                "grade_gpt": 1.25,
                "metal_oz": 39600000,
                "unit": "Au"
            },
            "inferred_resources": {
                "ore_mt": 720,
                "grade_gpt": 1.18,
                "metal_oz": 27300000,
                "unit": "Au"
            },
            "total_reserves": {
                "ore_mt": 1700,
                "grade_gpt": 1.22,
                "metal_oz": 66900000,
                "unit": "Au"
            }
        }
    }
}

RESOURCE_REPORTS = {
    "Pilbara Minerals": {
        "latest_report_date": "2026-03-31",
        "report_title": "March 2026 Quarterly Activities Report",
        "highlights": [
            "Record lithium production of 188,434 tonnes in Q1 2026",
            "Pilgangoora Phase 2 expansion on track for Q3 2026 completion",
            "Strong cash position of $1.2 billion",
            "Five-year supply agreement signed with major Chinese battery maker"
        ],
        "production_guidance": "750,000 - 800,000 tonnes of lithium concentrate for FY2026",
        "source": "https://www.pilbaraminerals.com.au/investors/reports"
    },
    "Newmont": {
        "latest_report_date": "2026-03-31",
        "report_title": "Q1 2026 Earnings Release",
        "highlights": [
            "Gold production of 1.4 million ounces in Q1 2026",
            "All-in sustaining costs of $1,287 per ounce",
            "Free cash flow of $285 million",
            "Dividend maintained at $0.50 per share"
        ],
        "production_guidance": "5.2 - 5.7 million ounces of gold for FY2026",
        "source": "https://www.newmont.com/investors/financial-information"
    },
    "Barrick Gold": {
        "latest_report_date": "2026-03-31",
        "report_title": "Q1 2026 Operational Update",
        "highlights": [
            "Gold production of 1.2 million ounces in Q1 2026",
            "Cost of sales of $1,190 per ounce",
            "Achieved production milestone at Carlin operations",
            "Exploration success at several projects"
        ],
        "production_guidance": "4.8 - 5.2 million ounces of gold for FY2026",
        "source": "https://www.barrick.com/investors"
    }
}


@mcp.tool()
def get_reserves_data(company: str, mineral: str = "lithium") -> str:
    """
    获取矿业公司的储量数据

    Args:
        company: 矿业公司名称，如 "Pilbara Minerals", "Newmont", "Barrick Gold"
        mineral: 矿种名称，如 "lithium", "gold", "copper"，默认lithium

    Returns:
        JSON格式的储量数据，包含矿石量(Mt)、品位、金属量等信息
    """
    company_data = RESERVES_DATA.get(company, {})
    mineral_data = company_data.get(mineral, {})

    if not mineral_data:
        return json.dumps({
            "error": "No reserves data found for %s - %s" % (company, mineral),
            "available_companies": list(RESERVES_DATA.keys()),
            "available_minerals_for_company": list(company_data.keys()) if company_data else []
        }, ensure_ascii=False, indent=2)

    return json.dumps({
        "company": company,
        "mineral": mineral,
        "reserves": mineral_data
    }, ensure_ascii=False, indent=2)


@mcp.tool()
def get_resource_report(company: str) -> str:
    """
    获取公司最新的资源报告摘要

    Args:
        company: 矿业公司名称，如 "Pilbara Minerals", "Newmont", "Barrick Gold"

    Returns:
        JSON格式的资源报告摘要，包含报告日期、标题、亮点、生产指引等信息
    """
    report = RESOURCE_REPORTS.get(company, None)

    if not report:
        return json.dumps({
            "error": "No resource report found for %s" % company,
            "available_companies": list(RESOURCE_REPORTS.keys())
        }, ensure_ascii=False, indent=2)

    return json.dumps({
        "company": company,
        "report": report
    }, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    mcp.run(transport="stdio")
