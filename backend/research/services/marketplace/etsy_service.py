"""
Etsy API integration service for vintage jeans marketplace tracking.

This service uses the Etsy API v3 to:
- Search for vintage jeans listings
- Monitor shop activity
- Track pricing and trends
- Analyze vintage clothing market

API Documentation: https://developers.etsy.com/documentation/
Package: etsyv3 v0.2.0
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from research.db.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)


class EtsyService:
    """Service for interacting with Etsy API v3."""

    def __init__(self):
        """Initialize Etsy service with credentials from environment."""
        self.api_key = os.getenv("ETSY_API_KEY")
        self.api_secret = os.getenv("ETSY_API_SECRET")
        self.redirect_uri = os.getenv("ETSY_REDIRECT_URI")

        # Validate credentials
        if not self.api_key or not self.api_secret:
            logger.warning("Etsy credentials not configured. Set ETSY_API_KEY and ETSY_API_SECRET.")

        self.access_token = None
        self.token_expires_at = None
        self.supabase = get_supabase_client()

    def _get_access_token(self) -> str:
        """
        Get OAuth access token for Etsy API.

        Uses OAuth 2.0 for API access.
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
            from etsyv3 import Etsy
        except ImportError:
            raise ImportError(
                "etsyv3 package not installed. Run: pip install etsyv3>=0.2.0"
            )

        try:
            # Initialize Etsy client
            etsy = Etsy(api_key=self.api_key)

            # For public API access, Etsy v3 uses API key directly
            # No OAuth required for read-only public data
            self.access_token = self.api_key

            # Set expiration to 1 year (API keys don't expire)
            self.token_expires_at = datetime.now() + timedelta(days=365)

            logger.info("Etsy API key validated")
            return self.access_token

        except Exception as e:
            logger.error(f"Failed to validate Etsy API key: {e}")
            raise

    def search_vintage_jeans(
        self,
        keywords: str = "vintage jeans",
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for vintage jeans listings on Etsy.

        Args:
            keywords: Search keywords (default: "vintage jeans")
            limit: Maximum number of results (default: 100, max: 100 per request)
            filters: Optional filters (price_min, price_max, category)

        Returns:
            List of listing dictionaries with standardized fields
        """
        try:
            from etsyv3 import Etsy
        except ImportError:
            logger.error("etsyv3 package not installed")
            return []

        try:
            # Get access token
            token = self._get_access_token()

            # Initialize API
            etsy = Etsy(api_key=token)

            # Build search parameters
            filters = filters or {}
            params = {
                "keywords": keywords,
                "limit": min(limit, 100),  # Etsy max is 100 per request
                "sort_on": "score",  # or 'created', 'price'
                "sort_order": "desc"
            }

            # Add price filter
            if filters.get("price_min"):
                params["min_price"] = float(filters["price_min"]) * 100  # Etsy uses cents
            if filters.get("price_max"):
                params["max_price"] = float(filters["price_max"]) * 100

            # Execute search
            response = etsy.find_all_active_listings_by_shop(**params)

            # Parse results
            listings = []
            if response and "results" in response:
                for item in response["results"]:
                    listing = self._parse_etsy_listing(item)
                    listings.append(listing)

                logger.info(f"Found {len(listings)} Etsy listings for '{keywords}'")
            else:
                # Fallback: Try different search method
                logger.warning("find_all_active_listings_by_shop failed, trying alternative")
                listings = self._search_listings_alternative(keywords, limit, filters)

            return listings

        except Exception as e:
            logger.error(f"Etsy search failed: {e}")
            return []

    def _search_listings_alternative(
        self,
        keywords: str,
        limit: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Alternative search method using direct API calls.

        This is a fallback when the etsyv3 package methods don't work as expected.

        Args:
            keywords: Search keywords
            limit: Maximum results
            filters: Optional filters

        Returns:
            List of parsed listings
        """
        import requests

        try:
            # Etsy API v3 endpoint
            url = "https://openapi.etsy.com/v3/application/listings/active"

            headers = {
                "x-api-key": self.api_key
            }

            params = {
                "keywords": keywords,
                "limit": min(limit, 100),
                "sort_on": "score",
                "includes": "Images,Shop"
            }

            # Add filters
            if filters:
                if filters.get("price_min"):
                    params["min_price"] = float(filters["price_min"]) * 100
                if filters.get("price_max"):
                    params["max_price"] = float(filters["price_max"]) * 100

            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()

            data = response.json()
            listings = []

            if "results" in data:
                for item in data["results"]:
                    listing = self._parse_etsy_listing(item)
                    listings.append(listing)

            logger.info(f"Alternative search found {len(listings)} Etsy listings")
            return listings

        except Exception as e:
            logger.error(f"Alternative Etsy search failed: {e}")
            return []

    def _parse_etsy_listing(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse Etsy listing into standardized format.

        Args:
            item: Etsy listing dictionary from API response

        Returns:
            Standardized listing dictionary
        """
        # Extract basic info
        listing_id = item.get("listing_id", "")
        title = item.get("title", "")
        description = item.get("description", "")

        # Price info
        price_data = item.get("price", {})
        if isinstance(price_data, dict):
            price = float(price_data.get("amount", 0)) / price_data.get("divisor", 100)
            currency = price_data.get("currency_code", "USD")
        else:
            price = float(item.get("price", 0))
            currency = item.get("currency_code", "USD")

        # Images
        images = item.get("images", [])
        image_urls = []
        thumbnail_url = None

        if isinstance(images, list) and len(images) > 0:
            # Get first image as thumbnail
            first_image = images[0]
            if isinstance(first_image, dict):
                thumbnail_url = first_image.get("url_570xN") or first_image.get("url_fullxfull")
                image_urls = [img.get("url_fullxfull") or img.get("url_570xN") for img in images if isinstance(img, dict)]
            elif isinstance(first_image, str):
                thumbnail_url = first_image
                image_urls = images

        # Shop info (seller)
        shop_data = item.get("shop", {})
        seller_username = shop_data.get("shop_name") if isinstance(shop_data, dict) else None
        seller_location = shop_data.get("city") if isinstance(shop_data, dict) else None

        # Build listing URL
        url = item.get("url", f"https://www.etsy.com/listing/{listing_id}")

        # Parse creation date
        listed_at = None
        created_timestamp = item.get("created_timestamp")
        if created_timestamp:
            try:
                listed_at = datetime.fromtimestamp(int(created_timestamp))
            except:
                listed_at = datetime.now()

        # Return standardized format
        return {
            "platform": "etsy",
            "external_id": str(listing_id),
            "url": url,
            "title": title,
            "description": description,
            "price": price,
            "currency": currency,
            "condition": "vintage",  # Etsy vintage category
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
            "seller_rating": None,  # Etsy doesn't provide rating in listing API
            "seller_location": seller_location,
            "status": "active",
            "listed_at": listed_at or datetime.now(),
            "view_count": item.get("views", 0),
            "watch_count": item.get("num_favorers", 0),
            "favorite_count": item.get("num_favorers", 0),
            "ai_tags": [],
            "ai_summary": None,
            "trend_score": None,
            "raw_data": item
        }

    def save_listings_to_db(self, listings: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Save Etsy listings to Supabase database.

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
                    "platform", "etsy"
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
                logger.error(f"Failed to save Etsy listing {listing.get('external_id')}: {e}")
                errors += 1

        logger.info(f"Etsy listings saved: {added} added, {updated} updated, {errors} errors")
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
        logger.info(f"Starting Etsy sync for '{keywords}' (limit: {limit})")

        # Search listings
        listings = self.search_vintage_jeans(keywords, limit, filters)

        # Save to database
        stats = self.save_listings_to_db(listings)
        stats["listings_found"] = len(listings)

        logger.info(f"Etsy sync complete: {stats}")
        return stats


# Convenience function
def sync_etsy_listings(keywords: str = "vintage jeans", limit: int = 100) -> Dict[str, Any]:
    """
    Convenience function to sync Etsy listings.

    Args:
        keywords: Search keywords
        limit: Maximum results

    Returns:
        Sync statistics
    """
    service = EtsyService()
    return service.sync_listings(keywords, limit)
