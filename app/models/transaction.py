# app/models/transaction.py
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum, Boolean, JSON
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from enum import Enum as PyEnum

class TransactionStatus(PyEnum):
    PENDING = "pending"          # Matched but not paid
    PAYMENT_INITIATED = "payment_initiated"  # Payment link sent
    PAYMENT_CONFIRMED = "payment_confirmed"  # Payment received
    IN_LOGISTICS = "in_logistics" # Transport arranged
    DELIVERED = "delivered"       # Successfully delivered
    COMPLETED = "completed"       # Payment released to farmer
    DISPUTED = "disputed"         # Problem reported
    CANCELLED = "cancelled"       # Transaction cancelled

class PaymentMethod(PyEnum):
    PAYSTACK = "paystack"
    BANK_TRANSFER = "bank_transfer"
    CASH_ON_DELIVERY = "cash_on_delivery"
    MOBILE_MONEY = "mobile_money"

class PaymentStatus(PyEnum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, index=True, default=lambda: f"txn_{uuid4().hex[:8]}")
    produce_listing_id = Column(String, ForeignKey("produce_listings.id"), nullable=False)
    seller_id = Column(String, ForeignKey("users.id"), nullable=False)  # Farmer
    buyer_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Transaction details
    agreed_price_per_kg = Column(Float, nullable=False)
    quantity_kg = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)  # Calculated: price * quantity
    
    # Status & timing
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    matched_at = Column(DateTime, default=datetime.utcnow)
    payment_confirmed_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    produce_listing = relationship("ProduceListing", back_populates="transactions")
    seller = relationship("User", foreign_keys=[seller_id], back_populates="transactions_as_seller")
    buyer = relationship("User", foreign_keys=[buyer_id], back_populates="transactions_as_buyer")
    payment_records = relationship("PaymentRecord", back_populates="transaction")
    logistics_request = relationship("LogisticsRequest", uselist=False, back_populates="transaction")
    
    @property
    def payment_status(self):
        if not self.payment_records:
            return "not_initiated"
        latest_payment = max(self.payment_records, key=lambda p: p.created_at)
        return latest_payment.status
    
    @property
    def estimated_delivery_date(self):
        """Estimate delivery date based on logistics data"""
        if self.logistics_request and self.logistics_request.scheduled_pickup:
            # Simple estimation: pickup + 1 day
            return self.logistics_request.scheduled_pickup + timedelta(days=1)
        return None

class PaymentRecord(Base):
    __tablename__ = "payment_records"

    id = Column(String, primary_key=True, default=lambda: f"pay_{uuid4().hex[:8]}")
    transaction_id = Column(String, ForeignKey("transactions.id"), nullable=False)
    
    # Payment details
    payment_method = Column(Enum(PaymentMethod), default=PaymentMethod.PAYSTACK)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="NGN")
    reference = Column(String, unique=True, nullable=False)  # Paystack reference
    
    # Status tracking
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    confirmed_at = Column(DateTime, nullable=True)
    
    # Paystack specific data
    paystack_data = Column(JSON, nullable=True)  # Raw webhook data
    
    # Relationships
    transaction = relationship("Transaction", back_populates="payment_records")