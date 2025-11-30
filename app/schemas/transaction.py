from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from enum import Enum


class TransactionStatus(Enum):
    PENDING = "pending"          # Matched but not paid
    PAYMENT_INITIATED = "payment_initiated"  # Payment link sent
    PAYMENT_CONFIRMED = "payment_confirmed"  # Payment received
    IN_LOGISTICS = "in_logistics" # Transport arranged
    DELIVERED = "delivered"       # Successfully delivered
    COMPLETED = "completed"       # Payment released to farmer
    DISPUTED = "disputed"         # Problem reported
    CANCELLED = "cancelled"       # Transaction cancelled


class TransactionCreate(BaseModel):
    produce_listing_id: str
    seller_id: str  # Farmer
    buyer_id: str
    agreed_price_per_kg: float
    quantity_kg: float
    total_amount: float  # Calculated: price * quantity
    status: Optional[TransactionStatus] = TransactionStatus.PENDING


class TransactionUpdate(BaseModel):
    produce_listing_id: Optional[str] = None
    seller_id: Optional[str] = None
    buyer_id: Optional[str] = None
    agreed_price_per_kg: Optional[float] = None
    quantity_kg: Optional[float] = None
    total_amount: Optional[float] = None
    status: Optional[TransactionStatus] = None


class TransactionResponse(BaseModel):
    id: str
    produce_listing_id: str
    seller_id: str
    buyer_id: str
    agreed_price_per_kg: float
    quantity_kg: float
    total_amount: float
    status: TransactionStatus
    matched_at: datetime
    payment_confirmed_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
