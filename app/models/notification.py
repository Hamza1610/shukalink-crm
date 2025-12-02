# app/models/notification.py
from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, Enum, Boolean
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from enum import Enum as PyEnum

class NotificationChannel(PyEnum):
    WHATSAPP = "WHATSAPP"
    SMS = "SMS"
    IN_APP = "IN_APP"
    VOICE_CALL = "VOICE_CALL"

class NotificationType(PyEnum):
    PAYMENT_CONFIRMATION = "PAYMENT_CONFIRMATION"
    PRODUCE_LISTING_CONFIRMATION = "PRODUCE_LISTING_CONFIRMATION"
    LOGISTICS_UPDATE = "LOGISTICS_UPDATE"
    ADVISORY_ALERT = "ADVISORY_ALERT"
    BUYER_INTEREST = "BUYER_INTEREST"
    PRICE_ALERT = "PRICE_ALERT"
    SYSTEM_ALERT = "SYSTEM_ALERT"
    BROADCAST = "BROADCAST"

class NotificationStatus(PyEnum):
    PENDING = "PENDING"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    READ = "READ"
    FAILED = "FAILED"

class NotificationPriority(PyEnum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, default=lambda: f"notif_{uuid4().hex[:8]}")
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    transaction_id = Column(String, ForeignKey("transactions.id"), nullable=True)
    logistics_id = Column(String, ForeignKey("logistics_requests.id"), nullable=True)
    
    # Notification details
    notification_type = Column(Enum(NotificationType, name="notification_type_enum"), default=NotificationType.BROADCAST)
    channel = Column(Enum(NotificationChannel), default=NotificationChannel.WHATSAPP, name="notification_channel_enum")
    title = Column(Text, nullable=False)
    message = Column(Text, nullable=False)
    voice_message_url = Column(String, nullable=True)  # For voice notifications
    
    # Status tracking
    status = Column(Enum(NotificationStatus, name="notification_status_enum"), default=NotificationStatus.PENDING)
    priority = Column(Enum(NotificationPriority, name="priority_enum"), default=NotificationPriority.MEDIUM)
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    
    # Delivery metadata
    delivery_attempts = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="notifications")