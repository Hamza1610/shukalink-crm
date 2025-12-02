from fastapi import APIRouter, Request, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.crud import get_transaction, update_transaction, update_transaction_status
from app.crud.crud_transaction import create_payment_record, get_payment_record, update_payment_record
from app.services.payment_service import PaymentService
from app.core.config import settings
from app.schemas.payment import PaymentRecordCreate, PaymentRecordUpdate
from app.models.transaction import PaymentStatus, TransactionStatus
import hashlib
import hmac
import json
import uuid

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/initialize")
async def initialize_payment(transaction_id: str, db: Session = Depends(get_db)):
    """
    Initialize a payment for a transaction
    """
    # 1. Get the transaction
    transaction = get_transaction(db, transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    # 2. Check if already paid
    if transaction.status in [TransactionStatus.PAYMENT_CONFIRMED, TransactionStatus.COMPLETED]:
        return {
            "status": False,
            "message": "Transaction already paid"
        }

    # 3. Generate unique payment reference
    payment_reference = f"pay_{uuid.uuid4().hex[:12]}"
    
    # 4. Initialize with Paystack
    payment_service = PaymentService()
    amount_kobo = int(transaction.total_amount * 100)
    email = f"user_{transaction.buyer_id}@agrilink.com"  # In real app, fetch buyer's email
    
    try:
        paystack_response = payment_service.initialize_transaction(
            email=email,
            amount=amount_kobo,
            reference=payment_reference,
            callback_url=f"{settings.API_V1_STR}/payments/callback",
            metadata={"transaction_id": transaction.id}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
    # 5. Create PaymentRecord in DB
    if paystack_response.get("status"):
        data = paystack_response.get("data", {})
        
        payment_record_in = PaymentRecordCreate(
            transaction_id=transaction.id,
            payment_method="PAYSTACK",
            amount=transaction.total_amount,
            currency="NGN",
            reference=payment_reference,
            status="PENDING",  # Use uppercase to match enum
            paystack_data={"access_code": data.get("access_code")}
        )
        
        create_payment_record(db, payment_record_in, transaction.id)
        
        # Update transaction status
        update_transaction_status(db, transaction.id, TransactionStatus.PAYMENT_INITIATED)
        
        return {
            "status": True,
            "message": "Payment initialized",
            "authorization_url": data.get("authorization_url"),
            "reference": payment_reference,
            "access_code": data.get("access_code")
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to initialize payment with provider"
        )

@router.post("/verify")
async def verify_payment_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Verify payment completion (called by Paystack webhook)
    """
    # 1. Verify Signature
    body = await request.body()
    signature = request.headers.get("x-paystack-signature")
    
    if not signature:
        # Allow missing signature in dev if secret not set, otherwise error
        if settings.PAYSTACK_WEBHOOK_SECRET:
             raise HTTPException(status_code=400, detail="No signature provided")
    
    if settings.PAYSTACK_WEBHOOK_SECRET:
        expected_signature = hmac.new(
            settings.PAYSTACK_WEBHOOK_SECRET.encode('utf-8'),
            body,
            hashlib.sha512
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            raise HTTPException(status_code=400, detail="Invalid signature")
    
    # 2. Parse Payload
    try:
        payload = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
        
    event = payload.get("event")
    data = payload.get("data", {})
    reference = data.get("reference")
    
    if not reference:
        return {"status": "ignored", "message": "No reference found"}

    try:
        # 3. Find PaymentRecord
        from app.models.transaction import PaymentRecord
        payment_record = db.query(PaymentRecord).filter(PaymentRecord.reference == reference).first()
        
        if not payment_record:
            # If record not found, we can't update it. Log error.
            print(f"Payment record not found for reference: {reference}")
            return {"status": "error", "message": "Payment record not found"}
            
        # 4. Handle Events
        if event == "charge.success":
            # Update PaymentRecord
            payment_update = PaymentRecordUpdate(
                status="SUCCESS",  # Use uppercase to match enum
                paystack_data=payload
            )
            update_payment_record(db, payment_record.id, payment_update)
            
            # Update Transaction
            update_transaction_status(db, payment_record.transaction_id, TransactionStatus.PAYMENT_CONFIRMED)
            
            # Here you would trigger logistics, notify user, etc.
            
            return {"status": "success", "message": "Payment verified"}
            
        elif event == "charge.failed":
            payment_update = PaymentRecordUpdate(
                status="FAILED",  # Use uppercase to match enum
                paystack_data=payload
            )
            update_payment_record(db, payment_record.id, payment_update)
            return {"status": "success", "message": "Payment marked as failed"}
            
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return {"status": "error", "message": str(e)}
        
    return {"status": "ignored"}