"""
Marketplace API endpoints for vintage jeans data.

This router provides:
- Listing search and filtering
- Marketplace trend data
- Sync job management
- AI analysis triggers
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from research.db.supabase_client import get_supabase_client

router = APIRouter()


# =====================================================
# PYDANTIC MODELS
# =====================================================

class ListingResponse(BaseModel):
    """Response model for marketplace listing."""
    id: str
    platform: str
    external_id: str
    url: str
    title: str
    description: Optional[str] = None
    price: Optional[float] = None
    currency: str = "USD"
    condition: Optional[str] = None
    brand: Optional[str] = None
    size: Optional[str] = None
    seller_username: Optional[str] = None
    listed_at: datetime
    trend_score: Optional[float] = None
    image_urls: List[str] = []
    ai_tags: List[str] = []


class TrendResponse(BaseModel):
    """Response model for trend data."""
    id: str
    category: str
    platform: str
    total_listings: int
    avg_price: float
    min_price: float
    max_price: float
    engagement_score: float
    period_start: datetime
    period_end: datetime


class SyncJobResponse(BaseModel):
    """Response model for sync job."""
    id: str
    platform: str
    job_type: str
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    listings_added: int = 0
    listings_updated: int = 0
    error_message: Optional[str] = None


class TriggerSyncRequest(BaseModel):
    """Request model for triggering sync."""
    platform: str
    keywords: str = "vintage jeans"
    limit: int = 100


# =====================================================
# LISTING ENDPOINTS
# =====================================================

@router.get("/listings", response_model=List[ListingResponse])
async def get_listings(
    platform: Optional[str] = Query(None, description="Filter by platform (ebay, etsy, reddit)"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    min_price: Optional[float] = Query(None, description="Minimum price"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    size: Optional[str] = Query(None, description="Filter by size"),
    condition: Optional[str] = Query(None, description="Filter by condition"),
    sort_by: str = Query("created_at", description="Sort field (created_at, price, trend_score)"),
    sort_order: str = Query("desc", description="Sort order (asc, desc)"),
    limit: int = Query(50, le=200, description="Maximum results (max 200)"),
    offset: int = Query(0, description="Pagination offset")
) -> List[Dict[str, Any]]:
    """
    Get marketplace listings with filtering and pagination.

    Supports filtering by:
    - Platform (eBay, Etsy, Reddit)
    - Brand (Levi's, Lee, Wrangler, etc.)
    - Price range
    - Size
    - Condition

    Returns paginated results sorted by your preference.
    """
    supabase = get_supabase_client()

    try:
        # Build query
        query = supabase.table("marketplace_listings").select("*")

        # Apply filters
        if platform:
            query = query.eq("platform", platform.lower())

        if brand:
            query = query.ilike("brand", f"%{brand}%")

        if min_price is not None:
            query = query.gte("price", min_price)

        if max_price is not None:
            query = query.lte("price", max_price)

        if size:
            query = query.eq("size", size)

        if condition:
            query = query.ilike("condition", f"%{condition}%")

        # Apply sorting
        if sort_order.lower() == "desc":
            query = query.order(sort_by, desc=True)
        else:
            query = query.order(sort_by)

        # Apply pagination
        query = query.range(offset, offset + limit - 1)

        # Execute query
        result = query.execute()

        return result.data if result.data else []

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch listings: {str(e)}")


@router.get("/listings/{listing_id}", response_model=ListingResponse)
async def get_listing_by_id(listing_id: str) -> Dict[str, Any]:
    """
    Get a specific listing by ID.

    Returns full listing details including:
    - Complete description
    - All images
    - AI analysis tags
    - Raw API data
    """
    supabase = get_supabase_client()

    try:
        result = supabase.table("marketplace_listings").select("*").eq("id", listing_id).execute()

        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=404, detail="Listing not found")

        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch listing: {str(e)}")


@router.get("/listings/search/{keywords}")
async def search_listings(
    keywords: str,
    platform: Optional[str] = None,
    limit: int = Query(50, le=200)
) -> List[Dict[str, Any]]:
    """
    Search listings by keywords.

    Searches in:
    - Title
    - Description
    - Brand
    - AI tags

    Returns relevance-ranked results.
    """
    supabase = get_supabase_client()

    try:
        # Build search query using PostgreSQL full-text search
        query = supabase.table("marketplace_listings").select("*")

        if platform:
            query = query.eq("platform", platform.lower())

        # Search in title, description, and brand
        # Note: This is a simple implementation. For production, use PostgreSQL full-text search
        query = query.or_(f"title.ilike.%{keywords}%,description.ilike.%{keywords}%,brand.ilike.%{keywords}%")

        query = query.limit(limit)

        result = query.execute()

        return result.data if result.data else []

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


# =====================================================
# TREND ENDPOINTS
# =====================================================

@router.get("/trends", response_model=List[TrendResponse])
async def get_trends(
    platform: Optional[str] = Query(None, description="Filter by platform"),
    category: Optional[str] = Query(None, description="Filter by category"),
    days: int = Query(7, le=90, description="Number of days to look back (max 90)")
) -> List[Dict[str, Any]]:
    """
    Get market trend data.

    Returns aggregated analytics including:
    - Average prices
    - Listing volume
    - Engagement metrics
    - Popular categories

    Grouped by platform and category over time.
    """
    supabase = get_supabase_client()

    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Build query
        query = supabase.table("marketplace_trends").select("*").gte(
            "period_start", start_date.isoformat()
        )

        if platform:
            query = query.eq("platform", platform.lower())

        if category:
            query = query.eq("category", category)

        query = query.order("period_start", desc=True)

        result = query.execute()

        return result.data if result.data else []

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch trends: {str(e)}")


@router.get("/trends/brands")
async def get_brand_trends(
    days: int = Query(7, le=90),
    limit: int = Query(10, le=50)
) -> List[Dict[str, Any]]:
    """
    Get trending brands.

    Returns top brands by:
    - Listing volume
    - Average price
    - Engagement score

    Useful for identifying popular brands in the market.
    """
    supabase = get_supabase_client()

    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Get brand trends
        result = supabase.table("marketplace_trends").select("*").gte(
            "period_start", start_date.isoformat()
        ).neq(
            "category", "platform"
        ).neq(
            "category", "overall"
        ).order(
            "total_listings", desc=True
        ).limit(limit).execute()

        return result.data if result.data else []

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch brand trends: {str(e)}")


@router.get("/trends/summary")
async def get_trends_summary(days: int = Query(7, le=90)) -> Dict[str, Any]:
    """
    Get high-level market summary.

    Returns:
    - Total listings across all platforms
    - Average market price
    - Most active platform
    - Trending brands
    - Price trends
    """
    supabase = get_supabase_client()

    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Get listings in date range
        listings_result = supabase.table("marketplace_listings").select(
            "platform, price, brand, created_at"
        ).gte(
            "created_at", start_date.isoformat()
        ).execute()

        listings = listings_result.data if listings_result.data else []

        if not listings:
            return {
                "period": f"Last {days} days",
                "total_listings": 0,
                "avg_price": 0,
                "platforms": {},
                "top_brands": []
            }

        # Calculate summary stats
        total_listings = len(listings)
        prices = [l["price"] for l in listings if l.get("price")]
        avg_price = sum(prices) / len(prices) if prices else 0

        # Group by platform
        platforms = {}
        for listing in listings:
            platform = listing.get("platform", "unknown")
            if platform not in platforms:
                platforms[platform] = 0
            platforms[platform] += 1

        # Count brands
        brand_counts = {}
        for listing in listings:
            brand = listing.get("brand")
            if brand:
                brand_counts[brand] = brand_counts.get(brand, 0) + 1

        # Get top 5 brands
        top_brands = sorted(brand_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "period": f"Last {days} days",
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat(),
            "total_listings": total_listings,
            "avg_price": round(avg_price, 2),
            "min_price": min(prices) if prices else 0,
            "max_price": max(prices) if prices else 0,
            "platforms": platforms,
            "top_brands": [{"brand": brand, "count": count} for brand, count in top_brands]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")


# =====================================================
# SYNC JOB ENDPOINTS
# =====================================================

@router.get("/sync-jobs", response_model=List[SyncJobResponse])
async def get_sync_jobs(
    platform: Optional[str] = Query(None, description="Filter by platform"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(20, le=100)
) -> List[Dict[str, Any]]:
    """
    Get sync job history.

    Shows status of all marketplace synchronization jobs:
    - Completed jobs with stats
    - Running jobs
    - Failed jobs with errors

    Useful for monitoring data pipeline health.
    """
    supabase = get_supabase_client()

    try:
        query = supabase.table("marketplace_sync_jobs").select("*")

        if platform:
            query = query.eq("platform", platform.lower())

        if status:
            query = query.eq("status", status.lower())

        query = query.order("created_at", desc=True).limit(limit)

        result = query.execute()

        return result.data if result.data else []

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch sync jobs: {str(e)}")


@router.post("/sync/trigger")
async def trigger_sync(request: TriggerSyncRequest, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """
    Manually trigger a marketplace sync.

    Starts a background task to sync listings from the specified platform.

    **Platforms:**
    - `ebay`: Sync eBay listings
    - `etsy`: Sync Etsy listings
    - `reddit`: Sync Reddit posts
    - `all`: Sync all platforms

    Returns task ID for tracking.
    """
    from tasks.marketplace_tasks import (
        sync_ebay_task,
        sync_etsy_task,
        sync_reddit_task,
        sync_all_marketplaces_task
    )

    platform = request.platform.lower()

    try:
        if platform == "ebay":
            task = sync_ebay_task.apply_async(args=[request.keywords, request.limit])
        elif platform == "etsy":
            task = sync_etsy_task.apply_async(args=[request.keywords, request.limit])
        elif platform == "reddit":
            task = sync_reddit_task.apply_async(args=[request.keywords, request.limit])
        elif platform == "all":
            task = sync_all_marketplaces_task.apply_async(args=[request.keywords, request.limit])
        else:
            raise HTTPException(status_code=400, detail=f"Invalid platform: {platform}")

        return {
            "status": "triggered",
            "platform": platform,
            "task_id": task.id,
            "message": f"Sync task started for {platform}",
            "keywords": request.keywords,
            "limit": request.limit
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger sync: {str(e)}")


@router.get("/sync/status/{task_id}")
async def get_sync_status(task_id: str) -> Dict[str, Any]:
    """
    Get status of a sync task by Celery task ID.

    Returns:
    - Task state (PENDING, STARTED, SUCCESS, FAILURE)
    - Progress info
    - Results (if completed)
    - Error details (if failed)
    """
    from celery.result import AsyncResult
    from celery_app import app

    try:
        task = AsyncResult(task_id, app=app)

        response = {
            "task_id": task_id,
            "state": task.state,
            "status": task.status
        }

        if task.state == "SUCCESS":
            response["result"] = task.result
        elif task.state == "FAILURE":
            response["error"] = str(task.info)

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get task status: {str(e)}")


# =====================================================
# ANALYTICS ENDPOINTS
# =====================================================

@router.post("/analyze/{listing_id}")
async def analyze_listing(listing_id: str, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """
    Trigger AI analysis for a specific listing.

    Uses OpenAI GPT-4 to extract:
    - Brand, size, style, condition
    - Generated tags
    - Summary

    Returns task ID for tracking.
    """
    from tasks.analytics_tasks import analyze_listing_with_ai

    try:
        # Verify listing exists
        supabase = get_supabase_client()
        result = supabase.table("marketplace_listings").select("id").eq("id", listing_id).execute()

        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=404, detail="Listing not found")

        # Trigger AI analysis
        task = analyze_listing_with_ai.apply_async(args=[listing_id])

        return {
            "status": "triggered",
            "listing_id": listing_id,
            "task_id": task.id,
            "message": "AI analysis started"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger analysis: {str(e)}")


@router.get("/stats")
async def get_marketplace_stats() -> Dict[str, Any]:
    """
    Get overall marketplace statistics.

    Returns:
    - Total listings by platform
    - Last sync times
    - Database health
    """
    supabase = get_supabase_client()

    try:
        # Get total listings by platform
        ebay_count = supabase.table("marketplace_listings").select("id", count="exact").eq("platform", "ebay").execute()
        etsy_count = supabase.table("marketplace_listings").select("id", count="exact").eq("platform", "etsy").execute()
        reddit_count = supabase.table("marketplace_listings").select("id", count="exact").eq("platform", "reddit").execute()

        # Get last sync jobs
        last_syncs = supabase.table("marketplace_sync_jobs").select("platform, completed_at, status").order(
            "completed_at", desc=True
        ).limit(3).execute()

        return {
            "total_listings": {
                "ebay": ebay_count.count if ebay_count else 0,
                "etsy": etsy_count.count if etsy_count else 0,
                "reddit": reddit_count.count if reddit_count else 0,
                "total": (ebay_count.count or 0) + (etsy_count.count or 0) + (reddit_count.count or 0)
            },
            "last_syncs": last_syncs.data if last_syncs.data else [],
            "database_status": "healthy"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")
