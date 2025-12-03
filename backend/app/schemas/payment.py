
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class PaymentRecordBase(BaseModel):
    transaction_id: str
    payment_method: str
    amount: float
    currency: str
    reference: str
    status: str
    paystack_data: Optional[dict] = None


class PaymentRecordCreate(PaymentRecordBase):
    pass


class PaymentRecordUpdate(BaseModel):
    payment_method: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    reference: Optional[str] = None
    status: Optional[str] = None
    paystack_data: Optional[dict] = None


class PaymentRecord(PaymentRecordBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True