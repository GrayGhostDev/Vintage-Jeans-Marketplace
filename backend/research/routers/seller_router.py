"""Seller registration, authentication, and profile management."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import timedelta, datetime

from research.db.supabase_client import get_supabase_client
from research.services.auth_service_supabase import (
    get_password_hash,
    authenticate_seller,
    create_access_token,
    get_current_seller,
    get_current_admin,
    generate_referral_code,
    update_last_login,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter()

# Pydantic models for request/response


class SellerRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    business_name: Optional[str] = None
    phone: Optional[str] = None
    location: str
    referred_by_code: Optional[str] = None

class SellerResponse(BaseModel):
    id: str  # UUID
    email: str
    full_name: str
    business_name: Optional[str]
    location: str
    is_verified: bool
    role: str
    total_listings: int
    active_listings: int
    referral_code: Optional[str]
    created_at: str

class SellerUpdate(BaseModel):
    full_name: Optional[str] = None
    business_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    seller: SellerResponse


# Authentication endpoints

@router.post("/register", response_model=SellerResponse, status_code=status.HTTP_201_CREATED)
def register_seller(seller_data: SellerRegister):
    """Register a new seller account."""

    supabase = get_supabase_client()

    # Check if seller already exists
    existing_response = supabase.table("sellers").select("id").eq("email", seller_data.email).execute()

    if existing_response.data and len(existing_response.data) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Handle referral code if provided
    referred_by_id = None
    if seller_data.referred_by_code:
        referrer_response = supabase.table("sellers").select("id").eq(
            "referral_code", seller_data.referred_by_code
        ).execute()

        if referrer_response.data and len(referrer_response.data) > 0:
            referred_by_id = referrer_response.data[0]["id"]

    # Create new seller
    seller_insert_data = {
        "email": seller_data.email,
        "hashed_password": get_password_hash(seller_data.password),
        "full_name": seller_data.full_name,
        "business_name": seller_data.business_name,
        "phone": seller_data.phone,
        "location": seller_data.location,
        "referred_by": referred_by_id,
        "is_active": True,
        "is_verified": False,
        "role": "seller",
        "total_listings": 0,
        "active_listings": 0
    }

    insert_response = supabase.table("sellers").insert(seller_insert_data).execute()

    if not insert_response.data or len(insert_response.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create seller account"
        )

    new_seller = insert_response.data[0]

    # Generate and update referral code after we have the seller UUID
    referral_code = generate_referral_code(new_seller["id"], new_seller["full_name"])

    update_response = supabase.table("sellers").update({
        "referral_code": referral_code
    }).eq("id", new_seller["id"]).execute()

    if update_response.data and len(update_response.data) > 0:
        new_seller = update_response.data[0]

    return SellerResponse(
        id=new_seller["id"],
        email=new_seller["email"],
        full_name=new_seller["full_name"],
        business_name=new_seller.get("business_name"),
        location=new_seller["location"],
        is_verified=new_seller["is_verified"],
        role=new_seller["role"],
        total_listings=new_seller["total_listings"],
        active_listings=new_seller["active_listings"],
        referral_code=new_seller.get("referral_code"),
        created_at=new_seller["created_at"]
    )


@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate seller and return access token."""

    seller = authenticate_seller(form_data.username, form_data.password)

    if not seller:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last login timestamp
    update_last_login(seller["id"])

    # Create access token (sub should be string UUID)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": seller["id"], "email": seller["email"], "role": seller["role"]},
        expires_delta=access_token_expires
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        seller=SellerResponse(
            id=seller["id"],
            email=seller["email"],
            full_name=seller["full_name"],
            business_name=seller.get("business_name"),
            location=seller["location"],
            is_verified=seller["is_verified"],
            role=seller["role"],
            total_listings=seller["total_listings"],
            active_listings=seller["active_listings"],
            referral_code=seller.get("referral_code"),
            created_at=seller["created_at"]
        )
    )


# Profile endpoints

@router.get("/me", response_model=SellerResponse)
async def get_current_seller_profile(
    current_seller: Dict[str, Any] = Depends(get_current_seller)
):
    """Get current seller's profile."""

    return SellerResponse(
        id=current_seller["id"],
        email=current_seller["email"],
        full_name=current_seller["full_name"],
        business_name=current_seller.get("business_name"),
        location=current_seller["location"],
        is_verified=current_seller["is_verified"],
        role=current_seller["role"],
        total_listings=current_seller["total_listings"],
        active_listings=current_seller["active_listings"],
        referral_code=current_seller.get("referral_code"),
        created_at=current_seller["created_at"]
    )


@router.patch("/me", response_model=SellerResponse)
async def update_seller_profile(
    updates: SellerUpdate,
    current_seller: Dict[str, Any] = Depends(get_current_seller)
):
    """Update current seller's profile."""

    supabase = get_supabase_client()

    # Build update data dictionary with only provided fields
    update_data = {}
    if updates.full_name is not None:
        update_data["full_name"] = updates.full_name
    if updates.business_name is not None:
        update_data["business_name"] = updates.business_name
    if updates.phone is not None:
        update_data["phone"] = updates.phone
    if updates.location is not None:
        update_data["location"] = updates.location

    # Add updated_at timestamp
    update_data["updated_at"] = datetime.utcnow().isoformat()

    # Update seller in Supabase
    update_response = supabase.table("sellers").update(
        update_data
    ).eq("id", current_seller["id"]).execute()

    if not update_response.data or len(update_response.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update seller profile"
        )

    updated_seller = update_response.data[0]

    return SellerResponse(
        id=updated_seller["id"],
        email=updated_seller["email"],
        full_name=updated_seller["full_name"],
        business_name=updated_seller.get("business_name"),
        location=updated_seller["location"],
        is_verified=updated_seller["is_verified"],
        role=updated_seller["role"],
        total_listings=updated_seller["total_listings"],
        active_listings=updated_seller["active_listings"],
        referral_code=updated_seller.get("referral_code"),
        created_at=updated_seller["created_at"]
    )


# Admin endpoints

@router.get("/all", response_model=list[SellerResponse])
async def list_all_sellers(
    skip: int = 0,
    limit: int = 100,
    current_admin: Dict[str, Any] = Depends(get_current_admin)
):
    """List all sellers (admin only)."""

    supabase = get_supabase_client()

    # Query sellers with pagination using range
    # Supabase uses range(start, end) where end is inclusive
    # So for skip=0, limit=10: range(0, 9) returns 10 items
    end = skip + limit - 1
    response = supabase.table("sellers").select("*").range(skip, end).execute()

    if not response.data:
        return []

    return [
        SellerResponse(
            id=seller["id"],
            email=seller["email"],
            full_name=seller["full_name"],
            business_name=seller.get("business_name"),
            location=seller["location"],
            is_verified=seller["is_verified"],
            role=seller["role"],
            total_listings=seller["total_listings"],
            active_listings=seller["active_listings"],
            referral_code=seller.get("referral_code"),
            created_at=seller["created_at"]
        )
        for seller in response.data
    ]


@router.patch("/{seller_id}/verify", response_model=SellerResponse)
async def verify_seller(
    seller_id: str,  # UUID
    current_admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Verify a seller account (admin only)."""

    supabase = get_supabase_client()

    # Check if seller exists
    seller_response = supabase.table("sellers").select("*").eq("id", seller_id).execute()

    if not seller_response.data or len(seller_response.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seller not found"
        )

    # Update seller verification status
    update_response = supabase.table("sellers").update({
        "is_verified": True,
        "updated_at": datetime.utcnow().isoformat()
    }).eq("id", seller_id).execute()

    if not update_response.data or len(update_response.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify seller"
        )

    verified_seller = update_response.data[0]

    return SellerResponse(
        id=verified_seller["id"],
        email=verified_seller["email"],
        full_name=verified_seller["full_name"],
        business_name=verified_seller.get("business_name"),
        location=verified_seller["location"],
        is_verified=verified_seller["is_verified"],
        role=verified_seller["role"],
        total_listings=verified_seller["total_listings"],
        active_listings=verified_seller["active_listings"],
        referral_code=verified_seller.get("referral_code"),
        created_at=verified_seller["created_at"]
    )
