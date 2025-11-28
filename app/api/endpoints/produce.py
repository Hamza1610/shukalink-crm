from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.db.session import SessionLocal
from app.schemas.produce import ProduceCreate, ProduceResponse, ProduceSearch
from app.crud.crud_produce import crud_produce
from app.crud.crud_user import crud_user
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ProduceResponse)
def create_produce(
    produce_in: ProduceCreate,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    Create a new produce listing (Farmer only)
    """
    # Verify user is a farmer
    if current_user.user_type != "farmer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only farmers can create produce listings"
        )
    
    # Add farmer_id to the produce data
    produce_data = produce_in.dict()
    produce_data["farmer_id"] = current_user.id
    
    produce = crud_produce.create(db, obj_in=produce_data)
    return produce

@router.get("/", response_model=List[ProduceResponse])
def search_produce(
    crop_type: Optional[str] = None,
    min_quantity: Optional[int] = None,
    radius_km: Optional[int] = None,
    max_price: Optional[float] = None,
    db=Depends(get_db)
):
    """
    Search and list available produce
    """
    filters = {}
    if crop_type:
        filters["crop_type"] = crop_type
    if min_quantity:
        filters["min_quantity"] = min_quantity
    if max_price:
        filters["max_price"] = max_price
    
    produce_list = crud_produce.get_multi_by_filters(db, **filters)
    return produce_list

@router.get("/{produce_id}", response_model=ProduceResponse)
def get_produce(
    produce_id: str,
    db=Depends(get_db)
):
    """
    Get a specific produce listing by ID
    """
    produce = crud_produce.get(db, id=produce_id)
    if not produce:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produce listing not found"
        )
    return produce

@router.put("/{produce_id}", response_model=ProduceResponse)
def update_produce(
    produce_id: str,
    produce_in: ProduceCreate,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    Update a produce listing (Farmer only)
    """
    # Get the existing produce
    existing_produce = crud_produce.get(db, id=produce_id)
    if not existing_produce:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produce listing not found"
        )
    
    # Verify that the current user is the owner
    if existing_produce.farmer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this produce listing"
        )
    
    # Update the produce
    updated_produce = crud_produce.update(db, db_obj=existing_produce, obj_in=produce_in.dict())
    return updated_produce

@router.delete("/{produce_id}")
def delete_produce(
    produce_id: str,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    Delete a produce listing (Farmer only)
    """
    # Get the existing produce
    existing_produce = crud_produce.get(db, id=produce_id)
    if not existing_produce:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produce listing not found"
        )
    
    # Verify that the current user is the owner
    if existing_produce.farmer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this produce listing"
        )
    
    # Delete the produce
    crud_produce.remove(db, id=produce_id)
    return {"message": "Produce listing deleted successfully"}