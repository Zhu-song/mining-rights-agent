from typing import TypedDict, Annotated, List, Optional
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage

class ReportState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    user_query: str
    company_name: str
    mineral_type: str
    country: str
    news_data: Optional[str]
    reserves_data: Optional[str]
    price_data: Optional[str]
    risk_factors: List[str]
    final_report: Optional[str]
    steps_completed: List[str]
