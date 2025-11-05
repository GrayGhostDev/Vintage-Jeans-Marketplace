"""
Analytics and AI processing Celery tasks.

These tasks handle:
- Trend analysis and aggregation
- AI-powered listing analysis
- Price trend calculations
- Market insights generation
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

from celery_app import app
from research.db.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)


@app.task(name="tasks.analytics_tasks.generate_daily_trends")
def generate_daily_trends() -> Dict[str, Any]:
    """
    Generate daily trend analysis across all marketplaces.

    Analyzes:
    - Average prices by category
    - Popular brands
    - Trending styles
    - Engagement metrics

    Returns:
        Trend statistics dictionary
    """
    logger.info("Generating daily trend analysis")

    supabase = get_supabase_client()

    try:
        # Calculate date range (last 24 hours)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)

        # Get all listings from last 24 hours
        listings_result = supabase.table("marketplace_listings").select("*").gte(
            "created_at", start_date.isoformat()
        ).lte(
            "created_at", end_date.isoformat()
        ).execute()

        listings = listings_result.data if listings_result.data else []

        if not listings:
            logger.info("No listings found for trend analysis")
            return {"status": "no_data"}

        # Calculate trends by platform
        trends_by_platform = _calculate_platform_trends(listings)

        # Calculate trends by brand
        trends_by_brand = _calculate_brand_trends(listings)

        # Calculate overall market trends
        overall_trends = _calculate_overall_trends(listings)

        # Save trends to database
        for platform, trend_data in trends_by_platform.items():
            _save_trend_record(platform, "platform", trend_data, start_date, end_date)

        for brand, trend_data in trends_by_brand.items():
            _save_trend_record("all", brand, trend_data, start_date, end_date)

        _save_trend_record("all", "overall", overall_trends, start_date, end_date)

        result = {
            "status": "completed",
            "period": f"{start_date.isoformat()} to {end_date.isoformat()}",
            "listings_analyzed": len(listings),
            "platforms_analyzed": len(trends_by_platform),
            "brands_identified": len(trends_by_brand)
        }

        logger.info(f"Daily trends generated: {result}")
        return result

    except Exception as e:
        logger.error(f"Failed to generate daily trends: {e}")
        return {"status": "failed", "error": str(e)}


def _calculate_platform_trends(listings: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Calculate trends grouped by platform."""
    trends = {}

    for platform in ["ebay", "etsy", "reddit"]:
        platform_listings = [l for l in listings if l.get("platform") == platform]

        if platform_listings:
            prices = [l.get("price", 0) for l in platform_listings if l.get("price")]

            trends[platform] = {
                "total_listings": len(platform_listings),
                "avg_price": sum(prices) / len(prices) if prices else 0,
                "min_price": min(prices) if prices else 0,
                "max_price": max(prices) if prices else 0,
                "total_sales": 0,  # Would need sold status tracking
                "engagement_score": sum([l.get("trend_score", 0) for l in platform_listings]) / len(platform_listings)
            }

    return trends


def _calculate_brand_trends(listings: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Calculate trends grouped by brand."""
    trends = {}
    brands = {}

    # Group listings by brand
    for listing in listings:
        brand = listing.get("brand")
        if brand:
            if brand not in brands:
                brands[brand] = []
            brands[brand].append(listing)

    # Calculate stats for each brand
    for brand, brand_listings in brands.items():
        prices = [l.get("price", 0) for l in brand_listings if l.get("price")]

        trends[brand] = {
            "total_listings": len(brand_listings),
            "avg_price": sum(prices) / len(prices) if prices else 0,
            "min_price": min(prices) if prices else 0,
            "max_price": max(prices) if prices else 0,
            "engagement_score": sum([l.get("trend_score", 0) for l in brand_listings]) / len(brand_listings)
        }

    return trends


def _calculate_overall_trends(listings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate overall market trends."""
    prices = [l.get("price", 0) for l in listings if l.get("price")]
    engagement_scores = [l.get("trend_score", 0) for l in listings if l.get("trend_score")]

    return {
        "total_listings": len(listings),
        "avg_price": sum(prices) / len(prices) if prices else 0,
        "min_price": min(prices) if prices else 0,
        "max_price": max(prices) if prices else 0,
        "engagement_score": sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0,
        "total_sales": 0
    }


def _save_trend_record(
    platform: str,
    category: str,
    trend_data: Dict[str, Any],
    start_date: datetime,
    end_date: datetime
) -> None:
    """Save trend record to database."""
    supabase = get_supabase_client()

    record = {
        "category": category,
        "platform": platform,
        "total_listings": trend_data.get("total_listings", 0),
        "avg_price": trend_data.get("avg_price", 0),
        "min_price": trend_data.get("min_price", 0),
        "max_price": trend_data.get("max_price", 0),
        "total_sales": trend_data.get("total_sales", 0),
        "engagement_score": trend_data.get("engagement_score", 0),
        "period_start": start_date.isoformat(),
        "period_end": end_date.isoformat(),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

    try:
        # Check if record already exists
        existing = supabase.table("marketplace_trends").select("id").eq(
            "category", category
        ).eq(
            "platform", platform
        ).eq(
            "period_start", start_date.isoformat()
        ).eq(
            "period_end", end_date.isoformat()
        ).execute()

        if existing.data and len(existing.data) > 0:
            # Update existing record
            supabase.table("marketplace_trends").update(record).eq(
                "id", existing.data[0]["id"]
            ).execute()
        else:
            # Insert new record
            supabase.table("marketplace_trends").insert(record).execute()

    except Exception as e:
        logger.error(f"Failed to save trend record for {category}/{platform}: {e}")


@app.task(name="tasks.analytics_tasks.analyze_listing_with_ai")
def analyze_listing_with_ai(listing_id: str) -> Dict[str, Any]:
    """
    Analyze a listing using AI to extract:
    - Brand, size, style, condition from title/description
    - Generate tags and summary
    - Calculate trend score

    Args:
        listing_id: UUID of the listing

    Returns:
        Analysis results dictionary
    """
    import os
    import openai

    logger.info(f"Starting AI analysis for listing {listing_id}")

    supabase = get_supabase_client()

    try:
        # Get listing
        listing_result = supabase.table("marketplace_listings").select("*").eq("id", listing_id).execute()

        if not listing_result.data or len(listing_result.data) == 0:
            logger.error(f"Listing {listing_id} not found")
            return {"status": "not_found"}

        listing = listing_result.data[0]

        # Skip if AI analysis disabled
        if not os.getenv("MARKETPLACE_ENABLE_AI_ANALYSIS", "true").lower() == "true":
            logger.info("AI analysis disabled in configuration")
            return {"status": "disabled"}

        # Initialize OpenAI
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            logger.warning("OpenAI API key not configured")
            return {"status": "no_api_key"}

        # Build prompt
        prompt = f"""
Analyze this vintage jeans listing and extract structured information:

Title: {listing.get('title', '')}
Description: {listing.get('description', '')[:500]}
Price: ${listing.get('price', 0)} {listing.get('currency', 'USD')}

Extract and return JSON with:
- brand: The jeans brand (Levi's, Lee, Wrangler, etc.)
- size: Waist size (e.g., "32")
- inseam_length: Inseam length if mentioned (e.g., "34")
- style: Style name (e.g., "501", "505", "Bootcut")
- wash: Wash type (e.g., "Dark wash", "Stonewash")
- era: Approximate era (e.g., "1990s", "1980s")
- condition: Condition (Excellent, Good, Fair, etc.)
- tags: Array of relevant tags
- summary: One sentence summary
"""

        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4-turbo"),
            messages=[
                {"role": "system", "content": "You are an expert in vintage denim and fashion. Extract structured information from product listings."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        # Parse response
        analysis = response.choices[0].message.content
        import json
        ai_data = json.loads(analysis)

        # Update listing with AI analysis
        update_data = {
            "brand": ai_data.get("brand"),
            "size": ai_data.get("size"),
            "waist_size": int(ai_data.get("size")) if ai_data.get("size") and ai_data.get("size").isdigit() else None,
            "inseam_length": int(ai_data.get("inseam_length")) if ai_data.get("inseam_length") and ai_data.get("inseam_length").isdigit() else None,
            "style": ai_data.get("style"),
            "wash": ai_data.get("wash"),
            "era": ai_data.get("era"),
            "condition": ai_data.get("condition") or listing.get("condition"),
            "ai_tags": ai_data.get("tags", []),
            "ai_summary": ai_data.get("summary"),
            "updated_at": datetime.now().isoformat()
        }

        supabase.table("marketplace_listings").update(update_data).eq("id", listing_id).execute()

        logger.info(f"AI analysis completed for listing {listing_id}")
        return {"status": "completed", "analysis": ai_data}

    except Exception as e:
        logger.error(f"AI analysis failed for listing {listing_id}: {e}")
        return {"status": "failed", "error": str(e)}
