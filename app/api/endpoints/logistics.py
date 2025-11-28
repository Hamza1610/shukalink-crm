from fastapi import APIRouter, Depends, HTTPException, status
from app.db.session import SessionLocal
from app.schemas.logistics import LogisticsRequest, LogisticsResponse
from app.crud.crud_logistics import crud_logistics
from app.crud.crud_transaction import crud_transaction
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=LogisticsResponse)
def request_logistics(
    logistics_request: LogisticsRequest,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    Request transport for a transaction
    """
    # Verify that the user is part of the transaction
    transaction = crud_transaction.get(db, id=logistics_request.transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    if transaction.buyer_id != current_user.id and transaction.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to request logistics for this transaction"
        )
    
    # Create logistics request
    logistics_data = logistics_request.dict()
    logistics_data["requester_id"] = current_user.id
    
    logistics = crud_logistics.create(db, obj_in=logistics_data)
    return logistics

@router.get("/{logistics_id}", response_model=LogisticsResponse)
def get_logistics(
    logistics_id: str,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    Get logistics request by ID
    """
    logistics = crud_logistics.get(db, id=logistics_id)
    if not logistics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Logistics request not found"
        )
    
    # Verify user has access to this logistics request
    if logistics.requester_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this logistics request"
        )
    
    return logistics

@router.put("/{logistics_id}", response_model=LogisticsResponse)
def update_logistics(
    logistics_id: str,
    logistics_update: LogisticsRequest,  # This should actually be a different schema
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    Update logistics request status
    """
    logistics = crud_logistics.get(db, id=logistics_id)
    if not logistics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Logistics request not found"
        )
    
    # Verify user has permission to update
    if logistics.requester_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this logistics request"
        )
    
    # Update logistics
    updated_logistics = crud_logistics.update(db, db_obj=logistics, obj_in=logistics_update.dict())
    return updated_logistics

@router.patch("/{logistics_id}/status")
def update_logistics_status(
    logistics_id: str,
    status: str,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    Update logistics request status
    """
    logistics = crud_logistics.get(db, id=logistics_id)
    if not logistics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Logistics request not found"
        )
    
    # Verify user has permission to update
    if logistics.requester_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this logistics request"
        )
    
    # Update status
    logistics_data = {"status": status}
    updated_logistics = crud_logistics.update(db, db_obj=logistics, obj_in=logistics_data)
    return updated_logistics