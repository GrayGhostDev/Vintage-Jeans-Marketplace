# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Vintage Jeans Marketplace Platform** is an AI-powered marketplace for vintage and slightly-used jeans. The platform enables sellers to list inventory (manual or via API sync), provides AI-driven market analytics, tracks ROI opportunities, and supports multi-platform integrations (eBay, Etsy, Whatnot).

**Tech Stack:**
- **Backend:** FastAPI (Python 3.13), SQLModel ORM, SQLite (dev) / PostgreSQL (prod)
- **Frontend:** React 18 + TypeScript, Vite 5, Tailwind CSS, TanStack React Query
- **AI:** OpenAI GPT-5 for market insights
- **Auth:** JWT with passlib bcrypt
- **Background Tasks:** Celery + Redis (planned)

## Project Structure

```
Vintage-Jeans/
├── backend/                          # FastAPI application
│   ├── main.py                       # App entry point with CORS, lifespan, routers
│   ├── requirements.txt              # Python dependencies
│   ├── .env.example                  # Environment template
│   ├── vintage_jeans.db              # SQLite database (auto-created)
│   └── research/
│       ├── models/                   # SQLModel database models
│       │   ├── seller.py             # Seller accounts + OAuth tokens
│       │   ├── listing.py            # Normalized listing schema + enums
│       │   ├── analytics.py          # Analytics, Insight, SyncLog models
│       │   └── research_model.py     # ResearchSummary (legacy)
│       ├── routers/
│       │   ├── seller_router.py      # /api/sellers (register, login, profile)
│       │   ├── listing_router.py     # /api/listings (CRUD, approval)
│       │   └── research_router.py    # /api/research (legacy upload)
│       ├── services/
│       │   ├── auth_service.py       # JWT auth, password hashing
│       │   ├── ai_summary_service.py # OpenAI GPT-5 calls
│       │   └── db_service.py         # Database helpers
│       └── db/
│           ├── base.py               # SQLModel base (unused, replaced)
│           └── session.py            # Engine, get_session(), init_db()
├── frontend/                         # React application
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Landing.tsx           # Marketing landing page
│   │   │   ├── Login.tsx             # Seller authentication
│   │   │   ├── Register.tsx          # Seller registration
│   │   │   ├── SellForm.tsx          # Public listing submission
│   │   │   ├── SellerDashboard.tsx   # Seller KPIs, listings table
│   │   │   └── AdminDashboard.tsx    # Admin approval queue, analytics
│   │   ├── lib/
│   │   │   ├── api.ts                # Axios client + API functions
│   │   │   ├── auth.tsx              # AuthProvider + useAuth hook
│   │   │   └── utils.ts              # Utility functions (formatCurrency, calculateROI)
│   │   ├── App.tsx                   # Router, AuthProvider, PrivateRoute
│   │   ├── main.tsx                  # React entry with QueryClientProvider
│   │   └── index.css                 # Tailwind CSS + theme variables
│   ├── package.json                  # Frontend dependencies
│   ├── vite.config.ts                # Vite config with API proxy
│   ├── tailwind.config.js            # Tailwind theme configuration
│   └── tsconfig.json                 # TypeScript configuration
├── data/                             # Data pipeline
│   ├── raw/                          # Unprocessed API data
│   ├── processed/                    # Normalized listings
│   └── insights/                     # AI-generated reports
├── docs/
│   └── Vintage-Jeans-Research-Workflow.md  # Platform strategy doc
├── README.md                         # Setup and development guide
└── CLAUDE.md                         # This file
```

## Common Commands

### Backend Development
```bash
# Navigate to backend
cd backend

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload

# Run with custom host/port
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Backend runs on http://localhost:8000
- API Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

### Frontend Development
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

Frontend runs on http://localhost:5173 (proxies `/api` requests to backend)

### Database Operations
Database is auto-initialized on backend startup via `init_db()` in `session.py`. Tables are created from SQLModel metadata.

```bash
# Database file location (SQLite dev mode)
backend/vintage_jeans.db

# Switch to PostgreSQL (production)
# Set DATABASE_URL in .env:
DATABASE_URL=postgresql://user:password@localhost:5432/vintage_jeans
```

## Architecture Overview

### Backend Architecture

**Request Flow:**
1. Client sends request to FastAPI endpoint
2. CORS middleware validates origin
3. Router receives request, validates with Pydantic models
4. Auth dependency (`get_current_seller`) validates JWT token
5. Service layer performs business logic
6. SQLModel handles database operations
7. Response returned as Pydantic model

**Authentication Flow:**
1. User registers: `POST /api/sellers/register` → creates Seller with hashed password
2. User logs in: `POST /api/sellers/login` → returns JWT + seller data
3. Frontend stores JWT in localStorage
4. Protected routes use JWT in Authorization header
5. `get_current_seller` dependency validates token on each request

**Database Models:**

```python
# Seller (seller.py)
- id, email, hashed_password, full_name, business_name, location
- OAuth tokens for eBay, Etsy, Whatnot (access_token, refresh_token, expires_at)
- Metrics: total_listings, active_listings, total_sales, total_revenue
- Referral: referral_code, referred_by
- Timestamps: created_at, updated_at, last_login_at

# Listing (listing.py)
- id, seller_id, platform (enum), platform_listing_id
- Product: brand, decade, model, waist_size, inseam_length
- Condition: condition (enum), condition_notes
- Pricing: price, currency, purchase_price, shipping_cost
- Images: primary_image_url, image_urls (JSON)
- Status: status (enum), approved_by, approved_at, rejection_reason
- Metrics: views, favorites, sale_price, sold_at, sold_to_country
- SEO: provenance, is_featured, tags (JSON)

# Analytics (analytics.py)
- Aggregated metrics by time period + platform
- Price trends: avg_listing_price, median_listing_price, avg_sale_price
- Brand/decade breakdowns (JSON)
- ROI: avg_roi_percentage, total_profit, high_roi_opportunities
- Geographic: top_buyer_countries, top_seller_locations

# Insight (analytics.py)
- AI-generated insights: insight_type, title, summary, detailed_analysis
- Confidence: confidence_score (0-1), data_source
- Actionability: action_items (JSON), estimated_impact
- Targeting: product_category, recommended_price_range, target_market

# SyncLog (analytics.py)
- Platform sync tracking: platform, sync_type, status
- Results: items_fetched, items_created, items_updated, items_failed
- Performance: started_at, completed_at, duration_seconds, api_calls_made
```

### Frontend Architecture

**Component Hierarchy:**
```
App (AuthProvider, Router)
├── Landing (public)
├── Login (public)
├── Register (public)
├── SellForm (public)
├── SellerDashboard (PrivateRoute)
│   ├── KPI Cards (total/active listings, referral code)
│   ├── AI Recommendations Panel
│   └── Listings Table (brand, price, status, ROI, views)
└── AdminDashboard (PrivateRoute, requireAdmin)
    ├── Platform KPIs (sellers, listings, pending, avg ROI)
    ├── Approval Queue
    ├── Platform Analytics
    └── Market Insights
```

**State Management:**
- **Global Auth:** `AuthProvider` in `lib/auth.tsx` manages user state
- **Server State:** TanStack React Query for API data fetching
- **Local State:** useState for form inputs, UI state

**API Client:**
```typescript
// lib/api.ts structure
- axios instance with baseURL='/api'
- Request interceptor: adds Bearer token from localStorage
- Response interceptor: handles 401 (redirect to login)
- API functions grouped by resource:
  - auth: register, login, getMe, updateProfile
  - listings: list, get, create, update, delete, approve, reject
```

## Key Implementation Details

### Authentication System
Located in `backend/research/services/auth_service.py`:
- **Password Hashing:** Uses passlib with bcrypt
- **JWT Creation:** python-jose with HS256 algorithm
- **Token Validation:** Decodes JWT, fetches Seller from DB
- **Dependencies:**
  - `get_current_seller`: Validates token, returns Seller
  - `get_current_admin`: Validates token + checks role == "admin"

### Database Session Management
Located in `backend/research/db/session.py`:
- **Engine Creation:** SQLite with check_same_thread=False
- **Model Registration:** Imports all models to register with SQLModel.metadata
- **get_session():** Returns Session context manager
- **init_db():** Creates all tables via SQLModel.metadata.create_all()

### CORS Configuration
In `backend/main.py`:
- Allows origins: http://localhost:5173 (Vite dev server), http://localhost:3000
- Credentials: true (for cookies/auth headers)
- Methods: all
- Headers: all

### Frontend Routing & Guards
In `frontend/src/App.tsx`:
- **PrivateRoute Component:** Checks user auth, redirects to /login if not authenticated
- **Admin Guard:** `requireAdmin` prop checks user.role === 'admin'
- **Loading State:** Shows loading screen while auth status is determined

## Environment Variables

See `backend/.env.example` for full list. Key variables:

**Required:**
```bash
OPENAI_API_KEY=sk-proj-...           # OpenAI API key for GPT-5
JWT_SECRET_KEY=your-secret-key       # Generate with: openssl rand -hex 32
```

**Optional:**
```bash
DATABASE_URL=sqlite:///./vintage_jeans.db  # or postgresql://...
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REDIS_URL=redis://localhost:6379/0

# OAuth Credentials (for Phase 2)
EBAY_CLIENT_ID=...
EBAY_CLIENT_SECRET=...
ETSY_CLIENT_ID=...
ETSY_CLIENT_SECRET=...
WHATNOT_CLIENT_ID=...
WHATNOT_CLIENT_SECRET=...
```

## API Endpoints Reference

### Sellers (`/api/sellers`)
- `POST /register` - Create seller account (returns SellerResponse)
- `POST /login` - Authenticate (returns TokenResponse with access_token + seller)
- `GET /me` - Get current seller profile (requires auth)
- `PATCH /me` - Update profile (requires auth)
- `GET /all` - List all sellers (admin only)
- `PATCH /{seller_id}/verify` - Verify seller (admin only)

### Listings (`/api/listings`)
- `GET /` - List listings with filters (seller sees own, admin sees all)
  - Query params: skip, limit, platform, status_filter, brand, decade, seller_id
- `POST /` - Create listing (requires auth, sets platform=manual)
- `GET /{listing_id}` - Get listing details (increments view count)
- `PATCH /{listing_id}` - Update listing (owner or admin)
- `DELETE /{listing_id}` - Delete listing (owner or admin)
- `POST /{listing_id}/approve` - Approve listing (admin only)
- `POST /{listing_id}/reject` - Reject with reason (admin only)

### Research (Legacy) (`/api/research`)
- `POST /upload` - Upload research document for AI analysis

## Development Workflow

### Adding a New Feature
1. **Backend:** Create/update SQLModel in `research/models/`
2. **Backend:** Add route handler in `research/routers/`
3. **Backend:** Register router in `main.py`
4. **Frontend:** Add API function in `lib/api.ts`
5. **Frontend:** Create React Query hook or component
6. **Frontend:** Add UI component/page

### Testing Flow
1. Start backend: `uvicorn main:app --reload`
2. Test endpoints in http://localhost:8000/docs
3. Start frontend: `npm run dev`
4. Test full flow in browser at http://localhost:5173

## Current Limitations & TODOs

### Backend
- No Alembic migrations (using SQLModel auto-create)
- No async database operations (using sync Session)
- No pagination on some list endpoints
- No rate limiting
- No comprehensive error handling/logging
- OAuth integrations not implemented (Phase 2)
- Celery background tasks not implemented (Phase 3)

### Frontend
- No form validation library (using HTML5 validation)
- No shadcn/ui components installed yet
- No charts library integrated (Recharts planned)
- No image upload functionality
- No real-time updates (websockets/polling)
- Dashboard data is placeholder/mocked in some areas

## Phase 2 Priorities (Next Steps)

1. **API Integrations:**
   - Create `backend/research/integrations/` module
   - Implement eBay OAuth flow + REST client
   - Implement Etsy OAuth flow + REST client
   - Implement Whatnot GraphQL client
   - Add OAuth callback routes in seller_router

2. **Background Sync:**
   - Set up Celery + Redis
   - Create sync tasks in `backend/research/tasks/sync_tasks.py`
   - Add scheduled jobs for hourly/daily syncs
   - Implement webhook handlers

3. **Analytics Engine:**
   - Expand `ai_summary_service.py` for analytics
   - Create analytics_router with endpoints
   - Build enrichment Celery tasks
   - Calculate ROI opportunities

4. **Frontend Polish:**
   - Install shadcn/ui components
   - Add Recharts for data visualization
   - Build out admin dashboard analytics
   - Add listing creation form with image upload

## Design Patterns & Conventions

### Backend
- **Models:** Use SQLModel for Pydantic + SQLAlchemy
- **Routers:** Group by resource, use APIRouter
- **Auth:** Dependency injection via Depends()
- **Responses:** Return Pydantic models (not SQLModel tables directly)
- **Errors:** Raise HTTPException with status codes

### Frontend
- **Components:** Functional components with hooks
- **Styling:** Tailwind utility classes
- **State:** React Query for server state, useState for local
- **Types:** Import types from `lib/api.ts`
- **Auth:** Use `useAuth()` hook from context

### Naming Conventions
- **Backend:** snake_case for files, functions, variables
- **Frontend:** PascalCase for components, camelCase for functions
- **Database:** snake_case for column names
- **Enums:** PascalCase with value as snake_case

## ROI Calculation & Market Strategy

The platform focuses on identifying arbitrage opportunities:
- **Example:** 1950s Levi's 501 bought for $50 in US → sold for $2,500 in Japan = 4,900% ROI
- **Key Markets:** Japan (premium for vintage US denim), Europe (sustainable fashion)
- **Threshold Tracking:** Japan duty-free limit ~¥200,000

ROI formula (in `lib/utils.ts` and future analytics):
```typescript
roi = ((sale_price - purchase_price - shipping_cost) / purchase_price) * 100
```

## Resources

- **FastAPI Docs:** https://fastapi.tiangolo.com
- **SQLModel Docs:** https://sqlmodel.tiangolo.com
- **React Query Docs:** https://tanstack.com/query/latest
- **Tailwind CSS:** https://tailwindcss.com
- **Marketplace APIs:**
  - eBay: https://developer.ebay.com
  - Etsy: https://developers.etsy.com
  - Whatnot: https://developers.whatnot.com

---

*Last Updated: 2025-11-03*
*Version: 2.0.0 (Full Platform Implementation)*
