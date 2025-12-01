from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.db.session import SessionLocal
from app.models.user import User, UserType
from app.api.deps import get_current_user, get_db
from app.schemas.user import UserResponse
from app.crud import get_users, get_user, get_user_by_phone, create_user, delete_user, update_user
from app.models.produce import ProduceListing
from app.models.transaction import Transaction
from app.models.notification import Notification
from app.models.conversation import ChatSession as Conversation
from app.models.logistics import LogisticsRequest
from app.schemas import user as user_schemas

router = APIRouter()

def require_admin(current_user: User = Depends(get_current_user)):
    """
    Dependency to ensure the current user is an admin
    """
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can perform this action"
        )
    return current_user

@router.get("/users", response_model=List[UserResponse])
def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_admin),
    db=Depends(get_db)
):
    """
    Get all users (Admin only)
    """
    users = get_users(db, skip=skip, limit=limit)
    return users

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: str,
    current_user: User = Depends(require_admin),
    db=Depends(get_db)
):
    """
    Get a specific user by ID (Admin only)
    """
    print("Userid: ", user_id, "Current_user: ", current_user)

    user = get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.put("/users/{user_id}/user-type")
def update_user_type(
    user_id: str,
    user_type: UserType,
    current_user: User = Depends(require_admin),
    db=Depends(get_db)
):
    """
    Update user type (Admin only)
    """
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user type
    user.user_type = user_type
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {"message": f"User type updated to {user_type.value}", "user": UserResponse.from_orm(user)}

@router.delete("/users/{user_id}")
def delete_user_by_id(
    user_id: str,
    current_user: User = Depends(require_admin),
    db=Depends(get_db)
):
    """
    Delete a user (Admin only)
    """
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # For now, we'll just mark as deleted rather than hard delete
    # In a real application, you might want to implement soft delete
    delete_user(db, user_id)
    
    return {"message": "User deleted successfully"}

@router.get("/statistics")
def get_platform_statistics(
    current_user: User = Depends(require_admin),
    db=Depends(get_db)
):
    """
    Get platform statistics (Admin only)
    """
    total_users = db.query(User).count()
    total_produce_listings = db.query(ProduceListing).count()
    total_transactions = db.query(Transaction).count()
    total_notifications = db.query(Notification).count()
    total_conversations = db.query(Conversation).count()
    
    # Count users by type
    farmer_count = db.query(User).filter(User.user_type == UserType.FARMER).count()
    buyer_count = db.query(User).filter(User.user_type == UserType.BUYER).count()
    admin_count = db.query(User).filter(User.user_type == UserType.ADMIN).count()
    aggregator_count = db.query(User).filter(User.user_type == UserType.AGGREGATOR).count()
    
    return {
        "total_users": total_users,
        "total_produce_listings": total_produce_listings,
        "total_transactions": total_transactions,
        "total_notifications": total_notifications,
        "total_conversations": total_conversations,
        "user_breakdown": {
            "farmers": farmer_count,
            "buyers": buyer_count,
            "admins": admin_count,
            "aggregators": aggregator_count
        }
    }

@router.get("/transactions")
def get_all_transactions(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_admin),
    db=Depends(get_db)
):
    """
    Get all transactions (Admin only)
    """
    transactions = db.query(Transaction).offset(skip).limit(limit).all()
    return transactions

@router.get("/produce-listings")
def get_all_produce_listings(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_admin),
    db=Depends(get_db)
):
    """
    Get all produce listings (Admin only)
    """
    produce_listings = db.query(ProduceListing).offset(skip).limit(limit).all()
    return produce_listings


@router.get("/logistics-requests")
def get_all_logistics_requests(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_admin),
    db=Depends(get_db)
):
    """
    Get all logistics requests (Admin only)
    """
    logistics_requests = db.query(LogisticsRequest).offset(skip).limit(limit).all()
    return logistics_requests


@router.put("/logistics-requests/{request_id}/status")
def update_logistics_status(
    request_id: str,
    status: str,
    current_user: User = Depends(require_admin),
    db=Depends(get_db)
):
    """
    Update logistics request status (Admin only)
    """
    from app.models.logistics import LogisticsStatus
    
    try:
        new_status = LogisticsStatus(status.upper())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status value"
        )
    
    logistics_request = db.query(LogisticsRequest).filter(LogisticsRequest.id == request_id).first()
    if not logistics_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Logistics request not found"
        )
    
    logistics_request.status = new_status
    db.add(logistics_request)
    db.commit()
    db.refresh(logistics_request)
    
    return {"message": f"Logistics request status updated to {new_status.value}", "request": logistics_request}


@router.get("/notifications")
def get_all_notifications(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_admin),
    db=Depends(get_db)
):
    """
    Get all notifications (Admin only)
    """
    notifications = db.query(Notification).offset(skip).limit(limit).all()
    return notifications


@router.post("/notifications/broadcast")
def broadcast_notification(
    title: str,
    message: str,
    user_type: UserType = None,
    current_user: User = Depends(require_admin),
    db=Depends(get_db)
):
    """
    Broadcast notification to all users or specific user type (Admin only)
    """
    from app.models.notification import Notification as NotificationModel
    
    # Create a broadcast notification
    notification = NotificationModel(
        title=title,
        message=message,
        notification_type="broadcast",
        priority="high"
    )
    
    # If user_type is specified, send to specific user type, otherwise to all
    if user_type:
        users = db.query(User).filter(User.user_type == user_type).all()
    else:
        users = db.query(User).all()
    
    # Send notification to each user
    for user in users:
        notification.user_id = user.id
        db.add(notification)
    
    db.commit()
    
    return {
        "message": f"Broadcast notification sent to {len(users)} users",
        "user_type": user_type.value if user_type else "all"
    }


@router.get("/activity-logs")
def get_platform_activity_logs(
    days: int = 7,
    current_user: User = Depends(require_admin),
    db=Depends(get_db)
):
    """
    Get platform activity logs for the specified number of days (Admin only)
    """
    from datetime import datetime, timedelta
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # This would typically connect to a logging system
    # For now, we'll return basic statistics
    user_activity = db.query(User).filter(User.last_active >= cutoff_date).count()
    produce_activity = db.query(ProduceListing).filter(ProduceListing.created_at >= cutoff_date).count()
    transaction_activity = db.query(Transaction).filter(Transaction.created_at >= cutoff_date).count()
    
    return {
        "period_days": days,
        "cutoff_date": cutoff_date,
        "user_activity": user_activity,
        "produce_activity": produce_activity,
        "transaction_activity": transaction_activity,
        "summary": f"Activity for the last {days} days: {user_activity} active users, {produce_activity} new listings, {transaction_activity} transactions"
    }