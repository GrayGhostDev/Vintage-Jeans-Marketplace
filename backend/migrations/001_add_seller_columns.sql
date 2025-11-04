-- Migration: Add missing columns to sellers table
-- Date: 2025-11-04
-- Description: Add location, phone, business_name, referred_by, and updated_at columns

-- Add location column (required field)
ALTER TABLE sellers
ADD COLUMN IF NOT EXISTS location TEXT;

-- Add optional profile columns
ALTER TABLE sellers
ADD COLUMN IF NOT EXISTS phone TEXT,
ADD COLUMN IF NOT EXISTS business_name TEXT;

-- Add referral tracking
ALTER TABLE sellers
ADD COLUMN IF NOT EXISTS referred_by UUID REFERENCES sellers(id) ON DELETE SET NULL;

-- Add updated_at timestamp
ALTER TABLE sellers
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Create index on referral_code for faster lookups
CREATE INDEX IF NOT EXISTS idx_sellers_referral_code ON sellers(referral_code);

-- Create index on referred_by for analytics
CREATE INDEX IF NOT EXISTS idx_sellers_referred_by ON sellers(referred_by);

-- Add trigger to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Drop trigger if exists, then recreate
DROP TRIGGER IF EXISTS update_sellers_updated_at ON sellers;

CREATE TRIGGER update_sellers_updated_at
    BEFORE UPDATE ON sellers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
