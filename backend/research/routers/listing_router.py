"""Listing management - CRUD operations for vintage jeans listings."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

from research.db.supabase_client import get_supabase_client
from research.services.auth_service_supabase import get_current_seller, get_current_admin

# Enum values as constants (these are stored as strings in Supabase)
class ListingStatus:
    PENDING_APPROVAL = "pending_approval"
    ACTIVE = "active"
    SOLD = "sold"
    ARCHIVED = "archived"
    REJECTED = "rejected"

class PlatformEnum:
    MANUAL = "manual"
    EBAY = "ebay"
    ETSY = "etsy"
    DEPOP = "depop"
    GRAILED = "grailed"
    POSHMARK = "poshmark"

class ConditionGrade:
    NEW_WITH_TAGS = "new_with_tags"
    NEW_WITHOUT_TAGS = "new_without_tags"
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"

router = APIRouter()

# Pydantic models


class ListingCreate(BaseModel):
    title: str
    description: str
    brand: str
    decade: Optional[str] = None
    year: Optional[int] = None
    model: Optional[str] = None
    waist_size: Optional[int] = None
    inseam_length: Optional[int] = None
    size_label: Optional[str] = None
    condition: str  # ConditionGrade constant
    condition_notes: Optional[str] = None
    material: Optional[str] = None
    wash: Optional[str] = None
    features: Optional[str] = None
    price: float
    currency: str = "USD"
    purchase_price: Optional[float] = None
    shipping_cost: float = 0.0
    ships_from: Optional[str] = None
    ships_to: Optional[str] = None
    primary_image_url: Optional[str] = None
    image_urls: Optional[str] = None
    provenance: Optional[str] = None
    tags: Optional[str] = None
    category: Optional[str] = None


class ListingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    condition: Optional[str] = None  # ConditionGrade constant
    status: Optional[str] = None  # ListingStatus constant
    is_featured: Optional[bool] = None


class ListingResponse(BaseModel):
    id: str  # UUID
    seller_id: str  # UUID
    platform: str
    title: str
    description: str
    brand: str
    decade: Optional[str]
    model: Optional[str]
    waist_size: Optional[int]
    inseam_length: Optional[int]
    condition: str
    price: float
    currency: str
    purchase_price: Optional[float]
    status: str
    views: int
    favorites: int
    is_featured: bool
    primary_image_url: Optional[str]
    created_at: str
    updated_at: str


# CRUD Endpoints

@router.post("/", response_model=ListingResponse, status_code=status.HTTP_201_CREATED)
async def create_listing(
    listing_data: ListingCreate,
    current_seller: Dict[str, Any] = Depends(get_current_seller)
):
    """Create a new listing (manual entry by seller)."""

    supabase = get_supabase_client()

    # Prepare listing data
    listing_insert_data = {
        "seller_id": current_seller["id"],
        "platform": PlatformEnum.MANUAL,
        **listing_data.model_dump(),
        "status": ListingStatus.PENDING_APPROVAL,
        "views": 0,
        "favorites": 0,
        "is_featured": False
    }

    # Insert listing
    insert_response = supabase.table("listings").insert(listing_insert_data).execute()

    if not insert_response.data or len(insert_response.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create listing"
        )

    new_listing = insert_response.data[0]

    # Update seller's listing count
    supabase.table("sellers").update({
        "total_listings": current_seller["total_listings"] + 1
    }).eq("id", current_seller["id"]).execute()

    return ListingResponse(
        id=new_listing["id"],
        seller_id=new_listing["seller_id"],
        platform=new_listing["platform"],
        title=new_listing["title"],
        description=new_listing["description"],
        brand=new_listing["brand"],
        decade=new_listing.get("decade"),
        model=new_listing.get("model"),
        waist_size=new_listing.get("waist_size"),
        inseam_length=new_listing.get("inseam_length"),
        condition=new_listing["condition"],
        price=new_listing["price"],
        currency=new_listing["currency"],
        purchase_price=new_listing.get("purchase_price"),
        status=new_listing["status"],
        views=new_listing["views"],
        favorites=new_listing["favorites"],
        is_featured=new_listing["is_featured"],
        primary_image_url=new_listing.get("primary_image_url"),
        created_at=new_listing["created_at"],
        updated_at=new_listing["updated_at"]
    )


@router.get("/", response_model=List[ListingResponse])
async def list_listings(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    platform: Optional[str] = None,
    status_filter: Optional[str] = None,
    brand: Optional[str] = None,
    decade: Optional[str] = None,
    seller_id: Optional[str] = None,  # UUID
    current_seller: Dict[str, Any] = Depends(get_current_seller)
):
    """List listings with filters. Sellers see their own, admins see all."""

    supabase = get_supabase_client()

    # Start building query
    query = supabase.table("listings").select("*")

    # Non-admin sellers can only see their own listings
    if current_seller["role"] != "admin":
        query = query.eq("seller_id", current_seller["id"])
    elif seller_id:
        query = query.eq("seller_id", seller_id)

    # Apply filters
    if platform:
        query = query.eq("platform", platform)
    if status_filter:
        query = query.eq("status", status_filter)
    if brand:
        query = query.ilike("brand", f"%{brand}%")
    if decade:
        query = query.eq("decade", decade)

    # Pagination and ordering
    end = skip + limit - 1
    response = query.order("created_at", desc=True).range(skip, end).execute()

    if not response.data:
        return []

    return [
        ListingResponse(
            id=listing["id"],
            seller_id=listing["seller_id"],
            platform=listing["platform"],
            title=listing["title"],
            description=listing["description"],
            brand=listing["brand"],
            decade=listing.get("decade"),
            model=listing.get("model"),
            waist_size=listing.get("waist_size"),
            inseam_length=listing.get("inseam_length"),
            condition=listing["condition"],
            price=listing["price"],
            currency=listing["currency"],
            purchase_price=listing.get("purchase_price"),
            status=listing["status"],
            views=listing["views"],
            favorites=listing["favorites"],
            is_featured=listing["is_featured"],
            primary_image_url=listing.get("primary_image_url"),
            created_at=listing["created_at"],
            updated_at=listing["updated_at"]
        )
        for listing in response.data
    ]


@router.get("/{listing_id}", response_model=ListingResponse)
async def get_listing(
    listing_id: str,  # UUID
    current_seller: Dict[str, Any] = Depends(get_current_seller)
):
    """Get a specific listing by ID."""

    supabase = get_supabase_client()

    # Fetch listing
    response = supabase.table("listings").select("*").eq("id", listing_id).execute()

    if not response.data or len(response.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found"
        )

    listing = response.data[0]

    # Non-admin sellers can only access their own listings
    if current_seller["role"] != "admin" and listing["seller_id"] != current_seller["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this listing"
        )

    # Increment view count
    new_views = listing["views"] + 1
    supabase.table("listings").update({
        "views": new_views
    }).eq("id", listing_id).execute()

    listing["views"] = new_views

    return ListingResponse(
        id=listing["id"],
        seller_id=listing["seller_id"],
        platform=listing["platform"],
        title=listing["title"],
        description=listing["description"],
        brand=listing["brand"],
        decade=listing.get("decade"),
        model=listing.get("model"),
        waist_size=listing.get("waist_size"),
        inseam_length=listing.get("inseam_length"),
        condition=listing["condition"],
        price=listing["price"],
        currency=listing["currency"],
        purchase_price=listing.get("purchase_price"),
        status=listing["status"],
        views=listing["views"],
        favorites=listing["favorites"],
        is_featured=listing["is_featured"],
        primary_image_url=listing.get("primary_image_url"),
        created_at=listing["created_at"],
        updated_at=listing["updated_at"]
    )


@router.patch("/{listing_id}", response_model=ListingResponse)
async def update_listing(
    listing_id: str,  # UUID
    updates: ListingUpdate,
    current_seller: Dict[str, Any] = Depends(get_current_seller)
):
    """Update a listing."""

    supabase = get_supabase_client()

    # Fetch listing to check authorization
    response = supabase.table("listings").select("*").eq("id", listing_id).execute()

    if not response.data or len(response.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found"
        )

    listing = response.data[0]

    # Authorization check
    if current_seller["role"] != "admin" and listing["seller_id"] != current_seller["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this listing"
        )

    # Apply updates
    update_data = updates.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow().isoformat()

    # Update listing
    update_response = supabase.table("listings").update(
        update_data
    ).eq("id", listing_id).execute()

    if not update_response.data or len(update_response.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update listing"
        )

    updated_listing = update_response.data[0]

    return ListingResponse(
        id=updated_listing["id"],
        seller_id=updated_listing["seller_id"],
        platform=updated_listing["platform"],
        title=updated_listing["title"],
        description=updated_listing["description"],
        brand=updated_listing["brand"],
        decade=updated_listing.get("decade"),
        model=updated_listing.get("model"),
        waist_size=updated_listing.get("waist_size"),
        inseam_length=updated_listing.get("inseam_length"),
        condition=updated_listing["condition"],
        price=updated_listing["price"],
        currency=updated_listing["currency"],
        purchase_price=updated_listing.get("purchase_price"),
        status=updated_listing["status"],
        views=updated_listing["views"],
        favorites=updated_listing["favorites"],
        is_featured=updated_listing["is_featured"],
        primary_image_url=updated_listing.get("primary_image_url"),
        created_at=updated_listing["created_at"],
        updated_at=updated_listing["updated_at"]
    )


@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_listing(
    listing_id: str,  # UUID
    current_seller: Dict[str, Any] = Depends(get_current_seller)
):
    """Delete a listing."""

    supabase = get_supabase_client()

    # Fetch listing
    response = supabase.table("listings").select("*").eq("id", listing_id).execute()

    if not response.data or len(response.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found"
        )

    listing = response.data[0]

    # Authorization check
    if current_seller["role"] != "admin" and listing["seller_id"] != current_seller["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this listing"
        )

    # Update seller's listing count
    seller_response = supabase.table("sellers").select("*").eq("id", listing["seller_id"]).execute()
    if seller_response.data and len(seller_response.data) > 0:
        seller = seller_response.data[0]
        new_total = max(0, seller["total_listings"] - 1)
        new_active = seller["active_listings"]

        if listing["status"] == ListingStatus.ACTIVE:
            new_active = max(0, seller["active_listings"] - 1)

        supabase.table("sellers").update({
            "total_listings": new_total,
            "active_listings": new_active
        }).eq("id", listing["seller_id"]).execute()

    # Delete listing
    supabase.table("listings").delete().eq("id", listing_id).execute()

    return None


# Admin approval endpoints

@router.post("/{listing_id}/approve", response_model=ListingResponse)
async def approve_listing(
    listing_id: str,  # UUID
    current_admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Approve a pending listing (admin only)."""

    supabase = get_supabase_client()

    # Fetch listing
    response = supabase.table("listings").select("*").eq("id", listing_id).execute()

    if not response.data or len(response.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found"
        )

    listing = response.data[0]

    # Update listing status
    update_response = supabase.table("listings").update({
        "status": ListingStatus.ACTIVE,
        "approved_by": current_admin["id"],
        "approved_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }).eq("id", listing_id).execute()

    if not update_response.data or len(update_response.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to approve listing"
        )

    approved_listing = update_response.data[0]

    # Update seller's active listing count
    seller_response = supabase.table("sellers").select("*").eq("id", listing["seller_id"]).execute()
    if seller_response.data and len(seller_response.data) > 0:
        seller = seller_response.data[0]
        supabase.table("sellers").update({
            "active_listings": seller["active_listings"] + 1
        }).eq("id", listing["seller_id"]).execute()

    return ListingResponse(
        id=approved_listing["id"],
        seller_id=approved_listing["seller_id"],
        platform=approved_listing["platform"],
        title=approved_listing["title"],
        description=approved_listing["description"],
        brand=approved_listing["brand"],
        decade=approved_listing.get("decade"),
        model=approved_listing.get("model"),
        waist_size=approved_listing.get("waist_size"),
        inseam_length=approved_listing.get("inseam_length"),
        condition=approved_listing["condition"],
        price=approved_listing["price"],
        currency=approved_listing["currency"],
        purchase_price=approved_listing.get("purchase_price"),
        status=approved_listing["status"],
        views=approved_listing["views"],
        favorites=approved_listing["favorites"],
        is_featured=approved_listing["is_featured"],
        primary_image_url=approved_listing.get("primary_image_url"),
        created_at=approved_listing["created_at"],
        updated_at=approved_listing["updated_at"]
    )


@router.post("/{listing_id}/reject", response_model=ListingResponse)
async def reject_listing(
    listing_id: str,  # UUID
    reason: str,
    current_admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Reject a pending listing (admin only)."""

    supabase = get_supabase_client()

    # Fetch listing
    response = supabase.table("listings").select("*").eq("id", listing_id).execute()

    if not response.data or len(response.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found"
        )

    # Update listing status
    update_response = supabase.table("listings").update({
        "status": ListingStatus.REJECTED,
        "rejection_reason": reason,
        "approved_by": current_admin["id"],
        "approved_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }).eq("id", listing_id).execute()

    if not update_response.data or len(update_response.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reject listing"
        )

    rejected_listing = update_response.data[0]

    return ListingResponse(
        id=rejected_listing["id"],
        seller_id=rejected_listing["seller_id"],
        platform=rejected_listing["platform"],
        title=rejected_listing["title"],
        description=rejected_listing["description"],
        brand=rejected_listing["brand"],
        decade=rejected_listing.get("decade"),
        model=rejected_listing.get("model"),
        waist_size=rejected_listing.get("waist_size"),
        inseam_length=rejected_listing.get("inseam_length"),
        condition=rejected_listing["condition"],
        price=rejected_listing["price"],
        currency=rejected_listing["currency"],
        purchase_price=rejected_listing.get("purchase_price"),
        status=rejected_listing["status"],
        views=rejected_listing["views"],
        favorites=rejected_listing["favorites"],
        is_featured=rejected_listing["is_featured"],
        primary_image_url=rejected_listing.get("primary_image_url"),
        created_at=rejected_listing["created_at"],
        updated_at=rejected_listing["updated_at"]
    )
