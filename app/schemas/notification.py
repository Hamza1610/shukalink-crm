from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class NotificationBase(BaseModel):
    user_id: str
    transaction_id: Optional[str] = None
    logistics_id: Optional[str] = None
    notification_type: str
    channel: str
    message: str
    voice_message_url: Optional[str] = None
    status: str
    error_message: Optional[str] = None


class NotificationCreate(NotificationBase):
    pass


class NotificationUpdate(BaseModel):
    transaction_id: Optional[str] = None
    logistics_id: Optional[str] = None
    notification_type: Optional[str] = None
    channel: Optional[str] = None
    message: Optional[str] = None
    voice_message_url: Optional[str] = None
    status: Optional[str] = None
    error_message: Optional[str] = None


class Notification(NotificationBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True