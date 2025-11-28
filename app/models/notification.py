# app/models/notification.py
from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, Enum, Boolean
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from enum import Enum as PyEnum

class NotificationChannel(PyEnum):
    WHATSAPP = "whatsapp"
    SMS = "sms"
    IN_APP = "in_app"
    VOICE_CALL = "voice_call"

class NotificationType(PyEnum):
    PAYMENT_CONFIRMATION = "payment_confirmation"
    PRODUCE_LISTING_CONFIRMATION = "produce_listing_confirmation"
    LOGISTICS_UPDATE = "logistics_update"
    ADVISORY_ALERT = "advisory_alert"
    BUYER_INTEREST = "buyer_interest"
    PRICE_ALERT = "price_alert"
    SYSTEM_ALERT = "system_alert"

class NotificationStatus(PyEnum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, default=lambda: f"notif_{uuid4().hex[:8]}")
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    transaction_id = Column(String, ForeignKey("transactions.id"), nullable=True)
    logistics_id = Column(String, ForeignKey("logistics_requests.id"), nullable=True)
    
    # Notification details
    notification_type = Column(Enum(NotificationType), nullable=False)
    channel = Column(Enum(NotificationChannel), default=NotificationChannel.WHATSAPP)
    message = Column(Text, nullable=False)
    voice_message_url = Column(String, nullable=True)  # For voice notifications
    
    # Status tracking
    status = Column(Enum(NotificationStatus), default=NotificationStatus.PENDING)
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    
    # Delivery metadata
    delivery_attempts = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="notifications")