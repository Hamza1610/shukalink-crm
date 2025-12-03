from langchain.tools import tool
from typing import Optional
from app.services.advisory_service import AdvisoryService

advisory_service = AdvisoryService()

@tool
def get_crop_advice(query: str, user_id: Optional[str] = None) -> str:
    """
    Get expert farming advice for crops, pests, diseases, and soil management.
    Use this tool when the user asks specific questions about farming practices.
    
    Args:
        query: The specific farming question (e.g., "how to treat maize stalk borer", "best fertilizer for yams")
        user_id: The ID of the user requesting advice (optional)
    
    Returns:
        Expert farming advice as a string
    """
    # Don't create User objects - just pass user_id to service
    return advisory_service.get_crop_advice(query, user=None)
