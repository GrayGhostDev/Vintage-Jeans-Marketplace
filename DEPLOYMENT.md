# 🚀 Vintage Jeans Marketplace - Deployment Guide

Complete guide for deploying the Vintage Jeans Marketplace to production using Supabase, Render, and Vercel.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Supabase Setup](#supabase-setup)
4. [Backend Deployment (Render)](#backend-deployment-render)
5. [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
6. [Post-Deployment](#post-deployment)
7. [Troubleshooting](#troubleshooting)

---

## Overview

### Architecture

```
┌─────────────┐      ┌─────────────┐      ┌──────────────┐
│   Vercel    │─────▶│   Render    │─────▶│   Supabase   │
│  (Frontend) │      │  (Backend)  │      │ (PostgreSQL) │
│  React/Vite │      │   FastAPI   │      │   Database   │
└─────────────┘      └─────────────┘      └──────────────┘
```

### Tech Stack

- **Database**: Supabase (PostgreSQL with UUID primary keys)
- **Backend**: FastAPI on Render (Python 3.13)
- **Frontend**: React 18 + Vite 5 on Vercel
- **Authentication**: JWT with passlib + bcrypt

---

## Prerequisites

### Required Accounts

- [ ] [Supabase](https://supabase.com) account (free tier available)
- [ ] [Render](https://render.com) account (free tier available)
- [ ] [Vercel](https://vercel.com) account (free tier available)
- [ ] GitHub account for repository hosting

### Required Tools

```bash
# Node.js 18+ and npm
node --version  # Should be v18 or higher
npm --version

# Python 3.9+
python3 --version  # Should be 3.9 or higher

# Git
git --version

# Supabase CLI (optional, for local development)
npx supabase --version
```

---

## Supabase Setup

### Step 1: Create a New Supabase Project

1. Go to [https://supabase.com/dashboard](https://supabase.com/dashboard)
2. Click "New Project"
3. Fill in project details:
   - **Name**: `vintage-jeans-marketplace`
   - **Database Password**: Generate a strong password and save it
   - **Region**: Choose closest to your users
   - **Plan**: Free tier is sufficient to start

### Step 2: Run Database Schema

1. Navigate to **SQL Editor** in Supabase dashboard
2. Create a new query
3. Copy the contents of `backend/database/supabase_schema.sql`
4. Paste and click **Run**
5. Verify tables were created in **Table Editor**

Expected tables:
- `sellers` (with UUID primary key)
- `listings` (with UUID primary key and seller_id foreign key)
- `blog_posts` (with UUID primary key and author_id foreign key)

### Step 3: Get Supabase Credentials

From your Supabase project dashboard:

1. Go to **Settings** → **API**
2. Copy these values:

```
Project URL: https://xxxxxxxxxxxxx.supabase.co
anon/public key: eyJhbGc...  (for frontend)
service_role key: eyJhbGc...  (for backend - KEEP SECRET!)
```

### Step 4: Enable Row Level Security (RLS) Policies

The schema includes RLS policies, but verify they're enabled:

1. Go to **Authentication** → **Policies**
2. Ensure policies are active for:
   - `sellers` table
   - `listings` table
   - `blog_posts` table

---

## Backend Deployment (Render)

### Step 1: Prepare Repository

Ensure your GitHub repository has:
- `backend/` directory with all FastAPI code
- `backend/requirements.txt` with dependencies
- `render.yaml` in project root

### Step 2: Connect to Render

1. Go to [https://dashboard.render.com](https://dashboard.render.com)
2. Click "New +" → "Blueprint"
3. Connect your GitHub repository
4. Render will detect `render.yaml` automatically

### Step 3: Configure Environment Variables

In Render dashboard, go to your service and add these environment variables:

```bash
# Supabase Configuration
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=your-service-role-key-here

# Authentication & Security
JWT_SECRET_KEY=<generate with: openssl rand -hex 32>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# AI Configuration (Optional)
OPENAI_API_KEY=sk-proj-your-key-here
OPENAI_MODEL=gpt-4-turbo

# CORS Configuration
ALLOWED_ORIGINS=https://your-vercel-app.vercel.app,https://vintage-jeans.vercel.app

# Application
ENVIRONMENT=production
DEBUG=false
```

### Step 4: Generate Secure Secrets

```bash
# Generate JWT secret
openssl rand -hex 32

# Generate database password (if not using Supabase-generated)
openssl rand -base64 32
```

### Step 5: Deploy

1. Click "Create Web Service" or "Deploy Latest Commit"
2. Wait for build to complete (~2-5 minutes)
3. Render will automatically deploy from `main` branch

### Step 6: Verify Deployment

Test the health endpoint:

```bash
curl https://your-app.onrender.com/api/health
```

Expected response:
```json
{
  "status": "ok",
  "service": "vintage-jeans-api",
  "version": "2.0.0",
  "database": {
    "status": "ok",
    "database": "supabase",
    "connected": true
  }
}
```

---

## Frontend Deployment (Vercel)

### Step 1: Prepare Repository

Ensure your repository has:
- `frontend/` directory with React/Vite code
- `frontend/vercel.json` configuration
- `frontend/package.json` with build scripts

### Step 2: Connect to Vercel

1. Go to [https://vercel.com/dashboard](https://vercel.com/dashboard)
2. Click "Add New Project"
3. Import your GitHub repository
4. Select `frontend/` as the root directory

### Step 3: Configure Build Settings

Vercel should auto-detect Vite, but verify:

```
Framework Preset: Vite
Build Command: npm run build
Output Directory: dist
Install Command: npm install
```

### Step 4: Configure Environment Variables

In Vercel project settings → Environment Variables, add:

```bash
# API Configuration
VITE_API_URL=https://your-render-app.onrender.com/api

# Supabase Configuration (optional, for direct client access)
VITE_SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key-here

# Application Settings
VITE_APP_NAME=Vintage Jeans Marketplace
VITE_ENVIRONMENT=production
```

**Important**: In Vite, only variables prefixed with `VITE_` are exposed to the client.

### Step 5: Deploy

1. Click "Deploy"
2. Vercel will build and deploy automatically
3. Your app will be live at `https://your-project.vercel.app`

### Step 6: Configure Custom Domain (Optional)

1. Go to Project Settings → Domains
2. Add your custom domain
3. Follow Vercel's DNS configuration instructions
4. Update `ALLOWED_ORIGINS` in Render to include your custom domain

---

## Post-Deployment

### 1. Update CORS Configuration

In Render, update `ALLOWED_ORIGINS` to include your Vercel domain:

```bash
ALLOWED_ORIGINS=https://your-app.vercel.app
```

### 2. Create Admin User

Use the API to create your first admin seller:

```bash
curl -X POST https://your-render-app.onrender.com/api/sellers/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@vintagejeans.com",
    "password": "secure_password",
    "full_name": "Admin User",
    "location": "Los Angeles, CA"
  }'
```

Then manually update the seller role in Supabase:

```sql
UPDATE sellers
SET role = 'admin', is_verified = true
WHERE email = 'admin@vintagejeans.com';
```

### 3. Test Critical Flows

#### Authentication Flow

```bash
# 1. Register a seller
curl -X POST https://your-app.onrender.com/api/sellers/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123",
    "full_name": "Test Seller",
    "location": "New York, NY"
  }'

# 2. Login
curl -X POST https://your-app.onrender.com/api/sellers/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=test123"

# 3. Get profile (use token from login response)
curl https://your-app.onrender.com/api/sellers/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

#### Listing Flow

```bash
# Create a listing (requires auth token)
curl -X POST https://your-app.onrender.com/api/listings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "title": "Vintage Levis 501 1990s",
    "description": "Excellent condition vintage jeans",
    "brand": "Levis",
    "condition": "excellent",
    "price": 85.00,
    "waist_size": 32,
    "inseam_length": 32
  }'

# List all listings (public)
curl https://your-app.onrender.com/api/listings
```

### 4. Monitor Services

- **Render Dashboard**: Monitor backend health, logs, and metrics
- **Vercel Dashboard**: Monitor frontend deployments and analytics
- **Supabase Dashboard**: Monitor database usage and query performance

### 5. Set Up CI/CD (Optional)

Both Render and Vercel auto-deploy from your repository:

```bash
# Render: Deploys from 'main' branch automatically
git push origin main

# Vercel: Deploys preview for all branches, production for 'main'
git push origin feature-branch  # Creates preview deployment
git push origin main            # Deploys to production
```

---

## Troubleshooting

### Backend Issues

#### 1. "ModuleNotFoundError: No module named 'supabase'"

```bash
# Verify requirements.txt includes:
supabase>=2.0.0

# Rebuild on Render to install dependencies
```

#### 2. "Could not validate credentials" when accessing protected endpoints

- Verify `JWT_SECRET_KEY` is set correctly in Render
- Check token expiration (`ACCESS_TOKEN_EXPIRE_MINUTES`)
- Ensure token is sent in header: `Authorization: Bearer <token>`

#### 3. Database connection errors

```python
# Check SUPABASE_URL and SUPABASE_KEY are correct
# Verify Supabase project is active
# Test connection from backend logs
```

### Frontend Issues

#### 1. CORS errors in browser

```
Access to XMLHttpRequest blocked by CORS policy
```

**Solution**: Add your Vercel domain to `ALLOWED_ORIGINS` in Render:

```bash
ALLOWED_ORIGINS=https://your-app.vercel.app
```

#### 2. API_URL environment variable not found

```
VITE_API_URL is undefined
```

**Solution**: Ensure variable is prefixed with `VITE_` in Vercel settings.

#### 3. Build fails with "Cannot find module"

```bash
# Clear Vercel build cache
# Re-run deployment

# Or locally test build:
cd frontend
npm install
npm run build
```

### Database Issues

#### 1. UUID generation errors

```sql
-- Enable uuid-ossp extension (should be enabled by default)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Verify extension is installed
SELECT * FROM pg_extension WHERE extname = 'uuid-ossp';
```

#### 2. RLS policies blocking queries

```sql
-- Temporarily disable RLS for testing (NOT for production)
ALTER TABLE sellers DISABLE ROW LEVEL SECURITY;

-- Re-enable after fixing policies
ALTER TABLE sellers ENABLE ROW LEVEL SECURITY;
```

#### 3. Foreign key constraint violations

```sql
-- Check if seller_id exists before creating listing
SELECT id FROM sellers WHERE id = 'uuid-here';

-- Verify foreign key constraints
SELECT * FROM information_schema.table_constraints
WHERE constraint_type = 'FOREIGN KEY';
```

---

## Security Checklist

Before going live:

- [ ] Change all default passwords
- [ ] Use strong, unique `JWT_SECRET_KEY`
- [ ] Use service_role key for backend, anon key for frontend
- [ ] Enable RLS policies on all tables
- [ ] Set up HTTPS (automatic on Render/Vercel)
- [ ] Limit `ALLOWED_ORIGINS` to production domains only
- [ ] Never commit `.env` files with real credentials
- [ ] Set up database backups in Supabase
- [ ] Enable rate limiting (future enhancement)
- [ ] Monitor logs for suspicious activity

---

## Performance Optimization

### Backend

```python
# Use connection pooling (handled by Supabase client)
# Implement caching for frequently accessed data
# Add database indexes for common queries

# In Supabase, add indexes:
CREATE INDEX idx_listings_status ON listings(status);
CREATE INDEX idx_listings_seller ON listings(seller_id);
CREATE INDEX idx_blog_status ON blog_posts(status, published_at);
```

### Frontend

```bash
# Enable gzip compression (automatic on Vercel)
# Implement lazy loading for images
# Use React.lazy for code splitting
# Cache API responses with React Query or SWR
```

---

## Scaling Considerations

### Current Limits (Free Tier)

- **Supabase**: 500 MB database, 2 GB bandwidth
- **Render**: 512 MB RAM, sleeps after 15 min inactivity
- **Vercel**: 100 GB bandwidth, 1000 build minutes/month

### When to Upgrade

- **Database**: > 400 MB or slow queries
- **Backend**: Cold starts taking > 30 seconds
- **Frontend**: > 80 GB bandwidth usage

### Upgrade Path

1. **Supabase Pro** ($25/mo): 8 GB database, 250 GB bandwidth
2. **Render Starter** ($7/mo): No cold starts, custom domains
3. **Vercel Pro** ($20/mo): Priority support, advanced analytics

---

## Monitoring & Maintenance

### Daily Checks

- Backend health endpoint returns 200 OK
- Frontend loads without errors
- Database size under limit

### Weekly Tasks

- Review error logs in Render
- Check Supabase database usage
- Monitor API response times

### Monthly Tasks

- Update dependencies (`npm update`, `pip install -U`)
- Review and archive old listings
- Backup database (Supabase handles automatically)

---

## Support & Resources

### Documentation

- [Supabase Docs](https://supabase.com/docs)
- [Render Docs](https://render.com/docs)
- [Vercel Docs](https://vercel.com/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com/)

### Community

- Supabase Discord: https://discord.supabase.com
- Render Community: https://community.render.com
- Vercel Discussions: https://github.com/vercel/vercel/discussions

---

## Deployment Complete! 🎉

Your Vintage Jeans Marketplace is now live!

- **Frontend**: https://your-app.vercel.app
- **Backend**: https://your-app.onrender.com
- **Database**: Supabase Dashboard

**Next Steps:**

1. Add your first admin user
2. Create sample listings
3. Test all user flows
4. Share with beta testers
5. Monitor performance and iterate

Good luck with your marketplace! 🚀👖
