from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.db.session import SessionLocal
from app.schemas.produce import ProduceCreate, ProduceResponse, ProduceSearch, ProduceListingUpdate
from app.crud import create_produce_listing, get_produce_listing, delete_produce_listing, update_produce_listing, get_produce_listings, search_produce_listings
from app.crud import crud_produce
from app.api.deps import get_current_user
from app.models.user import User, UserType

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
    if current_user.user_type != UserType.FARMER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only farmers can create produce listings"
        )
    
    # Add farmer_id to the produce data
    produce_data = produce_in.model_dump()

    produce_data["farmer_id"] = current_user.id
    


    # print("Produce", produce_data)
    # produce = create_produce_listing(db, produce_data)
    # return produce

    # produce_data = {
    #     **produce_in.model_dump(),
    #     farmer_id=current_user.id
    # }

    return create_produce_listing(db, produce_data)



@router.get("/all", response_model=List[ProduceResponse])
def get_all_produce(
    skip: int = 0,
    limit: int = 100,
    farmer_id: Optional[str] = None,
    db=Depends(get_db)
):
    """
    Search and list available produce
    """
    filters = {
        "skip": skip,
        "limit": limit
    }

    if farmer_id:
        filters["farmer_id"] = farmer_id

    produce_list = get_produce_listings(db, **filters)
    return produce_list

@router.get("/", response_model=List[ProduceResponse])
def search_produce(
    crop_type: Optional[str] = None,
    min_quantity: Optional[int] = None,
    radius_km: Optional[int] = None,
    max_price: Optional[float] = None,
    farmer_id: Optional[str] = None,
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
    if radius_km:
        filters["radius_km"] = radius_km
    if radius_km:
        filters["radius_km"] = radius_km
    if farmer_id:
        filters["farmer_id"] = farmer_id
    
    produce_list = search_produce_listings(db, **filters)
    return produce_list

@router.get("/{produce_id}", response_model=ProduceResponse)
def get_produce_details(
    produce_id: str,
    db=Depends(get_db)
):
    """
    Get a specific produce listing by ID
    """
    produce = get_produce_listing(db, produce_id)
    if not produce:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produce listing not found"
        )
    return produce

@router.put("/{produce_id}", response_model=ProduceResponse)
def update_produce(
    produce_id: str,
    produce_in: ProduceListingUpdate,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    Update a produce listing (Farmer only)
    """
    # Get the existing produce
    existing_produce = get_produce_listing(db, produce_id)
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
    updated_produce = update_produce_listing(db, existing_produce.id, produce_in.model_dump())
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
    existing_produce = get_produce_listing(db, produce_id)
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
    delete_produce_listing(db, produce_id)
    return {"message": "Produce listing deleted successfully"}