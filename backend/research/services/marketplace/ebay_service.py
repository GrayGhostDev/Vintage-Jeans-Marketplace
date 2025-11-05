"""
eBay API integration service for vintage jeans marketplace tracking.

This service uses the eBay REST API to:
- Search for vintage jeans listings
- Monitor pricing trends
- Track seller activity
- Analyze market data

API Documentation: https://developer.ebay.com/
Package: ebay-rest v1.0.14
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from research.db.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)


class eBayService:
    """Service for interacting with eBay API."""

    def __init__(self):
        """Initialize eBay service with credentials from environment."""
        self.client_id = os.getenv("EBAY_CLIENT_ID")
        self.client_secret = os.getenv("EBAY_CLIENT_SECRET")
        self.environment = os.getenv("EBAY_ENVIRONMENT", "sandbox")  # 'sandbox' or 'production'
        self.redirect_uri = os.getenv("EBAY_REDIRECT_URI")

        # Validate credentials
        if not self.client_id or not self.client_secret:
            logger.warning("eBay credentials not configured. Set EBAY_CLIENT_ID and EBAY_CLIENT_SECRET.")

        self.access_token = None
        self.token_expires_at = None
        self.supabase = get_supabase_client()

    def _get_access_token(self) -> str:
        """
        Get OAuth access token for eBay API.

        Uses Client Credentials flow for application-level access.
        Caches token until expiration.

        Returns:
            str: Valid access token
        """
        # Check if cached token is still valid
        if self.access_token and self.token_expires_at:
            if datetime.now() < self.token_expires_at:
                return self.access_token

        # Import here to avoid errors if package not installed
        try:
            from ebay_rest import API, Environment
        except ImportError:
            raise ImportError(
                "ebay-rest package not installed. Run: pip install ebay-rest>=1.0.14"
            )

        try:
            # Initialize eBay API client
            env = Environment.SANDBOX if self.environment == "sandbox" else Environment.PRODUCTION
            api = API(
                application_id=self.client_id,
                application_secret=self.client_secret,
                environment=env
            )

            # Get application token (no user auth required)
            api.get_application_token()
            self.access_token = api.access_token

            # Cache token for 2 hours (eBay tokens typically expire in 2 hours)
            self.token_expires_at = datetime.now() + timedelta(hours=2)

            logger.info(f"eBay access token obtained, expires at {self.token_expires_at}")
            return self.access_token

        except Exception as e:
            logger.error(f"Failed to get eBay access token: {e}")
            raise

    def search_vintage_jeans(
        self,
        keywords: str = "vintage jeans",
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for vintage jeans listings on eBay.

        Args:
            keywords: Search keywords (default: "vintage jeans")
            limit: Maximum number of results (default: 100, max: 200)
            filters: Optional filters (price_min, price_max, condition, size, brand)

        Returns:
            List of listing dictionaries with standardized fields
        """
        try:
            from ebay_rest import API, Environment
        except ImportError:
            logger.error("ebay-rest package not installed")
            return []

        try:
            # Get access token
            token = self._get_access_token()

            # Initialize API
            env = Environment.SANDBOX if self.environment == "sandbox" else Environment.PRODUCTION
            api = API(
                application_id=self.client_id,
                application_secret=self.client_secret,
                environment=env
            )
            api.access_token = token

            # Build search query
            filters = filters or {}

            # Search parameters
            search_params = {
                "q": keywords,
                "limit": min(limit, 200),  # eBay max is 200
                "filter": []
            }

            # Add price filter
            if filters.get("price_min") or filters.get("price_max"):
                price_filter = "price:["
                price_filter += str(filters.get("price_min", "")) + ".."
                price_filter += str(filters.get("price_max", "")) + "]"
                search_params["filter"].append(price_filter)

            # Add condition filter (NEW, USED_EXCELLENT, USED_GOOD, etc.)
            if filters.get("condition"):
                search_params["filter"].append(f"condition:{filters['condition']}")

            # Execute search using Browse API
            response = api.buy_browse.search(**search_params)

            # Parse results
            listings = []
            if response and hasattr(response, "itemSummaries"):
                for item in response.itemSummaries or []:
                    listing = self._parse_ebay_listing(item)
                    listings.append(listing)

            logger.info(f"Found {len(listings)} eBay listings for '{keywords}'")
            return listings

        except Exception as e:
            logger.error(f"eBay search failed: {e}")
            return []

    def _parse_ebay_listing(self, item: Any) -> Dict[str, Any]:
        """
        Parse eBay item into standardized listing format.

        Args:
            item: eBay item object from API response

        Returns:
            Standardized listing dictionary
        """
        # Extract basic info
        item_id = getattr(item, "itemId", "")
        title = getattr(item, "title", "")
        price_obj = getattr(item, "price", None)
        price = float(price_obj.value) if price_obj and hasattr(price_obj, "value") else None
        currency = price_obj.currency if price_obj and hasattr(price_obj, "currency") else "USD"

        # Extract image URLs
        image = getattr(item, "image", None)
        thumbnail_url = image.imageUrl if image and hasattr(image, "imageUrl") else None
        additional_images = getattr(item, "additionalImages", [])
        image_urls = [img.imageUrl for img in additional_images if hasattr(img, "imageUrl")]
        if thumbnail_url and thumbnail_url not in image_urls:
            image_urls.insert(0, thumbnail_url)

        # Extract seller info
        seller = getattr(item, "seller", None)
        seller_username = seller.username if seller and hasattr(seller, "username") else None
        seller_rating = seller.feedbackPercentage if seller and hasattr(seller, "feedbackPercentage") else None

        # Extract condition
        condition_obj = getattr(item, "condition", None)
        condition = condition_obj.conditionDisplayName if condition_obj and hasattr(condition_obj, "conditionDisplayName") else None

        # Extract location
        item_location = getattr(item, "itemLocation", None)
        seller_location = None
        if item_location and hasattr(item_location, "country"):
            seller_location = getattr(item_location, "country", None)

        # Build item URL
        item_web_url = getattr(item, "itemWebUrl", f"https://www.ebay.com/itm/{item_id}")

        # Return standardized format
        return {
            "platform": "ebay",
            "external_id": item_id,
            "url": item_web_url,
            "title": title,
            "description": None,  # Description requires separate API call
            "price": price,
            "currency": currency,
            "condition": condition,
            "size": None,  # Needs parsing from title/description
            "brand": None,  # Needs parsing from title/description
            "waist_size": None,
            "inseam_length": None,
            "style": None,
            "wash": None,
            "era": None,
            "image_urls": image_urls,
            "thumbnail_url": thumbnail_url,
            "seller_username": seller_username,
            "seller_rating": float(seller_rating) / 100.0 if seller_rating else None,
            "seller_location": seller_location,
            "status": "active",
            "listed_at": datetime.now(),  # eBay doesn't always provide listing date
            "view_count": 0,
            "watch_count": 0,
            "favorite_count": 0,
            "ai_tags": [],
            "ai_summary": None,
            "trend_score": None,
            "raw_data": {
                "itemId": item_id,
                "title": title,
                "price": {"value": price, "currency": currency},
                "condition": condition,
                "seller": {
                    "username": seller_username,
                    "feedbackPercentage": seller_rating
                }
            }
        }

    def save_listings_to_db(self, listings: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Save eBay listings to Supabase database.

        Args:
            listings: List of parsed listings

        Returns:
            Dictionary with counts: {"added": 5, "updated": 3, "errors": 0}
        """
        added = 0
        updated = 0
        errors = 0

        for listing in listings:
            try:
                # Check if listing already exists
                existing = self.supabase.table("marketplace_listings").select("id").eq(
                    "platform", "ebay"
                ).eq(
                    "external_id", listing["external_id"]
                ).execute()

                if existing.data and len(existing.data) > 0:
                    # Update existing listing
                    listing["updated_at"] = datetime.now().isoformat()
                    listing["last_synced_at"] = datetime.now().isoformat()

                    self.supabase.table("marketplace_listings").update(listing).eq(
                        "id", existing.data[0]["id"]
                    ).execute()
                    updated += 1
                else:
                    # Insert new listing
                    listing["created_at"] = datetime.now().isoformat()
                    listing["updated_at"] = datetime.now().isoformat()
                    listing["last_synced_at"] = datetime.now().isoformat()

                    self.supabase.table("marketplace_listings").insert(listing).execute()
                    added += 1

            except Exception as e:
                logger.error(f"Failed to save eBay listing {listing.get('external_id')}: {e}")
                errors += 1

        logger.info(f"eBay listings saved: {added} added, {updated} updated, {errors} errors")
        return {"added": added, "updated": updated, "errors": errors}

    def sync_listings(
        self,
        keywords: str = "vintage jeans",
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Complete sync operation: search and save listings.

        Args:
            keywords: Search keywords
            limit: Maximum results
            filters: Optional filters

        Returns:
            Sync statistics dictionary
        """
        logger.info(f"Starting eBay sync for '{keywords}' (limit: {limit})")

        # Search listings
        listings = self.search_vintage_jeans(keywords, limit, filters)

        # Save to database
        stats = self.save_listings_to_db(listings)
        stats["listings_found"] = len(listings)

        logger.info(f"eBay sync complete: {stats}")
        return stats


# Convenience function
def sync_ebay_listings(keywords: str = "vintage jeans", limit: int = 100) -> Dict[str, Any]:
    """
    Convenience function to sync eBay listings.

    Args:
        keywords: Search keywords
        limit: Maximum results

    Returns:
        Sync statistics
    """
    service = eBayService()
    return service.sync_listings(keywords, limit)
