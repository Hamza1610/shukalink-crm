# app/crud/crud_notification.py
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate, NotificationUpdate


def create_notification(db: Session, notification: NotificationCreate, user_id: str) -> Notification:
    """Create a new notification."""
    db_notification = Notification(
        user_id=user_id,
        transaction_id=notification.transaction_id,
        logistics_id=notification.logistics_id,
        notification_type=notification.notification_type,
        channel=notification.channel,
        message=notification.message,
        voice_message_url=notification.voice_message_url,
        status=notification.status,
        error_message=notification.error_message
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification


def get_notification(db: Session, notification_id: str) -> Optional[Notification]:
    """Get a notification by ID."""
    return db.query(Notification).filter(Notification.id == notification_id).first()


def get_notifications(db: Session, skip: int = 0, limit: int = 100, user_id: Optional[str] = None) -> List[Notification]:
    """Get a list of notifications."""
    query = db.query(Notification)
    if user_id:
        query = query.filter(Notification.user_id == user_id)
    return query.offset(skip).limit(limit).all()


def update_notification(db: Session, notification_id: str, notification_update: NotificationUpdate) -> Optional[Notification]:
    """Update a notification."""
    db_notification = get_notification(db, notification_id)
    if db_notification:
        update_data = notification_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_notification, field, value)
        db.commit()
        db.refresh(db_notification)
    return db_notification


def delete_notification(db: Session, notification_id: str) -> bool:
    """Delete a notification."""
    db_notification = get_notification(db, notification_id)
    if db_notification:
        db.delete(db_notification)
        db.commit()
        return True
    return False