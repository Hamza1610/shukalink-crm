from typing import TypedDict, Annotated, List, Union, Dict, Any
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    next: str
    user_id: str
    user_info: Dict[str, Any]
