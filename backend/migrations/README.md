# Database Migrations

This directory contains SQL migrations for the Vintage Jeans Marketplace database.

## Migration Files

### 001_add_seller_columns.sql
Adds missing columns to the sellers table:
- location (TEXT)
- phone (TEXT)
- business_name (TEXT)
- referred_by (UUID, foreign key to sellers)
- updated_at (TIMESTAMP WITH TIME ZONE)
- Indexes and triggers for referral tracking

### 002_create_marketplace_tables.sql
Creates tables for marketplace API integrations:
- **marketplace_listings** - Stores listings from eBay, Etsy, Reddit with AI analysis
- **marketplace_sync_jobs** - Tracks background sync jobs and their status
- **marketplace_trends** - Aggregated market analytics and trend data
- **marketplace_credentials** - Encrypted API credentials for each platform
- **marketplace_saved_searches** - User-defined searches to monitor

## How to Run Migrations

### Option 1: Supabase SQL Editor (Recommended)

1. Go to your Supabase project: https://supabase.com/dashboard/project/fpodzadjsjnlsztqtwdd
2. Navigate to **SQL Editor** in the left sidebar
3. Click **New query**
4. Copy the contents of the migration file
5. Paste into the SQL editor
6. Click **Run** or press `Cmd+Enter`
7. Verify success message

### Option 2: psql Command Line

```bash
# Set environment variables
export SUPABASE_URL="https://fpodzadjsjnlsztqtwdd.supabase.co"
export SUPABASE_PASSWORD="your-database-password"

# Run migration
psql "postgresql://postgres:${SUPABASE_PASSWORD}@db.fpodzadjsjnlsztqtwdd.supabase.co:5432/postgres" \
  -f migrations/002_create_marketplace_tables.sql
```

### Option 3: Python Script

```python
from research.db.supabase_client import get_supabase_client
from pathlib import Path

# Read migration file
migration_file = Path("migrations/002_create_marketplace_tables.sql")
sql = migration_file.read_text()

# Execute via Supabase
supabase = get_supabase_client()
supabase.rpc('exec_sql', {'query': sql}).execute()
```

## Migration Order

Run migrations in numerical order:
1. 001_add_seller_columns.sql ✅ (Already run)
2. 002_create_marketplace_tables.sql ⏳ (Ready to run)

## Verification

After running migration 002, verify tables were created:

```sql
-- Check tables exist
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name LIKE 'marketplace_%';

-- Expected result:
-- marketplace_listings
-- marketplace_sync_jobs
-- marketplace_trends
-- marketplace_credentials
-- marketplace_saved_searches

-- Check columns in marketplace_listings
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'marketplace_listings'
ORDER BY ordinal_position;

-- Check indexes
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename LIKE 'marketplace_%';
```

## Rollback

To rollback migration 002:

```sql
-- Drop all marketplace tables
DROP TABLE IF EXISTS marketplace_saved_searches CASCADE;
DROP TABLE IF EXISTS marketplace_credentials CASCADE;
DROP TABLE IF EXISTS marketplace_trends CASCADE;
DROP TABLE IF EXISTS marketplace_sync_jobs CASCADE;
DROP TABLE IF EXISTS marketplace_listings CASCADE;
```

## Database Schema Overview

```
sellers (existing)
  ├── id (UUID, primary key)
  ├── email
  ├── full_name
  ├── role (admin, seller, buyer)
  └── location, phone, business_name, referred_by

marketplace_listings
  ├── id (UUID, primary key)
  ├── platform (ebay, etsy, reddit)
  ├── external_id (platform's listing ID)
  ├── title, description, price
  ├── brand, size, condition
  ├── ai_tags[], ai_summary
  ├── trend_score
  └── raw_data (JSONB)

marketplace_sync_jobs
  ├── id (UUID, primary key)
  ├── platform
  ├── job_type (full_sync, incremental_sync, etc.)
  ├── status (pending, running, completed, failed)
  ├── listings_processed, listings_added
  └── celery_task_id

marketplace_trends
  ├── id (UUID, primary key)
  ├── category (e.g., "vintage_levis")
  ├── avg_price, total_listings
  ├── engagement_score
  └── period_start, period_end

marketplace_credentials
  ├── id (UUID, primary key)
  ├── platform (unique)
  ├── client_id, client_secret
  ├── access_token, refresh_token
  └── expires_at

marketplace_saved_searches
  ├── id (UUID, primary key)
  ├── created_by (foreign key to sellers)
  ├── keywords[], platforms[]
  ├── price filters, size/brand filters
  └── notification settings
```

## Next Steps

After running this migration:

1. Configure API credentials in `.env`:
   ```bash
   # eBay API
   EBAY_CLIENT_ID=your-ebay-client-id
   EBAY_CLIENT_SECRET=your-ebay-client-secret
   EBAY_REDIRECT_URI=http://localhost:8000/api/marketplace/ebay/callback

   # Etsy API
   ETSY_API_KEY=your-etsy-api-key
   ETSY_API_SECRET=your-etsy-api-secret
   ETSY_REDIRECT_URI=http://localhost:8000/api/marketplace/etsy/callback

   # Reddit API
   REDDIT_CLIENT_ID=your-reddit-client-id
   REDDIT_CLIENT_SECRET=your-reddit-client-secret
   REDDIT_USER_AGENT=VintageJeansMarketplace/1.0

   # Redis for Celery
   REDIS_URL=redis://localhost:6379/0
   ```

2. Install new dependencies:
   ```bash
   cd backend
   source ../.venv/bin/activate
   pip install -r requirements.txt
   ```

3. Implement API integration services
4. Set up Celery background tasks
5. Create marketplace API endpoints
