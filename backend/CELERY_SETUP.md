# Celery Background Tasks Setup

This guide covers setting up and running Celery for background marketplace synchronization.

## Prerequisites

### 1. Install Redis

Redis is required as the message broker and result backend for Celery.

**macOS:**
```bash
brew install redis
brew services start redis
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

**Verify Redis is running:**
```bash
redis-cli ping
# Should return: PONG
```

### 2. Install Python Dependencies

All required packages are already in `requirements.txt`:
```bash
cd backend
source ../.venv/bin/activate
pip install -r requirements.txt
```

## Configuration

### Environment Variables

Ensure these are set in `backend/.env`:

```bash
# Redis Configuration
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Celery Configuration
CELERY_TASK_TIME_LIMIT=600  # 10 minutes
CELERY_TASK_SOFT_TIME_LIMIT=540  # 9 minutes
CELERY_MAX_RETRIES=3
CELERY_RETRY_DELAY=60  # seconds

# Marketplace Sync Settings
MARKETPLACE_SYNC_INTERVAL_HOURS=6  # Sync every 6 hours
MARKETPLACE_MAX_LISTINGS_PER_SYNC=1000
MARKETPLACE_ENABLE_AI_ANALYSIS=true
```

## Running Celery

### Option 1: Development (Single Terminal per Service)

Open separate terminals for each service:

**Terminal 1 - Celery Worker:**
```bash
cd backend
source ../.venv/bin/activate
celery -A celery_app worker --loglevel=info
```

**Terminal 2 - Celery Beat (Scheduler):**
```bash
cd backend
source ../.venv/bin/activate
celery -A celery_app beat --loglevel=info
```

**Terminal 3 - Flower (Monitoring UI):**
```bash
cd backend
source ../.venv/bin/activate
celery -A celery_app flower --port=5555
```

Access Flower UI at: http://localhost:5555

### Option 2: Development (Combined Worker + Beat)

Run worker and beat in one process (simpler for development):

```bash
cd backend
source ../.venv/bin/activate
celery -A celery_app worker --beat --loglevel=info
```

### Option 3: Production (systemd services)

Create systemd service files for production deployment:

**`/etc/systemd/system/celery-worker.service`:**
```ini
[Unit]
Description=Celery Worker for Vintage Jeans Marketplace
After=network.target redis.service

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/path/to/backend
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/celery -A celery_app worker \
    --detach \
    --loglevel=info \
    --logfile=/var/log/celery/worker.log \
    --pidfile=/var/run/celery/worker.pid

[Install]
WantedBy=multi-user.target
```

**`/etc/systemd/system/celery-beat.service`:**
```ini
[Unit]
Description=Celery Beat Scheduler
After=network.target redis.service

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/path/to/backend
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/celery -A celery_app beat \
    --detach \
    --loglevel=info \
    --logfile=/var/log/celery/beat.log \
    --pidfile=/var/run/celery/beat.pid

[Install]
WantedBy=multi-user.target
```

Enable and start services:
```bash
sudo systemctl daemon-reload
sudo systemctl enable celery-worker celery-beat
sudo systemctl start celery-worker celery-beat
sudo systemctl status celery-worker celery-beat
```

## Available Tasks

### Marketplace Sync Tasks

**Sync eBay Listings:**
```python
from tasks.marketplace_tasks import sync_ebay_task
result = sync_ebay_task.apply_async(args=["vintage jeans", 100])
```

**Sync Etsy Listings:**
```python
from tasks.marketplace_tasks import sync_etsy_task
result = sync_etsy_task.apply_async(args=["vintage jeans", 100])
```

**Sync Reddit Posts:**
```python
from tasks.marketplace_tasks import sync_reddit_task
result = sync_reddit_task.apply_async(args=["vintage jeans", 100])
```

**Sync All Marketplaces:**
```python
from tasks.marketplace_tasks import sync_all_marketplaces_task
result = sync_all_marketplaces_task.apply_async(args=["vintage jeans", 100])
```

### Analytics Tasks

**Generate Daily Trends:**
```python
from tasks.analytics_tasks import generate_daily_trends
result = generate_daily_trends.apply_async()
```

**Analyze Listing with AI:**
```python
from tasks.analytics_tasks import analyze_listing_with_ai
result = analyze_listing_with_ai.apply_async(args=["listing-uuid"])
```

## Scheduled Tasks

The following tasks run automatically via Celery Beat:

| Task | Schedule | Description |
|------|----------|-------------|
| `sync-ebay-listings` | Every 6 hours | Sync eBay vintage jeans listings |
| `sync-etsy-listings` | Every 6 hours (offset +2h) | Sync Etsy vintage jeans listings |
| `sync-reddit-posts` | Every 6 hours (offset +4h) | Monitor Reddit marketplace posts |
| `daily-trend-analysis` | Daily at 1:00 AM | Generate market trend analytics |
| `cleanup-old-sync-jobs` | Daily at 3:00 AM | Remove sync jobs older than 30 days |

## Monitoring

### Flower UI

Flower provides a web-based UI for monitoring Celery:

**Start Flower:**
```bash
celery -A celery_app flower --port=5555
```

**Access:** http://localhost:5555

**Features:**
- Real-time task monitoring
- Worker status and stats
- Task history and results
- Rate limiting and time limits
- Task routing visualization

### Command Line Monitoring

**Check active workers:**
```bash
celery -A celery_app inspect active
```

**Check scheduled tasks:**
```bash
celery -A celery_app inspect scheduled
```

**Check registered tasks:**
```bash
celery -A celery_app inspect registered
```

**Worker stats:**
```bash
celery -A celery_app inspect stats
```

### Database Monitoring

Check sync job status via API or database:

```sql
-- Recent sync jobs
SELECT platform, status, listings_added, created_at
FROM marketplace_sync_jobs
ORDER BY created_at DESC
LIMIT 10;

-- Failed jobs
SELECT platform, error_message, created_at
FROM marketplace_sync_jobs
WHERE status = 'failed'
ORDER BY created_at DESC;
```

## Troubleshooting

### Redis Connection Issues

**Problem:** `celery.exceptions.ImproperlyConfigured: No Redis client found`

**Solution:**
```bash
# Check Redis is running
redis-cli ping

# Verify REDIS_URL in .env
echo $REDIS_URL

# Test Redis connection
redis-cli -u redis://localhost:6379/0 ping
```

### Task Not Running

**Problem:** Tasks are queued but not executing

**Solution:**
```bash
# Check worker is running
celery -A celery_app inspect active

# Check worker logs
celery -A celery_app worker --loglevel=debug

# Purge all pending tasks
celery -A celery_app purge
```

### Import Errors

**Problem:** `ImportError: No module named 'tasks'`

**Solution:**
```bash
# Ensure you're in the backend directory
cd backend

# Verify PYTHONPATH includes current directory
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run celery from backend directory
celery -A celery_app worker --loglevel=info
```

### Beat Not Scheduling Tasks

**Problem:** Scheduled tasks not executing

**Solution:**
```bash
# Verify beat is running
ps aux | grep "celery.*beat"

# Check beat schedule file
ls -la celerybeat-schedule

# Delete schedule file to reset (celery must be stopped)
rm celerybeat-schedule

# Restart beat
celery -A celery_app beat --loglevel=info
```

## API Integration

### Trigger Sync via API

**Endpoint:** `POST /api/marketplace/sync/trigger`

**Request:**
```json
{
  "platform": "ebay",
  "keywords": "vintage levi's jeans",
  "limit": 100
}
```

**Response:**
```json
{
  "status": "triggered",
  "platform": "ebay",
  "task_id": "abc123-def456-789",
  "message": "Sync task started for ebay",
  "keywords": "vintage levi's jeans",
  "limit": 100
}
```

### Check Task Status

**Endpoint:** `GET /api/marketplace/sync/status/{task_id}`

**Response:**
```json
{
  "task_id": "abc123-def456-789",
  "state": "SUCCESS",
  "status": "SUCCESS",
  "result": {
    "listings_found": 95,
    "added": 23,
    "updated": 72,
    "errors": 0
  }
}
```

## Performance Optimization

### Concurrency Settings

Adjust worker concurrency based on your server:

```bash
# Use 4 worker processes
celery -A celery_app worker --concurrency=4

# Use all available CPU cores
celery -A celery_app worker --autoscale=10,3
```

### Task Prioritization

High priority tasks:
```python
task.apply_async(priority=9)  # High priority (0-9)
```

### Rate Limiting

Limit API calls to avoid rate limits:

```python
@app.task(rate_limit='100/h')  # Max 100 tasks per hour
def rate_limited_task():
    pass
```

## Production Deployment

### Render.com

Add to `render.yaml`:

```yaml
services:
  - type: worker
    name: celery-worker
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: celery -A celery_app worker --loglevel=info
    envVars:
      - key: REDIS_URL
        fromService:
          type: redis
          name: redis
          property: connectionString

  - type: worker
    name: celery-beat
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: celery -A celery_app beat --loglevel=info
    envVars:
      - key: REDIS_URL
        fromService:
          type: redis
          name: redis
          property: connectionString

  - type: redis
    name: redis
    ipAllowList: []
```

### Docker

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  celery-worker:
    build: .
    command: celery -A celery_app worker --loglevel=info
    depends_on:
      - redis
    environment:
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - .:/app

  celery-beat:
    build: .
    command: celery -A celery_app beat --loglevel=info
    depends_on:
      - redis
    environment:
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - .:/app

  flower:
    build: .
    command: celery -A celery_app flower --port=5555
    ports:
      - "5555:5555"
    depends_on:
      - redis
    environment:
      - REDIS_URL=redis://redis:6379/0

volumes:
  redis_data:
```

## Testing

### Manual Task Testing

```python
# Test debug task
from celery_app import debug_task
result = debug_task.apply_async()
print(result.get(timeout=10))

# Test eBay sync (dry run)
from tasks.marketplace_tasks import sync_ebay_task
result = sync_ebay_task.apply_async(args=["vintage jeans", 5])
print(result.get(timeout=60))
```

### Unit Testing Celery Tasks

```python
# tests/test_celery_tasks.py
import pytest
from tasks.marketplace_tasks import sync_ebay_task

@pytest.mark.celery
def test_sync_ebay_task(celery_app, celery_worker):
    result = sync_ebay_task.apply_async(args=["test", 1])
    assert result.get(timeout=10)
```

## Resources

- [Celery Documentation](https://docs.celeryproject.org/)
- [Flower Documentation](https://flower.readthedocs.io/)
- [Redis Documentation](https://redis.io/documentation)
- [FastAPI Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)
