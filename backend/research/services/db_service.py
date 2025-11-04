"""
Database service for research summaries using Supabase.
Migrated from SQLModel to Supabase PostgreSQL.
"""
from research.db.supabase_client import get_supabase_client
from datetime import datetime
from typing import Dict, Any


def save_research_summary(client_name: str, summary: str) -> Dict[str, Any]:
    """
    Save a research summary to Supabase.

    Args:
        client_name: Name of the client
        summary: Research summary text

    Returns:
        Dictionary with the saved record data
    """
    supabase = get_supabase_client()

    # Insert into research_summaries table
    data = {
        "client_name": client_name,
        "summary": summary,
        "created_at": datetime.utcnow().isoformat()
    }

    result = supabase.table("research_summaries").insert(data).execute()

    if result.data and len(result.data) > 0:
        return result.data[0]
    else:
        raise Exception("Failed to save research summary")
