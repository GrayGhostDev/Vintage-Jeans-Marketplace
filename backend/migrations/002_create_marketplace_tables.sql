-- Migration: Create marketplace data tables
-- Date: 2025-11-04
-- Description: Add tables for eBay, Etsy, Reddit marketplace integrations and sync jobs

-- =====================================================
-- MARKETPLACE LISTINGS TABLE
-- =====================================================
-- Stores all marketplace listings from eBay, Etsy, Reddit
CREATE TABLE IF NOT EXISTS marketplace_listings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Source information
    platform VARCHAR(20) NOT NULL CHECK (platform IN ('ebay', 'etsy', 'reddit')),
    external_id VARCHAR(255) NOT NULL,
    url TEXT NOT NULL,

    -- Listing details
    title TEXT NOT NULL,
    description TEXT,
    price DECIMAL(10, 2),
    currency VARCHAR(3) DEFAULT 'USD',
    condition VARCHAR(50),
    size VARCHAR(20),
    brand VARCHAR(100),

    -- Product categorization
    waist_size INTEGER,
    inseam_length INTEGER,
    style VARCHAR(50),
    wash VARCHAR(50),
    era VARCHAR(50),

    -- Images
    image_urls TEXT[], -- Array of image URLs
    thumbnail_url TEXT,

    -- Seller information
    seller_username VARCHAR(255),
    seller_rating DECIMAL(3, 2),
    seller_location VARCHAR(255),

    -- Listing status
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'sold', 'removed', 'expired')),
    listed_at TIMESTAMP WITH TIME ZONE,
    sold_at TIMESTAMP WITH TIME ZONE,

    -- Market analytics
    view_count INTEGER DEFAULT 0,
    watch_count INTEGER DEFAULT 0,
    favorite_count INTEGER DEFAULT 0,

    -- AI analysis
    ai_tags TEXT[], -- AI-generated tags
    ai_summary TEXT, -- AI-generated summary
    trend_score DECIMAL(5, 2), -- Trending score (0-100)

    -- Metadata
    raw_data JSONB, -- Store complete API response
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_synced_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Unique constraint per platform
    UNIQUE(platform, external_id)
);

-- Indexes for marketplace_listings
CREATE INDEX IF NOT EXISTS idx_marketplace_listings_platform ON marketplace_listings(platform);
CREATE INDEX IF NOT EXISTS idx_marketplace_listings_status ON marketplace_listings(status);
CREATE INDEX IF NOT EXISTS idx_marketplace_listings_price ON marketplace_listings(price);
CREATE INDEX IF NOT EXISTS idx_marketplace_listings_brand ON marketplace_listings(brand);
CREATE INDEX IF NOT EXISTS idx_marketplace_listings_created_at ON marketplace_listings(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_marketplace_listings_trend_score ON marketplace_listings(trend_score DESC);
CREATE INDEX IF NOT EXISTS idx_marketplace_listings_ai_tags ON marketplace_listings USING GIN(ai_tags);


-- =====================================================
-- SYNC JOBS TABLE
-- =====================================================
-- Tracks background sync jobs for each marketplace
CREATE TABLE IF NOT EXISTS marketplace_sync_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Job information
    platform VARCHAR(20) NOT NULL CHECK (platform IN ('ebay', 'etsy', 'reddit')),
    job_type VARCHAR(50) NOT NULL CHECK (job_type IN ('full_sync', 'incremental_sync', 'listing_update', 'trending_analysis')),

    -- Job status
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),

    -- Execution details
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,

    -- Results
    listings_processed INTEGER DEFAULT 0,
    listings_added INTEGER DEFAULT 0,
    listings_updated INTEGER DEFAULT 0,
    listings_removed INTEGER DEFAULT 0,

    -- Error tracking
    error_message TEXT,
    error_details JSONB,
    retry_count INTEGER DEFAULT 0,

    -- Celery integration
    celery_task_id VARCHAR(255),

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for sync_jobs
CREATE INDEX IF NOT EXISTS idx_sync_jobs_platform ON marketplace_sync_jobs(platform);
CREATE INDEX IF NOT EXISTS idx_sync_jobs_status ON marketplace_sync_jobs(status);
CREATE INDEX IF NOT EXISTS idx_sync_jobs_created_at ON marketplace_sync_jobs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_sync_jobs_celery_task_id ON marketplace_sync_jobs(celery_task_id);


-- =====================================================
-- MARKETPLACE TRENDS TABLE
-- =====================================================
-- Stores aggregated trend data and analytics
CREATE TABLE IF NOT EXISTS marketplace_trends (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Trend information
    category VARCHAR(100) NOT NULL, -- e.g., "vintage_levis", "high_waist_jeans"
    platform VARCHAR(20) CHECK (platform IN ('ebay', 'etsy', 'reddit', 'all')),

    -- Metrics
    total_listings INTEGER DEFAULT 0,
    avg_price DECIMAL(10, 2),
    min_price DECIMAL(10, 2),
    max_price DECIMAL(10, 2),
    total_sales INTEGER DEFAULT 0,

    -- Popularity metrics
    search_volume INTEGER DEFAULT 0,
    engagement_score DECIMAL(5, 2), -- 0-100

    -- Time range
    period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    period_end TIMESTAMP WITH TIME ZONE NOT NULL,

    -- AI insights
    ai_insights JSONB, -- AI-generated insights about the trend

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Unique constraint
    UNIQUE(category, platform, period_start, period_end)
);

-- Indexes for trends
CREATE INDEX IF NOT EXISTS idx_trends_category ON marketplace_trends(category);
CREATE INDEX IF NOT EXISTS idx_trends_platform ON marketplace_trends(platform);
CREATE INDEX IF NOT EXISTS idx_trends_period_start ON marketplace_trends(period_start DESC);
CREATE INDEX IF NOT EXISTS idx_trends_engagement_score ON marketplace_trends(engagement_score DESC);


-- =====================================================
-- API CREDENTIALS TABLE
-- =====================================================
-- Stores encrypted API credentials for each marketplace
CREATE TABLE IF NOT EXISTS marketplace_credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Platform information
    platform VARCHAR(20) NOT NULL UNIQUE CHECK (platform IN ('ebay', 'etsy', 'reddit')),

    -- Credentials (encrypted in application layer)
    client_id TEXT,
    client_secret TEXT,
    access_token TEXT,
    refresh_token TEXT,

    -- OAuth details
    token_type VARCHAR(50),
    expires_at TIMESTAMP WITH TIME ZONE,
    scope TEXT,

    -- Additional configuration
    config JSONB, -- Platform-specific configuration

    -- Status
    is_active BOOLEAN DEFAULT true,
    last_refreshed_at TIMESTAMP WITH TIME ZONE,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


-- =====================================================
-- SAVED SEARCHES TABLE
-- =====================================================
-- User-defined searches to monitor across marketplaces
CREATE TABLE IF NOT EXISTS marketplace_saved_searches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- User information (link to sellers table for admin users)
    created_by UUID REFERENCES sellers(id) ON DELETE CASCADE,

    -- Search details
    name VARCHAR(255) NOT NULL,
    description TEXT,

    -- Search criteria
    platforms TEXT[] NOT NULL, -- Array of platforms to search
    keywords TEXT[] NOT NULL, -- Search keywords
    min_price DECIMAL(10, 2),
    max_price DECIMAL(10, 2),
    size_filter VARCHAR(20),
    brand_filter VARCHAR(100),
    condition_filter VARCHAR(50),

    -- Notification settings
    notify_on_new_listings BOOLEAN DEFAULT true,
    notify_on_price_drop BOOLEAN DEFAULT false,
    notification_email VARCHAR(255),

    -- Status
    is_active BOOLEAN DEFAULT true,
    last_run_at TIMESTAMP WITH TIME ZONE,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for saved_searches
CREATE INDEX IF NOT EXISTS idx_saved_searches_created_by ON marketplace_saved_searches(created_by);
CREATE INDEX IF NOT EXISTS idx_saved_searches_is_active ON marketplace_saved_searches(is_active);


-- =====================================================
-- TRIGGERS
-- =====================================================

-- Trigger to update updated_at for marketplace_listings
DROP TRIGGER IF EXISTS update_marketplace_listings_updated_at ON marketplace_listings;
CREATE TRIGGER update_marketplace_listings_updated_at
    BEFORE UPDATE ON marketplace_listings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger to update updated_at for sync_jobs
DROP TRIGGER IF EXISTS update_sync_jobs_updated_at ON marketplace_sync_jobs;
CREATE TRIGGER update_sync_jobs_updated_at
    BEFORE UPDATE ON marketplace_sync_jobs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger to update updated_at for trends
DROP TRIGGER IF EXISTS update_trends_updated_at ON marketplace_trends;
CREATE TRIGGER update_trends_updated_at
    BEFORE UPDATE ON marketplace_trends
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger to update updated_at for credentials
DROP TRIGGER IF EXISTS update_credentials_updated_at ON marketplace_credentials;
CREATE TRIGGER update_credentials_updated_at
    BEFORE UPDATE ON marketplace_credentials
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger to update updated_at for saved_searches
DROP TRIGGER IF EXISTS update_saved_searches_updated_at ON marketplace_saved_searches;
CREATE TRIGGER update_saved_searches_updated_at
    BEFORE UPDATE ON marketplace_saved_searches
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- =====================================================
-- COMMENTS
-- =====================================================

COMMENT ON TABLE marketplace_listings IS 'Stores all marketplace listings from eBay, Etsy, and Reddit with AI analysis';
COMMENT ON TABLE marketplace_sync_jobs IS 'Tracks background sync jobs for marketplace data collection';
COMMENT ON TABLE marketplace_trends IS 'Aggregated trend data and market analytics';
COMMENT ON TABLE marketplace_credentials IS 'Encrypted API credentials for marketplace platforms';
COMMENT ON TABLE marketplace_saved_searches IS 'User-defined searches to monitor across marketplaces';
