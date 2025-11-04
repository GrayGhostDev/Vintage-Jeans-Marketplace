from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Seller(SQLModel, table=True):
    """Seller account model with OAuth integrations and profile data."""

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: str

    # Profile information
    business_name: Optional[str] = None
    phone: Optional[str] = None
    location: str  # City, Country for analytics

    # Status and permissions
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    role: str = Field(default="seller")  # seller, admin

    # OAuth tokens for marketplace integrations (stored as JSON)
    ebay_access_token: Optional[str] = None
    ebay_refresh_token: Optional[str] = None
    ebay_token_expires_at: Optional[datetime] = None

    etsy_access_token: Optional[str] = None
    etsy_refresh_token: Optional[str] = None
    etsy_token_expires_at: Optional[datetime] = None

    whatnot_access_token: Optional[str] = None
    whatnot_refresh_token: Optional[str] = None
    whatnot_token_expires_at: Optional[datetime] = None

    # Metrics
    total_listings: int = Field(default=0)
    active_listings: int = Field(default=0)
    total_sales: int = Field(default=0)
    total_revenue: float = Field(default=0.0)

    # Referral system
    referral_code: Optional[str] = Field(unique=True, index=True)
    referred_by: Optional[int] = Field(default=None, foreign_key="seller.id")

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "email": "seller@example.com",
                "full_name": "Jane Doe",
                "business_name": "Vintage Finds Co",
                "location": "Los Angeles, USA",
                "role": "seller"
            }
        }
