"""
Celery application for background tasks.

This module configures Celery for distributed task processing:
- Marketplace data synchronization
- AI analysis and trend detection
- Scheduled periodic tasks
- Email notifications

Architecture:
- Broker: Redis (task queue)
- Backend: Redis (result storage)
- Worker: Celery worker process
- Beat: Celery Beat scheduler for periodic tasks
- Flower: Monitoring UI

Usage:
    # Start worker
    celery -A celery_app worker --loglevel=info

    # Start beat scheduler
    celery -A celery_app beat --loglevel=info

    # Start Flower monitoring
    celery -A celery_app flower --port=5555
"""

import os
from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Celery app
app = Celery(
    "vintage_jeans_marketplace",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
    include=[
        "tasks.marketplace_tasks",  # Marketplace sync tasks
        "tasks.analytics_tasks",    # Analytics and AI tasks
    ]
)

# Celery configuration
app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,

    # Task execution settings
    task_track_started=True,
    task_time_limit=int(os.getenv("CELERY_TASK_TIME_LIMIT", 600)),  # 10 minutes
    task_soft_time_limit=int(os.getenv("CELERY_TASK_SOFT_TIME_LIMIT", 540)),  # 9 minutes

    # Retry settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,

    # Worker settings
    worker_prefetch_multiplier=1,  # One task at a time
    worker_max_tasks_per_child=100,  # Restart worker after 100 tasks (memory leak prevention)

    # Result backend settings
    result_expires=3600,  # Results expire after 1 hour
    result_backend_transport_options={"master_name": "mymaster"},

    # Beat schedule (periodic tasks)
    beat_schedule={
        # Sync eBay listings every 6 hours
        "sync-ebay-listings": {
            "task": "tasks.marketplace_tasks.sync_ebay_task",
            "schedule": crontab(
                hour=f"*/{os.getenv('MARKETPLACE_SYNC_INTERVAL_HOURS', 6)}"
            ),
            "args": ("vintage jeans", 100),
        },

        # Sync Etsy listings every 6 hours (offset by 2 hours)
        "sync-etsy-listings": {
            "task": "tasks.marketplace_tasks.sync_etsy_task",
            "schedule": crontab(
                hour=f"2-23/{os.getenv('MARKETPLACE_SYNC_INTERVAL_HOURS', 6)}"
            ),
            "args": ("vintage jeans", 100),
        },

        # Sync Reddit posts every 6 hours (offset by 4 hours)
        "sync-reddit-posts": {
            "task": "tasks.marketplace_tasks.sync_reddit_task",
            "schedule": crontab(
                hour=f"4-23/{os.getenv('MARKETPLACE_SYNC_INTERVAL_HOURS', 6)}"
            ),
            "args": ("vintage jeans", 100),
        },

        # Generate daily trend analysis at 1 AM
        "daily-trend-analysis": {
            "task": "tasks.analytics_tasks.generate_daily_trends",
            "schedule": crontab(hour=1, minute=0),
        },

        # Cleanup old sync jobs every day at 3 AM
        "cleanup-old-sync-jobs": {
            "task": "tasks.marketplace_tasks.cleanup_old_sync_jobs",
            "schedule": crontab(hour=3, minute=0),
            "args": (30,),  # Keep last 30 days
        },
    },
)

# Optional: Configure logging
app.conf.update(
    worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
    worker_task_log_format="[%(asctime)s: %(levelname)s/%(processName)s] [%(task_name)s(%(task_id)s)] %(message)s",
)


@app.task(bind=True)
def debug_task(self):
    """Debug task to test Celery configuration."""
    print(f"Request: {self.request!r}")
    return {"status": "success", "message": "Celery is working!"}


if __name__ == "__main__":
    app.start()
