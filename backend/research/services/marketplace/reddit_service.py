"""
Reddit API integration service for vintage jeans trend tracking.

This service uses PRAW (Python Reddit API Wrapper) to:
- Monitor relevant subreddits (r/rawdenim, r/vintagefashion, r/ThriftStoreHauls)
- Track marketplace posts and buy/sell threads
- Analyze community discussions and trends
- Identify popular brands and styles

API Documentation: https://praw.readthedocs.io/
Package: praw v7.7.1
"""

import os
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from research.db.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)


class RedditService:
    """Service for interacting with Reddit API via PRAW."""

    # Target subreddits for vintage jeans
    RELEVANT_SUBREDDITS = [
        "rawdenim",
        "vintagefashion",
        "ThriftStoreHauls",
        "frugalmalefashion",
        "malefashionadvice",
        "femalefashionadvice",
        "Flipping",
        "VintageFashion"
    ]

    def __init__(self):
        """Initialize Reddit service with credentials from environment."""
        self.client_id = os.getenv("REDDIT_CLIENT_ID")
        self.client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        self.user_agent = os.getenv("REDDIT_USER_AGENT", "VintageJeansMarketplace/1.0")
        self.username = os.getenv("REDDIT_USERNAME")  # Optional for read-only
        self.password = os.getenv("REDDIT_PASSWORD")  # Optional for read-only

        # Validate credentials
        if not self.client_id or not self.client_secret:
            logger.warning("Reddit credentials not configured. Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET.")

        self.reddit = None
        self.supabase = get_supabase_client()

    def _get_reddit_client(self):
        """
        Get authenticated Reddit client (PRAW instance).

        Returns:
            praw.Reddit: Authenticated Reddit client
        """
        if self.reddit:
            return self.reddit

        # Import here to avoid errors if package not installed
        try:
            import praw
        except ImportError:
            raise ImportError(
                "praw package not installed. Run: pip install praw>=7.7.1"
            )

        try:
            # Initialize PRAW
            if self.username and self.password:
                # Authenticated mode (can post/comment)
                self.reddit = praw.Reddit(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    user_agent=self.user_agent,
                    username=self.username,
                    password=self.password
                )
                logger.info(f"Reddit client initialized (authenticated as u/{self.username})")
            else:
                # Read-only mode (no username/password)
                self.reddit = praw.Reddit(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    user_agent=self.user_agent
                )
                logger.info("Reddit client initialized (read-only mode)")

            return self.reddit

        except Exception as e:
            logger.error(f"Failed to initialize Reddit client: {e}")
            raise

    def search_marketplace_posts(
        self,
        subreddit: str = "rawdenim",
        keywords: str = "vintage jeans",
        limit: int = 100,
        time_filter: str = "week"
    ) -> List[Dict[str, Any]]:
        """
        Search for marketplace-related posts in a subreddit.

        Args:
            subreddit: Subreddit name (default: "rawdenim")
            keywords: Search keywords (default: "vintage jeans")
            limit: Maximum number of posts (default: 100)
            time_filter: Time filter (hour, day, week, month, year, all)

        Returns:
            List of post dictionaries
        """
        try:
            reddit = self._get_reddit_client()
            subreddit_obj = reddit.subreddit(subreddit)

            # Search for posts
            posts = []
            for submission in subreddit_obj.search(keywords, time_filter=time_filter, limit=limit):
                post = self._parse_reddit_post(submission)
                posts.append(post)

            logger.info(f"Found {len(posts)} posts in r/{subreddit} for '{keywords}'")
            return posts

        except Exception as e:
            logger.error(f"Reddit search failed for r/{subreddit}: {e}")
            return []

    def get_buy_sell_threads(
        self,
        subreddit: str = "rawdenim",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get Buy/Sell/Trade threads from a subreddit.

        Args:
            subreddit: Subreddit name
            limit: Maximum number of threads

        Returns:
            List of thread dictionaries with comments
        """
        try:
            reddit = self._get_reddit_client()
            subreddit_obj = reddit.subreddit(subreddit)

            # Search for BST threads
            threads = []
            for submission in subreddit_obj.search("buy sell trade", time_filter="month", limit=limit):
                if "buy" in submission.title.lower() or "sell" in submission.title.lower():
                    thread = self._parse_bst_thread(submission)
                    threads.append(thread)

            logger.info(f"Found {len(threads)} BST threads in r/{subreddit}")
            return threads

        except Exception as e:
            logger.error(f"Failed to get BST threads from r/{subreddit}: {e}")
            return []

    def monitor_multiple_subreddits(
        self,
        keywords: str = "vintage jeans",
        limit_per_subreddit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Monitor multiple relevant subreddits for vintage jeans posts.

        Args:
            keywords: Search keywords
            limit_per_subreddit: Limit per subreddit

        Returns:
            Combined list of posts from all subreddits
        """
        all_posts = []

        for subreddit_name in self.RELEVANT_SUBREDDITS:
            try:
                posts = self.search_marketplace_posts(
                    subreddit=subreddit_name,
                    keywords=keywords,
                    limit=limit_per_subreddit,
                    time_filter="week"
                )
                all_posts.extend(posts)
            except Exception as e:
                logger.error(f"Failed to search r/{subreddit_name}: {e}")
                continue

        logger.info(f"Total posts found across {len(self.RELEVANT_SUBREDDITS)} subreddits: {len(all_posts)}")
        return all_posts

    def _parse_reddit_post(self, submission) -> Dict[str, Any]:
        """
        Parse Reddit submission into standardized format.

        Args:
            submission: PRAW Submission object

        Returns:
            Standardized post dictionary
        """
        # Extract price from title or text using regex
        price = self._extract_price(submission.title + " " + submission.selftext)

        # Check if it's a marketplace/sale post
        is_marketplace = self._is_marketplace_post(submission)

        # Extract images
        image_urls = []
        thumbnail_url = None

        if hasattr(submission, "url") and submission.url:
            if any(ext in submission.url.lower() for ext in [".jpg", ".jpeg", ".png", ".gif"]):
                image_urls.append(submission.url)
                thumbnail_url = submission.url
            elif hasattr(submission, "preview") and submission.preview:
                # Extract preview images
                try:
                    images = submission.preview.get("images", [])
                    if images and len(images) > 0:
                        source = images[0].get("source", {})
                        if "url" in source:
                            image_url = source["url"].replace("&amp;", "&")
                            image_urls.append(image_url)
                            thumbnail_url = submission.thumbnail if hasattr(submission, "thumbnail") else image_url
                except:
                    pass

        # Build post URL
        post_url = f"https://reddit.com{submission.permalink}"

        # Return standardized format
        return {
            "platform": "reddit",
            "external_id": submission.id,
            "url": post_url,
            "title": submission.title,
            "description": submission.selftext[:500] if submission.selftext else None,  # Limit description
            "price": price,
            "currency": "USD",  # Reddit posts typically in USD
            "condition": None,  # Needs parsing
            "size": None,
            "brand": self._extract_brand(submission.title + " " + submission.selftext),
            "waist_size": None,
            "inseam_length": None,
            "style": None,
            "wash": None,
            "era": None,
            "image_urls": image_urls,
            "thumbnail_url": thumbnail_url,
            "seller_username": submission.author.name if submission.author else "[deleted]",
            "seller_rating": None,  # Reddit doesn't have seller ratings
            "seller_location": None,
            "status": "active" if is_marketplace else "removed",
            "listed_at": datetime.fromtimestamp(submission.created_utc),
            "view_count": 0,  # Reddit doesn't provide view count
            "watch_count": submission.num_comments,  # Use comments as engagement metric
            "favorite_count": submission.score,  # Upvotes
            "ai_tags": [],
            "ai_summary": None,
            "trend_score": self._calculate_engagement_score(submission),
            "raw_data": {
                "id": submission.id,
                "title": submission.title,
                "author": submission.author.name if submission.author else None,
                "subreddit": submission.subreddit.display_name,
                "score": submission.score,
                "num_comments": submission.num_comments,
                "upvote_ratio": submission.upvote_ratio,
                "created_utc": submission.created_utc,
                "is_marketplace": is_marketplace
            }
        }

    def _parse_bst_thread(self, submission) -> Dict[str, Any]:
        """
        Parse Buy/Sell/Trade thread and extract listings from comments.

        Args:
            submission: PRAW Submission object

        Returns:
            Thread data with parsed comments
        """
        # Get all comments
        submission.comments.replace_more(limit=0)  # Remove "load more comments"
        comments = []

        for comment in submission.comments.list():
            if hasattr(comment, "body") and comment.body:
                # Parse listing from comment
                listing = self._parse_bst_comment(comment, submission)
                if listing:
                    comments.append(listing)

        return {
            "thread_id": submission.id,
            "title": submission.title,
            "url": f"https://reddit.com{submission.permalink}",
            "subreddit": submission.subreddit.display_name,
            "created_at": datetime.fromtimestamp(submission.created_utc),
            "listings": comments[:50]  # Limit to 50 listings per thread
        }

    def _parse_bst_comment(self, comment, parent_submission) -> Optional[Dict[str, Any]]:
        """
        Parse a BST comment for listing information.

        Args:
            comment: PRAW Comment object
            parent_submission: Parent submission

        Returns:
            Listing dictionary or None if not a listing
        """
        # Check if comment contains price
        price = self._extract_price(comment.body)
        if not price:
            return None

        # Extract brand
        brand = self._extract_brand(comment.body)

        # Return listing
        return {
            "platform": "reddit",
            "external_id": f"{parent_submission.id}_{comment.id}",
            "url": f"https://reddit.com{comment.permalink}",
            "title": f"BST: {brand or 'Vintage Jeans'} - ${price}",
            "description": comment.body[:500],
            "price": price,
            "currency": "USD",
            "brand": brand,
            "seller_username": comment.author.name if comment.author else "[deleted]",
            "listed_at": datetime.fromtimestamp(comment.created_utc),
            "favorite_count": comment.score,
            "raw_data": {
                "comment_id": comment.id,
                "parent_id": parent_submission.id,
                "body": comment.body,
                "score": comment.score
            }
        }

    def _extract_price(self, text: str) -> Optional[float]:
        """Extract price from text using regex."""
        # Match $123, $123.45, $1,234.56
        price_pattern = r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
        matches = re.findall(price_pattern, text)

        if matches:
            # Return first price found, remove commas
            try:
                return float(matches[0].replace(",", ""))
            except:
                return None
        return None

    def _extract_brand(self, text: str) -> Optional[str]:
        """Extract brand name from text."""
        brands = [
            "Levi's", "Levis", "Lee", "Wrangler", "Calvin Klein",
            "Diesel", "G-Star", "Nudie", "APC", "Naked & Famous",
            "3sixteen", "Iron Heart", "Pure Blue Japan", "Momotaro",
            "Samurai", "Evisu", "Edwin", "Oni", "Studio D'Artisan"
        ]

        text_lower = text.lower()
        for brand in brands:
            if brand.lower() in text_lower:
                return brand

        return None

    def _is_marketplace_post(self, submission) -> bool:
        """Check if post is marketplace/sale related."""
        marketplace_keywords = ["sale", "sell", "selling", "fs", "wts", "$", "price"]
        title_lower = submission.title.lower()

        return any(keyword in title_lower for keyword in marketplace_keywords)

    def _calculate_engagement_score(self, submission) -> float:
        """Calculate engagement score (0-100) based on upvotes and comments."""
        # Weighted formula: 70% upvotes, 30% comments
        upvote_score = min(submission.score / 100.0, 1.0) * 70
        comment_score = min(submission.num_comments / 50.0, 1.0) * 30

        return round(upvote_score + comment_score, 2)

    def save_posts_to_db(self, posts: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Save Reddit posts to Supabase database.

        Args:
            posts: List of parsed posts

        Returns:
            Dictionary with counts
        """
        added = 0
        updated = 0
        errors = 0

        for post in posts:
            try:
                # Check if post already exists
                existing = self.supabase.table("marketplace_listings").select("id").eq(
                    "platform", "reddit"
                ).eq(
                    "external_id", post["external_id"]
                ).execute()

                if existing.data and len(existing.data) > 0:
                    # Update existing post
                    post["updated_at"] = datetime.now().isoformat()
                    post["last_synced_at"] = datetime.now().isoformat()

                    self.supabase.table("marketplace_listings").update(post).eq(
                        "id", existing.data[0]["id"]
                    ).execute()
                    updated += 1
                else:
                    # Insert new post
                    post["created_at"] = datetime.now().isoformat()
                    post["updated_at"] = datetime.now().isoformat()
                    post["last_synced_at"] = datetime.now().isoformat()

                    self.supabase.table("marketplace_listings").insert(post).execute()
                    added += 1

            except Exception as e:
                logger.error(f"Failed to save Reddit post {post.get('external_id')}: {e}")
                errors += 1

        logger.info(f"Reddit posts saved: {added} added, {updated} updated, {errors} errors")
        return {"added": added, "updated": updated, "errors": errors}

    def sync_listings(
        self,
        keywords: str = "vintage jeans",
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Complete sync operation: search and save posts.

        Args:
            keywords: Search keywords
            limit: Maximum results per subreddit

        Returns:
            Sync statistics dictionary
        """
        logger.info(f"Starting Reddit sync for '{keywords}'")

        # Search across multiple subreddits
        posts = self.monitor_multiple_subreddits(keywords, limit_per_subreddit=limit // len(self.RELEVANT_SUBREDDITS))

        # Save to database
        stats = self.save_posts_to_db(posts)
        stats["posts_found"] = len(posts)
        stats["subreddits_monitored"] = len(self.RELEVANT_SUBREDDITS)

        logger.info(f"Reddit sync complete: {stats}")
        return stats


# Convenience function
def sync_reddit_posts(keywords: str = "vintage jeans", limit: int = 100) -> Dict[str, Any]:
    """
    Convenience function to sync Reddit posts.

    Args:
        keywords: Search keywords
        limit: Maximum results

    Returns:
        Sync statistics
    """
    service = RedditService()
    return service.sync_listings(keywords, limit)
