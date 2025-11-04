from sqlmodel import create_engine, Session, SQLModel
import os
from dotenv import load_dotenv

# Import all models to register them with SQLModel
from research.models.seller import Seller
from research.models.listing import Listing
from research.models.analytics import Analytics, Insight, SyncLog
from research.models.research_model import ResearchSummary
from research.models.blog import BlogPost

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./vintage_jeans.db")

# Create engine with appropriate settings
engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)


def get_session():
    """Get database session (context manager pattern)."""
    return Session(engine)


def init_db():
    """Initialize database by creating all tables."""
    SQLModel.metadata.create_all(engine)
    print("✅ Database initialized successfully!")
