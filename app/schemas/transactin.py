from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class TransactionBase(BaseModel):
    produce_listing_id: str
    seller_id: str
    buyer_id: str
    agreed_price_per_kg: float
    quantity_kg: float
    total_amount: float
    status: str


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    agreed_price_per_kg: Optional[float] = None
    quantity_kg: Optional[float] = None
    total_amount: Optional[float] = None
    status: Optional[str] = None


class Transaction(TransactionBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


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