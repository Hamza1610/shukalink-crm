from fastapi import APIRouter, Request, Depends, HTTPException, status
from app.db.session import SessionLocal
from app.crud.crud_transaction import crud_transaction
from app.services.payment_service import PaymentService
from app.core.config import settings
import hashlib
import hmac
import json

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/verify")
async def verify_payment_webhook(request: Request):
    """
    Verify payment completion (called by Paystack webhook)
    """
    # Get the raw body for signature verification
    body = await request.body()
    signature = request.headers.get("x-paystack-signature")
    
    if not signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No signature provided"
        )
    
    # Verify the signature (in production)
    # expected_signature = hmac.new(
    #     settings.PAYSTACK_WEBHOOK_SECRET.encode('utf-8'),
    #     body,
    #     hashlib.sha512
    # ).hexdigest()
    # 
    # if not hmac.compare_digest(signature, expected_signature):
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Invalid signature"
    #     )
    
    # Parse the request body
    payload = await request.json()
    
    # Process the payment event
    event = payload.get("event")
    data = payload.get("data", {})
    
    if event == "charge.success":
        reference = data.get("reference")
        
        # Update transaction status in database
        db = next(get_db())
        try:
            # Find transaction by reference (which would be the transaction ID)
            transaction = crud_transaction.get_by_reference(db, reference)
            
            if not transaction:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Transaction with reference {reference} not found"
                )
            
            # Update transaction status to completed
            transaction_data = {
                "status": "completed",
                "payment_reference": reference,
                "payment_amount": data.get("amount", 0) / 100,  # Paystack sends amount in kobo
                "payment_method": "paystack"
            }
            
            updated_transaction = crud_transaction.update(
                db, 
                db_obj=transaction, 
                obj_in=transaction_data
            )
            
            return {
                "status": "success",
                "message": "Payment verified successfully"
            }
        finally:
            db.close()
    
    elif event == "charge.failed":
        reference = data.get("reference")
        return {
            "status": "success",
            "message": f"Payment failed for reference {reference}"
        }
    
    else:
        return {
            "status": "success",
            "message": "Event processed"
        }

@router.post("/initialize")
async def initialize_payment(transaction_id: str, db=Depends(get_db)):
    """
    Initialize a payment for a transaction
    """
    transaction = crud_transaction.get(db, id=transaction_id)
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    # Initialize payment with Paystack
    payment_service = PaymentService()
    payment_data = {
        "amount": int(transaction.total_amount * 100),  # Convert to kobo
        "email": f"user_{transaction_id}@agrilink.com",  # In real app, use actual user email
        "reference": transaction_id,
        "callback_url": f"{settings.API_V1_STR}/payments/verify"
    }
    
    response = payment_service.initialize_payment(payment_data)
    
    return response