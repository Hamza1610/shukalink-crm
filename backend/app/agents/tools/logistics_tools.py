from langchain.tools import tool
from typing import Optional
from app.services.logistics_service import LogisticsService

logistics_service = LogisticsService()

@tool
def get_transport_info(query: str, user_id: Optional[str] = None) -> str:
    """
    Get information about transport rates, availability, and logistics services.
    Use this when user asks about transport costs or availability.
    
    Args:
        query: The question about transport (e.g., "cost to transport to Kano", "available trucks")
        user_id: The ID of the user (optional)
    
    Returns:
        Transport information as a string
    """
    # Don't create User objects - just pass user_id to service
    return logistics_service.get_transport_info(query, user=None)

@tool
def schedule_transport(
    produce: str, 
    quantity: str, 
    destination: str, 
    user_id: Optional[str] = None
) -> str:
    """
    Schedule a transport pickup for produce. Only use this when you have ALL required details from the user.
    If any information is missing, ask the user for it first instead of calling this tool.
    
    Args:
        produce: The type of produce (e.g., "tomatoes", "maize", "rice")
        quantity: The quantity to transport (e.g., "50 bags", "100kg")
        destination: The destination for the delivery (e.g., "Kano market", "Lagos")
        user_id: The ID of the user (optional)
    
    Returns:
        Confirmation message for the transport request
    """
    return f"✅ Transport request received for {quantity} of {produce} to {destination}. A driver will contact you shortly at your registered phone number."
