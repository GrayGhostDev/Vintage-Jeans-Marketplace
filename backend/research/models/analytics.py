from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Analytics(SQLModel, table=True):
    """Aggregated analytics and metrics storage."""

    id: Optional[int] = Field(default=None, primary_key=True)

    # Scope of analytics
    metric_type: str = Field(index=True)  # "platform_overview", "seller_performance", "market_trend"
    entity_id: Optional[int] = None  # Seller ID if seller-specific

    # Time period
    period_start: datetime = Field(index=True)
    period_end: datetime
    granularity: str = Field(default="daily")  # hourly, daily, weekly, monthly

    # Platform metrics
    platform: Optional[str] = None  # ebay, etsy, whatnot, or "all"

    # Listing metrics
    total_listings: int = Field(default=0)
    active_listings: int = Field(default=0)
    sold_listings: int = Field(default=0)

    # Price metrics
    avg_listing_price: float = Field(default=0.0)
    median_listing_price: float = Field(default=0.0)
    avg_sale_price: float = Field(default=0.0)
    highest_sale_price: float = Field(default=0.0)

    # Brand/Category breakdown (JSON)
    top_brands: Optional[str] = None  # JSON: [{"brand": "Levi's", "count": 45}, ...]
    top_decades: Optional[str] = None  # JSON: [{"decade": "1950s", "count": 12}, ...]
    top_models: Optional[str] = None  # JSON: [{"model": "501", "count": 32}, ...]

    # ROI metrics
    avg_roi_percentage: float = Field(default=0.0)
    total_profit: float = Field(default=0.0)
    high_roi_opportunities: Optional[str] = None  # JSON array of opportunities

    # Geographic metrics
    top_buyer_countries: Optional[str] = None  # JSON: [{"country": "Japan", "count": 25}, ...]
    top_seller_locations: Optional[str] = None

    # Engagement metrics
    total_views: int = Field(default=0)
    total_favorites: int = Field(default=0)
    avg_time_to_sale_days: Optional[float] = None

    # Trend indicators
    price_trend: Optional[str] = None  # "increasing", "decreasing", "stable"
    demand_trend: Optional[str] = None

    # Timestamps
    calculated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "metric_type": "platform_overview",
                "period_start": "2025-10-01T00:00:00Z",
                "period_end": "2025-10-31T23:59:59Z",
                "granularity": "monthly",
                "platform": "all",
                "total_listings": 342,
                "active_listings": 156,
                "sold_listings": 89,
                "avg_listing_price": 125.50,
                "avg_roi_percentage": 245.3
            }
        }


class Insight(SQLModel, table=True):
    """AI-generated insights and recommendations."""

    id: Optional[int] = Field(default=None, primary_key=True)

    # Scope
    insight_type: str = Field(index=True)  # "market_opportunity", "pricing_suggestion", "trend_alert", "seller_recommendation"
    seller_id: Optional[int] = Field(default=None, foreign_key="seller.id", index=True)

    # Content
    title: str
    summary: str
    detailed_analysis: str  # GPT-5 generated detailed insight

    # Data backing the insight
    confidence_score: float = Field(ge=0.0, le=1.0)  # 0.0 to 1.0
    data_source: str  # "analytics", "gpt5", "manual"
    supporting_data: Optional[str] = None  # JSON with backing metrics

    # Actionability
    action_items: Optional[str] = None  # JSON array of recommended actions
    estimated_impact: Optional[str] = None  # "high", "medium", "low"

    # ROI opportunity specifics
    product_category: Optional[str] = None
    recommended_price_range: Optional[str] = None  # "$100-$150"
    target_market: Optional[str] = None  # "Japan", "Europe"

    # Status
    is_active: bool = Field(default=True)
    is_featured: bool = Field(default=False)  # Show prominently in dashboard

    # User interaction
    viewed_by_seller: bool = Field(default=False)
    acted_upon: bool = Field(default=False)
    feedback: Optional[str] = None  # Seller feedback on usefulness

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None  # Some insights are time-sensitive

    class Config:
        json_schema_extra = {
            "example": {
                "insight_type": "market_opportunity",
                "title": "High Demand for 1950s Levi's 501 in Japan",
                "summary": "Japanese buyers are paying 3-5x premium for authentic 1950s Levi's 501 jeans",
                "detailed_analysis": "Based on recent sales data...",
                "confidence_score": 0.85,
                "data_source": "gpt5",
                "estimated_impact": "high",
                "target_market": "Japan",
                "is_featured": True
            }
        }


class SyncLog(SQLModel, table=True):
    """Track API sync operations for marketplace integrations."""

    id: Optional[int] = Field(default=None, primary_key=True)
    seller_id: int = Field(foreign_key="seller.id", index=True)

    # Sync information
    platform: str = Field(index=True)  # ebay, etsy, whatnot
    sync_type: str  # "full", "incremental", "webhook"

    # Status
    status: str = Field(index=True)  # "started", "in_progress", "completed", "failed", "partial"

    # Results
    items_fetched: int = Field(default=0)
    items_created: int = Field(default=0)
    items_updated: int = Field(default=0)
    items_deleted: int = Field(default=0)
    items_failed: int = Field(default=0)

    # Error tracking
    error_message: Optional[str] = None
    error_details: Optional[str] = None  # JSON with detailed error info

    # Performance
    started_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None

    # API usage
    api_calls_made: int = Field(default=0)
    rate_limit_hit: bool = Field(default=False)

    # Metadata
    sync_metadata: Optional[str] = None  # JSON with additional sync info

    class Config:
        json_schema_extra = {
            "example": {
                "seller_id": 1,
                "platform": "ebay",
                "sync_type": "incremental",
                "status": "completed",
                "items_fetched": 45,
                "items_created": 3,
                "items_updated": 42,
                "duration_seconds": 12.5,
                "api_calls_made": 15
            }
        }
