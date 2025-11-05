"""
Vintage Jeans Marketplace Platform API
FastAPI backend with Supabase PostgreSQL database
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from research.routers import research_router, seller_router, listing_router, blog_router, marketplace_router
from research.db.supabase_client import health_check as supabase_health_check


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Check Supabase connection on startup."""
    # Verify Supabase connection
    health = supabase_health_check()
    if not health.get("connected"):
        print("⚠️  WARNING: Supabase connection failed. Check your credentials.")
        print(f"Error: {health.get('error')}")
    else:
        print("✅ Supabase connected successfully")
    yield


app = FastAPI(
    title="Vintage Jeans Marketplace Platform",
    description="AI-powered vintage jeans marketplace with seller onboarding, listing management, and market analytics.",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend
# Read allowed origins from environment variable or use defaults
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000,https://*.vercel.app"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(seller_router.router, prefix="/api/sellers", tags=["Sellers"])
app.include_router(listing_router.router, prefix="/api/listings", tags=["Listings"])
app.include_router(blog_router.router, prefix="/api/blog", tags=["Blog"])
app.include_router(research_router.router, prefix="/api/research", tags=["Research"])
app.include_router(marketplace_router.router, prefix="/api/marketplace", tags=["Marketplace"])


@app.get("/")
async def root():
    return {
        "message": "Vintage Jeans Marketplace Platform API",
        "version": "2.0.0",
        "endpoints": {
            "sellers": "/api/sellers",
            "listings": "/api/listings",
            "blog": "/api/blog",
            "research": "/api/research",
            "marketplace": "/api/marketplace",
            "docs": "/docs"
        }
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint for monitoring and deployment platforms."""
    health = supabase_health_check()
    return {
        "status": "ok" if health.get("connected") else "degraded",
        "service": "vintage-jeans-api",
        "version": "2.0.0",
        "database": health
    }
