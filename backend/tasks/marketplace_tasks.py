"""
Marketplace synchronization Celery tasks.

These tasks handle:
- eBay listing synchronization
- Etsy listing synchronization
- Reddit post monitoring
- Sync job tracking and cleanup
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

from celery_app import app
from research.db.supabase_client import get_supabase_client
from research.services.marketplace.ebay_service import sync_ebay_listings
from research.services.marketplace.etsy_service import sync_etsy_listings
from research.services.marketplace.reddit_service import sync_reddit_posts

logger = logging.getLogger(__name__)


@app.task(
    bind=True,
    name="tasks.marketplace_tasks.sync_ebay_task",
    max_retries=int(os.getenv("CELERY_MAX_RETRIES", 3)),
    default_retry_delay=int(os.getenv("CELERY_RETRY_DELAY", 60))
)
def sync_ebay_task(self, keywords: str = "vintage jeans", limit: int = 100) -> Dict[str, Any]:
    """
    Celery task to sync eBay listings.

    Args:
        keywords: Search keywords
        limit: Maximum listings to sync

    Returns:
        Sync statistics dictionary
    """
    logger.info(f"Starting eBay sync task: {keywords} (limit: {limit})")

    # Create sync job record
    supabase = get_supabase_client()
    job_data = {
        "platform": "ebay",
        "job_type": "incremental_sync",
        "status": "running",
        "started_at": datetime.now().isoformat(),
        "celery_task_id": self.request.id
    }

    try:
        # Insert job record
        job_result = supabase.table("marketplace_sync_jobs").insert(job_data).execute()
        job_id = job_result.data[0]["id"] if job_result.data else None

        # Execute sync
        start_time = datetime.now()
        stats = sync_ebay_listings(keywords, limit)
        duration = (datetime.now() - start_time).total_seconds()

        # Update job record with results
        if job_id:
            update_data = {
                "status": "completed",
                "completed_at": datetime.now().isoformat(),
                "duration_seconds": int(duration),
                "listings_processed": stats.get("listings_found", 0),
                "listings_added": stats.get("added", 0),
                "listings_updated": stats.get("updated", 0),
            }
            supabase.table("marketplace_sync_jobs").update(update_data).eq("id", job_id).execute()

        logger.info(f"eBay sync completed: {stats}")
        return stats

    except Exception as e:
        logger.error(f"eBay sync failed: {e}")

        # Update job record with error
        if job_id:
            error_data = {
                "status": "failed",
                "completed_at": datetime.now().isoformat(),
                "error_message": str(e),
                "error_details": {"exception_type": type(e).__name__}
            }
            supabase.table("marketplace_sync_jobs").update(error_data).eq("id", job_id).execute()

        # Retry task
        raise self.retry(exc=e)


@app.task(
    bind=True,
    name="tasks.marketplace_tasks.sync_etsy_task",
    max_retries=int(os.getenv("CELERY_MAX_RETRIES", 3)),
    default_retry_delay=int(os.getenv("CELERY_RETRY_DELAY", 60))
)
def sync_etsy_task(self, keywords: str = "vintage jeans", limit: int = 100) -> Dict[str, Any]:
    """
    Celery task to sync Etsy listings.

    Args:
        keywords: Search keywords
        limit: Maximum listings to sync

    Returns:
        Sync statistics dictionary
    """
    logger.info(f"Starting Etsy sync task: {keywords} (limit: {limit})")

    # Create sync job record
    supabase = get_supabase_client()
    job_data = {
        "platform": "etsy",
        "job_type": "incremental_sync",
        "status": "running",
        "started_at": datetime.now().isoformat(),
        "celery_task_id": self.request.id
    }

    try:
        # Insert job record
        job_result = supabase.table("marketplace_sync_jobs").insert(job_data).execute()
        job_id = job_result.data[0]["id"] if job_result.data else None

        # Execute sync
        start_time = datetime.now()
        stats = sync_etsy_listings(keywords, limit)
        duration = (datetime.now() - start_time).total_seconds()

        # Update job record with results
        if job_id:
            update_data = {
                "status": "completed",
                "completed_at": datetime.now().isoformat(),
                "duration_seconds": int(duration),
                "listings_processed": stats.get("listings_found", 0),
                "listings_added": stats.get("added", 0),
                "listings_updated": stats.get("updated", 0),
            }
            supabase.table("marketplace_sync_jobs").update(update_data).eq("id", job_id).execute()

        logger.info(f"Etsy sync completed: {stats}")
        return stats

    except Exception as e:
        logger.error(f"Etsy sync failed: {e}")

        # Update job record with error
        if job_id:
            error_data = {
                "status": "failed",
                "completed_at": datetime.now().isoformat(),
                "error_message": str(e),
                "error_details": {"exception_type": type(e).__name__}
            }
            supabase.table("marketplace_sync_jobs").update(error_data).eq("id", job_id).execute()

        # Retry task
        raise self.retry(exc=e)


@app.task(
    bind=True,
    name="tasks.marketplace_tasks.sync_reddit_task",
    max_retries=int(os.getenv("CELERY_MAX_RETRIES", 3)),
    default_retry_delay=int(os.getenv("CELERY_RETRY_DELAY", 60))
)
def sync_reddit_task(self, keywords: str = "vintage jeans", limit: int = 100) -> Dict[str, Any]:
    """
    Celery task to sync Reddit posts.

    Args:
        keywords: Search keywords
        limit: Maximum posts to sync

    Returns:
        Sync statistics dictionary
    """
    logger.info(f"Starting Reddit sync task: {keywords} (limit: {limit})")

    # Create sync job record
    supabase = get_supabase_client()
    job_data = {
        "platform": "reddit",
        "job_type": "incremental_sync",
        "status": "running",
        "started_at": datetime.now().isoformat(),
        "celery_task_id": self.request.id
    }

    try:
        # Insert job record
        job_result = supabase.table("marketplace_sync_jobs").insert(job_data).execute()
        job_id = job_result.data[0]["id"] if job_result.data else None

        # Execute sync
        start_time = datetime.now()
        stats = sync_reddit_posts(keywords, limit)
        duration = (datetime.now() - start_time).total_seconds()

        # Update job record with results
        if job_id:
            update_data = {
                "status": "completed",
                "completed_at": datetime.now().isoformat(),
                "duration_seconds": int(duration),
                "listings_processed": stats.get("posts_found", 0),
                "listings_added": stats.get("added", 0),
                "listings_updated": stats.get("updated", 0),
            }
            supabase.table("marketplace_sync_jobs").update(update_data).eq("id", job_id).execute()

        logger.info(f"Reddit sync completed: {stats}")
        return stats

    except Exception as e:
        logger.error(f"Reddit sync failed: {e}")

        # Update job record with error
        if job_id:
            error_data = {
                "status": "failed",
                "completed_at": datetime.now().isoformat(),
                "error_message": str(e),
                "error_details": {"exception_type": type(e).__name__}
            }
            supabase.table("marketplace_sync_jobs").update(error_data).eq("id", job_id).execute()

        # Retry task
        raise self.retry(exc=e)


@app.task(name="tasks.marketplace_tasks.sync_all_marketplaces")
def sync_all_marketplaces_task(keywords: str = "vintage jeans", limit: int = 100) -> Dict[str, Any]:
    """
    Sync all marketplaces in parallel using Celery groups.

    Args:
        keywords: Search keywords
        limit: Maximum listings per marketplace

    Returns:
        Combined statistics from all marketplaces
    """
    from celery import group

    logger.info(f"Starting full marketplace sync: {keywords}")

    # Create group of tasks to run in parallel
    job = group([
        sync_ebay_task.s(keywords, limit),
        sync_etsy_task.s(keywords, limit),
        sync_reddit_task.s(keywords, limit)
    ])

    # Execute tasks in parallel
    result = job.apply_async()

    # Wait for all tasks to complete (with timeout)
    results = result.get(timeout=600)  # 10 minute timeout

    # Combine statistics
    combined_stats = {
        "ebay": results[0] if len(results) > 0 else {},
        "etsy": results[1] if len(results) > 1 else {},
        "reddit": results[2] if len(results) > 2 else {},
        "total_listings": sum([
            results[0].get("listings_found", 0) if len(results) > 0 else 0,
            results[1].get("listings_found", 0) if len(results) > 1 else 0,
            results[2].get("posts_found", 0) if len(results) > 2 else 0
        ])
    }

    logger.info(f"Full marketplace sync completed: {combined_stats}")
    return combined_stats


@app.task(name="tasks.marketplace_tasks.cleanup_old_sync_jobs")
def cleanup_old_sync_jobs(days_to_keep: int = 30) -> Dict[str, int]:
    """
    Clean up old sync job records.

    Args:
        days_to_keep: Number of days to keep (default: 30)

    Returns:
        Cleanup statistics
    """
    logger.info(f"Cleaning up sync jobs older than {days_to_keep} days")

    supabase = get_supabase_client()
    cutoff_date = datetime.now() - timedelta(days=days_to_keep)

    try:
        # Delete old job records
        result = supabase.table("marketplace_sync_jobs").delete().lt(
            "created_at", cutoff_date.isoformat()
        ).execute()

        deleted_count = len(result.data) if result.data else 0
        logger.info(f"Cleaned up {deleted_count} old sync job records")

        return {"deleted": deleted_count, "cutoff_date": cutoff_date.isoformat()}

    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        return {"deleted": 0, "error": str(e)}
