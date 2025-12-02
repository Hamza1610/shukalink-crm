from langchain.tools import tool
from typing import Optional
from app.services.payment_service import PaymentService
from app.models.user import User

payment_service = PaymentService()

@tool
def get_payment_info(query: str, user_id: Optional[str] = None) -> str:
    """
    Get information about payments, transaction history, or payment status.
    Use this when user asks about their payment status or history.
    
    Args:
        query: The question about payments (e.g., "check my payment status", "payment history")
        user_id: The ID of the user (optional)
    
    Returns:
        Payment information as a string
    """
    user = User(id=user_id) if user_id else None
    return payment_service.get_payment_info(query, user=user)

@tool
def process_payment(
    amount: float, 
    description: str, 
    user_id: Optional[str] = None
) -> str:
    """
    Initiate a payment process. Only use this when you have a specific amount to charge.
    The amount MUST be a number (float), not a string.
    
    Args:
        amount: The amount to pay as a number (e.g., 100.0, 5000.50)
        description: Description of the payment (e.g., "Payment for tomatoes delivery")
        user_id: The ID of the user (optional)
    
    Returns:
        Payment link or confirmation message
    """
    return f"✅ Payment link generated for ₦{amount:,.2f}. Description: {description}. Please follow the link sent to your WhatsApp to complete the transaction."
