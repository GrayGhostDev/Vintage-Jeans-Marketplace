-- Vintage Jeans Marketplace - Supabase Database Schema
-- This schema is optimized for PostgreSQL with UUID primary keys

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- SELLERS TABLE
-- ============================================================================
CREATE TABLE sellers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    region TEXT NOT NULL,  -- City, Country (e.g., "Los Angeles, USA")

    -- Optional profile information
    business_name TEXT,
    phone TEXT,

    -- Authentication (if using custom JWT, not Supabase Auth)
    hashed_password TEXT NOT NULL,

    -- Status and permissions
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    role TEXT DEFAULT 'seller' CHECK (role IN ('seller', 'admin')),

    -- Metrics
    total_listings INTEGER DEFAULT 0,
    active_listings INTEGER DEFAULT 0,
    total_sales INTEGER DEFAULT 0,
    total_revenue NUMERIC(10, 2) DEFAULT 0.00,

    -- Referral system
    referral_code TEXT UNIQUE,
    referred_by UUID REFERENCES sellers(id) ON DELETE SET NULL,

    -- OAuth tokens for marketplace integrations (optional)
    ebay_access_token TEXT,
    ebay_refresh_token TEXT,
    ebay_token_expires_at TIMESTAMPTZ,

    etsy_access_token TEXT,
    etsy_refresh_token TEXT,
    etsy_token_expires_at TIMESTAMPTZ,

    whatnot_access_token TEXT,
    whatnot_refresh_token TEXT,
    whatnot_token_expires_at TIMESTAMPTZ,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login_at TIMESTAMPTZ
);

-- Indexes for sellers table
CREATE INDEX idx_sellers_email ON sellers(email);
CREATE INDEX idx_sellers_region ON sellers(region);
CREATE INDEX idx_sellers_referral_code ON sellers(referral_code);
CREATE INDEX idx_sellers_created_at ON sellers(created_at DESC);

-- ============================================================================
-- LISTINGS TABLE
-- ============================================================================
CREATE TABLE listings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    seller_id UUID NOT NULL REFERENCES sellers(id) ON DELETE CASCADE,

    -- Platform information
    platform TEXT DEFAULT 'manual' CHECK (platform IN ('manual', 'ebay', 'etsy', 'whatnot', 'depop', 'poshmark', 'grailed')),
    platform_listing_id TEXT,  -- External ID from platform
    platform_url TEXT,

    -- Basic listing information
    title TEXT NOT NULL,
    description TEXT NOT NULL,

    -- Product attributes
    brand TEXT NOT NULL,
    era TEXT,  -- e.g., "1950s", "1960s", "1970s", "1980s", "1990s"
    model TEXT,  -- e.g., "501", "505", "517"

    -- Sizing (flexible to accommodate different formats)
    size TEXT,  -- e.g., "32x34", "M", "L", "32"
    waist_size INTEGER,
    inseam_length INTEGER,

    -- Condition
    condition TEXT DEFAULT 'good' CHECK (condition IN ('new_with_tags', 'excellent', 'very_good', 'good', 'fair', 'poor')),
    condition_notes TEXT,

    -- Material and features
    material TEXT,  -- e.g., "100% cotton denim", "selvedge denim"
    wash TEXT,  -- e.g., "Dark wash", "Light wash", "Distressed"

    -- Pricing
    price NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    currency TEXT DEFAULT 'USD',
    purchase_price NUMERIC(10, 2),  -- For ROI calculation

    -- Shipping
    shipping_cost NUMERIC(10, 2) DEFAULT 0.00,
    ships_from TEXT,  -- Location
    ships_to TEXT,  -- e.g., "Worldwide", "US only"

    -- Images (PostgreSQL array of URLs)
    image_urls TEXT[],
    primary_image_url TEXT,

    -- Status and workflow
    status TEXT DEFAULT 'pending_approval' CHECK (status IN ('draft', 'pending_approval', 'active', 'sold', 'inactive', 'rejected')),
    approved_by UUID REFERENCES sellers(id) ON DELETE SET NULL,
    approved_at TIMESTAMPTZ,
    rejection_reason TEXT,

    -- Metrics
    views INTEGER DEFAULT 0,
    favorites INTEGER DEFAULT 0,

    -- Sale information
    sale_price NUMERIC(10, 2),
    sold_at TIMESTAMPTZ,
    sold_to_country TEXT,

    -- Discovery and marketing
    is_featured BOOLEAN DEFAULT false,
    tags TEXT[],  -- PostgreSQL array of tags
    category TEXT,
    provenance TEXT,  -- History/story of the jeans

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_synced_at TIMESTAMPTZ  -- Last sync from external platform
);

-- Indexes for listings table
CREATE INDEX idx_listings_seller_id ON listings(seller_id);
CREATE INDEX idx_listings_brand ON listings(brand);
CREATE INDEX idx_listings_era ON listings(era);
CREATE INDEX idx_listings_status ON listings(status);
CREATE INDEX idx_listings_price ON listings(price);
CREATE INDEX idx_listings_created_at ON listings(created_at DESC);
CREATE INDEX idx_listings_is_featured ON listings(is_featured) WHERE is_featured = true;

-- Composite indexes for common queries
CREATE INDEX idx_listings_brand_era ON listings(brand, era);
CREATE INDEX idx_listings_status_created ON listings(status, created_at DESC);

-- ============================================================================
-- BLOG POSTS TABLE (for SEO and content marketing)
-- ============================================================================
CREATE TABLE blog_posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    excerpt TEXT,
    content TEXT NOT NULL,

    -- SEO metadata
    meta_title TEXT,
    meta_description TEXT,
    meta_keywords TEXT,

    -- Categorization
    category TEXT CHECK (category IN ('guides', 'market_insights', 'seller_stories', 'trends', 'tips')),
    tags TEXT[],

    -- Author and publishing
    author TEXT NOT NULL,
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'archived')),
    published_at TIMESTAMPTZ,

    -- Featured content
    featured BOOLEAN DEFAULT false,
    featured_image_url TEXT,
    featured_image_alt TEXT,

    -- Metrics
    view_count INTEGER DEFAULT 0,
    read_time_minutes INTEGER,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for blog_posts table
CREATE INDEX idx_blog_posts_slug ON blog_posts(slug);
CREATE INDEX idx_blog_posts_status ON blog_posts(status);
CREATE INDEX idx_blog_posts_category ON blog_posts(category);
CREATE INDEX idx_blog_posts_published_at ON blog_posts(published_at DESC);

-- ============================================================================
-- ANALYTICS TABLE (for AI-generated market insights)
-- ============================================================================
CREATE TABLE analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    seller_id UUID REFERENCES sellers(id) ON DELETE CASCADE,

    -- Analysis metadata
    analysis_type TEXT CHECK (analysis_type IN ('market_trends', 'pricing_suggestions', 'arbitrage_opportunities', 'roi_analysis')),

    -- Input data
    input_data JSONB,  -- Flexible JSON storage for input parameters

    -- AI-generated insights
    summary TEXT NOT NULL,
    insights JSONB,  -- Structured insights as JSON
    recommendations TEXT[],

    -- Metrics and scores
    confidence_score NUMERIC(3, 2) CHECK (confidence_score >= 0 AND confidence_score <= 1),

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for analytics table
CREATE INDEX idx_analytics_seller_id ON analytics(seller_id);
CREATE INDEX idx_analytics_type ON analytics(analysis_type);
CREATE INDEX idx_analytics_created_at ON analytics(created_at DESC);

-- ============================================================================
-- SYNC LOGS TABLE (for tracking platform integrations)
-- ============================================================================
CREATE TABLE sync_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    seller_id UUID NOT NULL REFERENCES sellers(id) ON DELETE CASCADE,
    platform TEXT NOT NULL,

    -- Sync status
    status TEXT CHECK (status IN ('started', 'completed', 'failed', 'partial')),

    -- Sync results
    listings_fetched INTEGER DEFAULT 0,
    listings_created INTEGER DEFAULT 0,
    listings_updated INTEGER DEFAULT 0,
    errors TEXT[],

    -- Timestamps
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Indexes for sync_logs table
CREATE INDEX idx_sync_logs_seller_id ON sync_logs(seller_id);
CREATE INDEX idx_sync_logs_platform ON sync_logs(platform);
CREATE INDEX idx_sync_logs_started_at ON sync_logs(started_at DESC);

-- ============================================================================
-- FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at trigger to relevant tables
CREATE TRIGGER update_sellers_updated_at BEFORE UPDATE ON sellers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_listings_updated_at BEFORE UPDATE ON listings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_blog_posts_updated_at BEFORE UPDATE ON blog_posts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to generate unique referral code
CREATE OR REPLACE FUNCTION generate_referral_code(seller_uuid UUID, seller_name TEXT)
RETURNS TEXT AS $$
DECLARE
    code TEXT;
BEGIN
    code := 'VJ' || UPPER(SUBSTRING(REPLACE(seller_name, ' ', ''), 1, 4)) || SUBSTRING(REPLACE(seller_uuid::TEXT, '-', ''), 1, 6);
    RETURN code;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================
-- Enable RLS on tables (uncomment when using Supabase Auth)

-- ALTER TABLE sellers ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE listings ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE blog_posts ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE analytics ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE sync_logs ENABLE ROW LEVEL SECURITY;

-- Example policies (customize based on your auth setup)

-- Sellers can read their own data
-- CREATE POLICY "Sellers can view own profile" ON sellers
--     FOR SELECT USING (auth.uid() = id);

-- Sellers can update their own profile
-- CREATE POLICY "Sellers can update own profile" ON sellers
--     FOR UPDATE USING (auth.uid() = id);

-- Anyone can view active listings
-- CREATE POLICY "Anyone can view active listings" ON listings
--     FOR SELECT USING (status = 'active');

-- Sellers can manage their own listings
-- CREATE POLICY "Sellers can manage own listings" ON listings
--     FOR ALL USING (auth.uid() = seller_id);

-- Anyone can read published blog posts
-- CREATE POLICY "Anyone can read published blog posts" ON blog_posts
--     FOR SELECT USING (status = 'published');

-- ============================================================================
-- SAMPLE DATA (for testing)
-- ============================================================================
-- Uncomment to insert sample data after creating tables

-- INSERT INTO sellers (email, full_name, region, hashed_password, is_verified, referral_code) VALUES
-- ('jane@example.com', 'Jane Doe', 'Los Angeles, USA', '$2b$12$...hashed...', true, 'VJJANE123456'),
-- ('john@example.com', 'John Smith', 'New York, USA', '$2b$12$...hashed...', true, 'VJJOHN789012');

-- INSERT INTO listings (seller_id, title, description, brand, era, size, price, condition, status, image_urls) VALUES
-- (
--     (SELECT id FROM sellers WHERE email = 'jane@example.com'),
--     'Vintage Levi''s 501 Jeans 1950s Selvedge Denim',
--     'Rare 1950s Levi''s 501 with original selvedge, Big E tab, hidden rivets. Excellent condition with minimal fading.',
--     'Levi''s',
--     '1950s',
--     '32x34',
--     450.00,
--     'excellent',
--     'active',
--     ARRAY['https://example.com/image1.jpg', 'https://example.com/image2.jpg']
-- );

-- ============================================================================
-- NOTES FOR DEPLOYMENT
-- ============================================================================
-- 1. Run this SQL in Supabase SQL Editor
-- 2. Generate anon and service_role keys from Supabase dashboard
-- 3. Configure RLS policies based on your authentication method
-- 4. Set up environment variables in Render for backend:
--    - SUPABASE_URL
--    - SUPABASE_KEY (service_role for backend)
-- 5. Use anon key for frontend client-side operations (if applicable)
