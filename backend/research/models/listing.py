from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class PlatformEnum(str, Enum):
    """Supported marketplace platforms."""
    MANUAL = "manual"
    EBAY = "ebay"
    ETSY = "etsy"
    WHATNOT = "whatnot"
    DEPOP = "depop"
    POSHMARK = "poshmark"
    GRAILED = "grailed"

class ListingStatus(str, Enum):
    """Listing lifecycle status."""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    ACTIVE = "active"
    SOLD = "sold"
    INACTIVE = "inactive"
    REJECTED = "rejected"

class ConditionGrade(str, Enum):
    """Condition grading system."""
    NEW_WITH_TAGS = "new_with_tags"
    EXCELLENT = "excellent"
    VERY_GOOD = "very_good"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"

class Listing(SQLModel, table=True):
    """Normalized listing model across all platforms."""

    id: Optional[int] = Field(default=None, primary_key=True)
    seller_id: int = Field(foreign_key="seller.id", index=True)

    # Platform information
    platform: PlatformEnum = Field(index=True)
    platform_listing_id: Optional[str] = Field(index=True)  # External ID from platform
    platform_url: Optional[str] = None

    # Basic listing information
    title: str = Field(max_length=200)
    description: str

    # Product attributes
    brand: str = Field(index=True)  # Levi's, Wrangler, Lee, etc.
    decade: Optional[str] = Field(index=True)  # 1950s, 1960s, 1970s, etc.
    year: Optional[int] = None
    model: Optional[str] = None  # 501, 505, etc.

    # Sizing
    waist_size: Optional[int] = None
    inseam_length: Optional[int] = None
    size_label: Optional[str] = None  # "32x34", "M", "L"

    # Condition
    condition: ConditionGrade = Field(index=True)
    condition_notes: Optional[str] = None

    # Material and features
    material: Optional[str] = None  # "100% cotton denim", "selvedge denim"
    wash: Optional[str] = None  # "Dark wash", "Light wash", "Distressed"
    features: Optional[str] = None  # JSON string of features

    # Pricing
    price: float = Field(ge=0)
    currency: str = Field(default="USD")
    purchase_price: Optional[float] = None  # For ROI calculation

    # Shipping
    shipping_cost: float = Field(default=0.0)
    ships_from: Optional[str] = None  # Location
    ships_to: Optional[str] = None  # "Worldwide", "US only", etc.

    # Images
    primary_image_url: Optional[str] = None
    image_urls: Optional[str] = None  # JSON array of image URLs

    # Status and workflow
    status: ListingStatus = Field(default=ListingStatus.PENDING_APPROVAL, index=True)
    approved_by: Optional[int] = Field(default=None, foreign_key="seller.id")
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None

    # Metrics
    views: int = Field(default=0)
    favorites: int = Field(default=0)
    sale_price: Optional[float] = None
    sold_at: Optional[datetime] = None
    sold_to_country: Optional[str] = None  # For geographic analysis

    # Provenance and story (for marketing)
    provenance: Optional[str] = None  # History/story of the jeans
    is_featured: bool = Field(default=False)  # Featured in Fresh Finds Flow

    # SEO and discovery
    tags: Optional[str] = None  # JSON array of tags
    category: Optional[str] = None

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_synced_at: Optional[datetime] = None  # Last sync from platform

    class Config:
        json_schema_extra = {
            "example": {
                "seller_id": 1,
                "platform": "ebay",
                "title": "Vintage Levi's 501 Jeans 1950s Selvedge Denim",
                "description": "Rare 1950s Levi's 501 with original selvedge...",
                "brand": "Levi's",
                "decade": "1950s",
                "model": "501",
                "waist_size": 32,
                "inseam_length": 34,
                "condition": "very_good",
                "price": 450.00,
                "currency": "USD",
                "purchase_price": 50.00,
                "status": "pending_approval"
            }
        }
