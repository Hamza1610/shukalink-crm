from typing import Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.core.config import settings
from app.agents.state import AgentState
from app.agents.agents.advisory import create_advisory_agent
from app.agents.agents.logistics import create_logistics_agent
from app.agents.agents.sales import create_sales_agent
from app.agents.tools.advisory_tools import get_crop_advice
from app.agents.tools.logistics_tools import get_transport_info, schedule_transport
from app.agents.tools.payment_tools import get_payment_info, process_payment
from langgraph.prebuilt import ToolNode

def create_supervisor_node():
    """Create the supervisor node that routes requests"""
    if not settings.GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set")
        
    llm = ChatGroq(
        temperature=0,
        model_name="llama-3.1-8b-instant",
        groq_api_key=settings.GROQ_API_KEY
    )
    
    system_prompt = (
        "You are a supervisor for ShukaLink CRM that routes farmer inquiries.\n"
        "Analyze the user's FIRST message to determine the topic:\n"
        "- Advisory: Farming advice, crops, pests, diseases, soil, fertilizer\n"
        "- Logistics: Transport, delivery, pickup, trucks\n"
        "- Sales: Payments, transactions, buying, selling\n\n"
        "IMPORTANT: Route based on the INITIAL query only. Once routed, the specialist handles the rest.\n"
        "Reply with ONLY ONE WORD: Advisory, Logistics, Sales, or FINISH"
    )
    
    options = ["Advisory", "Logistics", "Sales", "FINISH"]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
        ("system", "What is the topic? Reply with ONE word: {options}"),
    ]).partial(options=str(options))
    
    chain = prompt | llm
    
    def supervisor_node(state: AgentState):
        result = chain.invoke(state)
        content = result.content.strip().upper()
        
        # More robust parsing
        if "ADVISORY" in content:
            return {"next": "Advisory"}
        elif "LOGISTICS" in content:
            return {"next": "Logistics"}
        elif "SALES" in content or "PAYMENT" in content:
            return {"next": "Sales"}
        else:
            # Default to finishing if unclear
            return {"next": "FINISH"}
            
    return supervisor_node

def create_agent_graph():
    """Create the main agent graph with improved flow"""
    
    # Initialize agents
    advisory_agent = create_advisory_agent()
    logistics_agent = create_logistics_agent()
    sales_agent = create_sales_agent()
    
    # Create tool nodes
    advisory_tools = [get_crop_advice]
    logistics_tools = [get_transport_info, schedule_transport]
    sales_tools = [get_payment_info, process_payment]
    
    # Define agent nodes
    def advisory_node(state: AgentState):
        result = advisory_agent.invoke(state)
        return {"messages": [result]}
        
    def logistics_node(state: AgentState):
        result = logistics_agent.invoke(state)
        return {"messages": [result]}
        
    def sales_node(state: AgentState):
        result = sales_agent.invoke(state)
        return {"messages": [result]}
    
    # Build graph
    workflow = StateGraph(AgentState)
    
    workflow.add_node("Supervisor", create_supervisor_node())
    workflow.add_node("Advisory", advisory_node)
    workflow.add_node("Logistics", logistics_node)
    workflow.add_node("Sales", sales_node)
    
    # Add tool nodes
    workflow.add_node("AdvisoryTools", ToolNode(advisory_tools))
    workflow.add_node("LogisticsTools", ToolNode(logistics_tools))
    workflow.add_node("SalesTools", ToolNode(sales_tools))
    
    # Entry point
    workflow.set_entry_point("Supervisor")
    
    # Supervisor routes to specialist agents
    workflow.add_conditional_edges(
        "Supervisor",
        lambda x: x.get("next", "FINISH"),
        {
            "Advisory": "Advisory",
            "Logistics": "Logistics",
            "Sales": "Sales",
            "FINISH": END
        }
    )
    
    # Improved routing logic for agents
    def should_continue(state):
        """Determine if agent should call tools or finish"""
        messages = state['messages']
        last_message = messages[-1]
        
        # If agent wants to call tools, go to tools
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools"
        
        # Otherwise, we're done
        return "end"

    # Advisory agent flow
    workflow.add_conditional_edges(
        "Advisory",
        should_continue,
        {
            "tools": "AdvisoryTools",
            "end": END  # Go directly to end after responding
        }
    )
    workflow.add_edge("AdvisoryTools", "Advisory")  # After tool execution, back to agent
    
    # Logistics agent flow
    workflow.add_conditional_edges(
        "Logistics",
        should_continue,
        {
            "tools": "LogisticsTools",
            "end": END
        }
    )
    workflow.add_edge("LogisticsTools", "Logistics")
    
    # Sales agent flow
    workflow.add_conditional_edges(
        "Sales",
        should_continue,
        {
            "tools": "SalesTools",
            "end": END
        }
    )
    workflow.add_edge("SalesTools", "Sales")
    
    # Compile with increased recursion limit
    return workflow.compile(
        checkpointer=None,
        interrupt_before=None,
        interrupt_after=None,
        debug=False
    )
