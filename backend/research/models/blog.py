from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class BlogStatus(str, Enum):
    """Blog post status."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class BlogCategory(str, Enum):
    """Blog post categories."""
    SELLING_TIPS = "selling_tips"
    VINTAGE_GUIDES = "vintage_guides"
    MARKET_INSIGHTS = "market_insights"
    COLLECTOR_STORIES = "collector_stories"
    SUSTAINABILITY = "sustainability"

class BlogPost(SQLModel, table=True):
    """Blog post model for SEO and content marketing."""

    id: Optional[int] = Field(default=None, primary_key=True)

    # Content
    title: str = Field(max_length=200, index=True)
    slug: str = Field(max_length=250, unique=True, index=True)
    excerpt: str  # Short summary for listings
    content: str  # Full article content (Markdown or HTML)

    # SEO
    meta_title: Optional[str] = Field(max_length=60)  # Optimized for search
    meta_description: Optional[str] = Field(max_length=160)
    meta_keywords: Optional[str] = None  # Comma-separated keywords
    featured_image_url: Optional[str] = None
    featured_image_alt: Optional[str] = None

    # Organization
    category: BlogCategory = Field(index=True)
    tags: Optional[str] = None  # JSON array of tags
    author: str = Field(default="Vintage Jeans Team")
    author_id: Optional[int] = Field(default=None, foreign_key="seller.id")

    # Publishing
    status: BlogStatus = Field(default=BlogStatus.DRAFT, index=True)
    published_at: Optional[datetime] = None
    featured: bool = Field(default=False)  # Show on homepage

    # Analytics
    view_count: int = Field(default=0)
    read_time_minutes: int = Field(default=5)  # Estimated read time

    # Internal linking (JSON array of related post IDs or listing IDs)
    related_posts: Optional[str] = None
    related_listings: Optional[str] = None

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "title": "How to Sell Vintage Jeans Online in 2025",
                "slug": "how-to-sell-vintage-jeans-online-2025",
                "excerpt": "Complete guide to selling vintage denim online with maximum ROI",
                "meta_title": "How to Sell Vintage Jeans Online | 2025 Guide",
                "meta_description": "Learn how to sell vintage jeans for top dollar. Expert tips on pricing, platforms, and finding buyers who pay premium for rare Levi's.",
                "meta_keywords": "sell vintage jeans, how to sell vintage denim, vintage jeans pricing, sell Levi's 501",
                "category": "selling_tips",
                "status": "published",
                "featured": True
            }
        }
