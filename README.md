# Vintage Jeans Marketplace Platform

AI-powered vintage jeans marketplace with seller onboarding, listing management, marketplace integrations, and market analytics.

## Project Overview

The Vintage Jeans Marketplace Platform enables sellers to list vintage and slightly-used jeans, aggregates inventory from third-party marketplaces (eBay, Etsy, Whatnot), and provides AI-driven analytics for both sellers and administrators.

**Key Features:**
- Seller registration and authentication (JWT-based)
- Manual listing creation with detailed product attributes
- Multi-platform sync (eBay, Etsy, Whatnot APIs - in development)
- AI-powered market insights using OpenAI GPT-5
- ROI tracking and arbitrage opportunity identification
- Admin approval workflow for listings
- Seller and admin dashboards with analytics

## Tech Stack

### Backend
- **Framework:** FastAPI (Python 3.13)
- **Database:** SQLite (dev) / PostgreSQL (prod)
- **ORM:** SQLModel (Pydantic + SQLAlchemy)
- **Authentication:** JWT with passlib bcrypt
- **AI/Analytics:** OpenAI GPT-5, Pandas
- **Background Tasks:** Celery + Redis (planned)

### Frontend
- **Framework:** React 18 with TypeScript
- **Build Tool:** Vite 5
- **Styling:** Tailwind CSS 3.4
- **State Management:** TanStack React Query
- **Routing:** React Router 6
- **Charts:** Recharts (planned)
- **UI Components:** shadcn/ui (Radix UI primitives)

## Getting Started

### Prerequisites
- Python 3.12+ (3.13 recommended)
- Node.js 20+ LTS
- PostgreSQL 16 (for production) or SQLite (for development)
- Redis 7 (for background tasks - optional)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   # or
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY and other credentials
   ```

5. **Initialize database:**
   ```bash
   # Database will be auto-created on first run
   # Tables are created via SQLModel metadata
   ```

6. **Run development server:**
   ```bash
   uvicorn main:app --reload
   ```

   API will be available at: `http://localhost:8000`
   - Interactive API docs: `http://localhost:8000/docs`
   - Alternative docs: `http://localhost:8000/redoc`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Run development server:**
   ```bash
   npm run dev
   ```

   Frontend will be available at: `http://localhost:5173`

### Development Workflow

1. **Start backend:**
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn main:app --reload
   ```

2. **Start frontend (in separate terminal):**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Access the application:**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Project Structure

```
Vintage-Jeans/
├── backend/                          # FastAPI application
│   ├── main.py                       # Application entry point with CORS and lifespan
│   ├── requirements.txt              # Python dependencies
│   ├── .env.example                  # Environment variables template
│   └── research/
│       ├── models/                   # SQLModel database models
│       │   ├── seller.py             # Seller accounts with OAuth tokens
│       │   ├── listing.py            # Normalized listing schema
│       │   ├── analytics.py          # Analytics, Insights, SyncLog
│       │   └── research_model.py     # Original research summary model
│       ├── routers/                  # API route handlers
│       │   ├── seller_router.py      # Registration, auth, profile
│       │   ├── listing_router.py     # CRUD, approval workflow
│       │   └── research_router.py    # Research document upload
│       ├── services/
│       │   ├── auth_service.py       # JWT authentication
│       │   ├── ai_summary_service.py # OpenAI GPT-5 integration
│       │   └── db_service.py         # Database operations
│       └── db/
│           ├── base.py               # SQLModel base
│           └── session.py            # Database engine and session
├── frontend/                         # React application
│   ├── src/
│   │   ├── pages/                    # Page components
│   │   │   ├── Landing.tsx           # Marketing landing page
│   │   │   ├── Login.tsx             # Seller login
│   │   │   ├── Register.tsx          # Seller registration
│   │   │   ├── SellForm.tsx          # Public listing submission
│   │   │   ├── SellerDashboard.tsx   # Seller analytics & listings
│   │   │   └── AdminDashboard.tsx    # Admin approval & analytics
│   │   ├── lib/
│   │   │   ├── api.ts                # Axios API client
│   │   │   ├── auth.tsx              # Auth context provider
│   │   │   └── utils.ts              # Utility functions
│   │   ├── App.tsx                   # Router and auth provider
│   │   ├── main.tsx                  # React entry point
│   │   └── index.css                 # Tailwind styles
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── tsconfig.json
├── data/                             # Data pipeline directories
│   ├── raw/                          # Unfiltered API data
│   ├── processed/                    # Normalized data
│   └── insights/                     # AI-generated reports
├── docs/                             # Documentation
│   └── Vintage-Jeans-Research-Workflow.md
└── README.md
```

## API Endpoints

### Authentication & Sellers
- `POST /api/sellers/register` - Create seller account
- `POST /api/sellers/login` - Authenticate and get JWT token
- `GET /api/sellers/me` - Get current seller profile
- `PATCH /api/sellers/me` - Update seller profile
- `GET /api/sellers/all` - List all sellers (admin only)
- `PATCH /api/sellers/{seller_id}/verify` - Verify seller (admin only)

### Listings
- `GET /api/listings` - List listings with filters
- `POST /api/listings` - Create new listing
- `GET /api/listings/{id}` - Get listing details
- `PATCH /api/listings/{id}` - Update listing
- `DELETE /api/listings/{id}` - Delete listing
- `POST /api/listings/{id}/approve` - Approve listing (admin only)
- `POST /api/listings/{id}/reject` - Reject listing (admin only)

### Research (Legacy)
- `POST /api/research/upload` - Upload research document for AI analysis

## Database Schema

### Seller
- Authentication (email, hashed_password)
- Profile (full_name, business_name, location)
- OAuth tokens (ebay, etsy, whatnot)
- Metrics (total_listings, active_listings, total_sales, total_revenue)
- Referral system (referral_code, referred_by)

### Listing
- Platform metadata (platform, platform_listing_id, platform_url)
- Product attributes (brand, decade, model, waist_size, inseam_length)
- Condition grading (condition, condition_notes)
- Pricing (price, currency, purchase_price, shipping_cost)
- Images (primary_image_url, image_urls)
- Status workflow (status, approved_by, approved_at)
- Metrics (views, favorites, sale_price, sold_at)
- Provenance and SEO (provenance, is_featured, tags)

### Analytics
- Aggregated metrics by time period and platform
- Price trends and ROI calculations
- Brand/decade/category distributions
- Geographic insights

### Insight
- AI-generated market opportunities
- Pricing suggestions
- Trend alerts
- Seller-specific recommendations

### SyncLog
- API sync tracking (platform, sync_type, status)
- Performance metrics (items_fetched, items_created, duration_seconds)
- Error handling (error_message, error_details)

## Environment Variables

See `backend/.env.example` for complete list. Key variables:

```bash
# Required
OPENAI_API_KEY=sk-proj-...
JWT_SECRET_KEY=your-secret-key

# Optional
DATABASE_URL=sqlite:///./vintage_jeans.db
REDIS_URL=redis://localhost:6379/0

# OAuth (for marketplace integrations)
EBAY_CLIENT_ID=...
EBAY_CLIENT_SECRET=...
ETSY_CLIENT_ID=...
ETSY_CLIENT_SECRET=...
WHATNOT_CLIENT_ID=...
WHATNOT_CLIENT_SECRET=...
```

## Development Roadmap

### Phase 1: Core Infrastructure ✅ (Completed)
- [x] Backend scaffolding with FastAPI
- [x] Database models (Seller, Listing, Analytics, Insight, SyncLog)
- [x] Authentication system (JWT)
- [x] Seller and listing CRUD endpoints
- [x] Frontend React/Vite setup
- [x] Landing, auth, and dashboard pages
- [x] API client and auth context

### Phase 2: API Integrations & Data Sync (In Progress)
- [ ] eBay OAuth and API client
- [ ] Etsy OAuth and API client
- [ ] Whatnot GraphQL client
- [ ] Background sync service (Celery)
- [ ] Webhook handlers
- [ ] Data normalization pipeline

### Phase 3: Analytics & AI Engine (Planned)
- [ ] Enrichment jobs (Celery tasks)
- [ ] GPT-5 analytics expansion
- [ ] Analytics endpoints
- [ ] Dashboard charts (Recharts)
- [ ] ROI calculation engine

### Phase 4: Seller Acquisition & Marketing (Planned)
- [ ] Referral system activation
- [ ] Social media integration
- [ ] Email campaigns
- [ ] Pilot seller program

### Phase 5: Future Enhancements
- [ ] Payment integration (Stripe)
- [ ] Verification & grading system
- [ ] International shipping
- [ ] Mobile app (React Native)

## Contributing

This is a client project. External contributions are not currently accepted.

## License

Proprietary - All rights reserved.

## Support

For questions or issues, contact the development team.

---

**Built with AI-powered market intelligence for the vintage denim community.**
