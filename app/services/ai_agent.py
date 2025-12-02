"""
AI Agent Service for processing user queries using Multi-Agent System with LangGraph
"""
from typing import Optional
from app.models.user import User


class AIAgent:
    """
    AI Agent that processes user queries and provides intelligent responses using a Multi-Agent System
    """
    
    def __init__(self):
        from app.agents import create_agent_graph
        try:
            self.graph = create_agent_graph()
        except Exception as e:
            print(f"Error initializing agent graph: {e}")
            self.graph = None
    
    def process_query(self, query: str, user: Optional[User] = None):
        """
        Process a user query and return an appropriate response
        """
        if not self.graph:
            return "System is currently initializing or missing configuration (GROQ_API_KEY). Please try again later."

        from langchain_core.messages import HumanMessage
        
        # Prepare initial state
        initial_state = {
            "messages": [HumanMessage(content=query)],
            "next": "",
            "user_id": user.id if user else "anonymous",
            "user_info": {
                "phone": user.phone_number if user else None,
                "name": user.village if user else None,
                "type": user.user_type if user else None
            }
        }
        
        try:
            # Invoke the graph with increased recursion limit
            result = self.graph.invoke(
                initial_state,
                config={"recursion_limit": 50}
            )
            
            # Extract the last message content
            messages = result.get("messages", [])
            if messages:
                last_message = messages[-1]
                # Handle both AIMessage and ToolMessage
                if hasattr(last_message, 'content'):
                    return last_message.content
                else:
                    return str(last_message)
            else:
                return "I processed your request but didn't generate a response."
                
        except Exception as e:
            print(f"Error processing query with agent graph: {e}")
            import traceback
            traceback.print_exc()
            return f"I encountered an error while processing your request. Please try again or rephrase your question."