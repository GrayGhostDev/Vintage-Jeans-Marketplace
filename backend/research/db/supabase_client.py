"""
Supabase Client Configuration
Replaces SQLModel/SQLite with Supabase PostgreSQL
"""

from supabase import create_client, Client
import os
from functools import lru_cache
from typing import Optional

# Supabase credentials from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")  # Service role key for backend

# Singleton pattern for Supabase client
_supabase_client: Optional[Client] = None


@lru_cache()
def get_supabase_client() -> Client:
    """
    Get or create Supabase client instance (singleton).

    Returns:
        Client: Initialized Supabase client

    Raises:
        ValueError: If SUPABASE_URL or SUPABASE_KEY is not set
    """
    global _supabase_client

    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError(
            "SUPABASE_URL and SUPABASE_KEY environment variables must be set. "
            "Check your .env file or environment configuration."
        )

    if _supabase_client is None:
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)

    return _supabase_client


# Export the client getter function
supabase = get_supabase_client


def health_check() -> dict:
    """
    Check if Supabase connection is healthy.

    Returns:
        dict: Status information
    """
    try:
        client = get_supabase_client()
        # Perform a simple query to verify connection
        result = client.table("sellers").select("id").limit(1).execute()
        return {
            "status": "ok",
            "database": "supabase",
            "connected": True
        }
    except Exception as e:
        return {
            "status": "error",
            "database": "supabase",
            "connected": False,
            "error": str(e)
        }


# Helper functions for common database operations

def paginate_query(table_name: str, page: int = 1, page_size: int = 20, filters: dict = None, order_by: str = "created_at", ascending: bool = False):
    """
    Helper function to paginate Supabase queries.

    Args:
        table_name: Name of the table to query
        page: Page number (1-indexed)
        page_size: Number of items per page
        filters: Dictionary of filters to apply
        order_by: Column to order by
        ascending: Sort order (True for ascending, False for descending)

    Returns:
        dict: Paginated results with data and metadata
    """
    client = get_supabase_client()

    # Calculate offset
    offset = (page - 1) * page_size

    # Build query
    query = client.table(table_name).select("*", count="exact")

    # Apply filters if provided
    if filters:
        for key, value in filters.items():
            if value is not None:
                query = query.eq(key, value)

    # Apply ordering and pagination
    query = query.order(order_by, desc=not ascending).range(offset, offset + page_size - 1)

    # Execute query
    response = query.execute()

    # Calculate total pages
    total_count = response.count if hasattr(response, 'count') else len(response.data)
    total_pages = (total_count + page_size - 1) // page_size

    return {
        "data": response.data,
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }


def execute_rpc(function_name: str, params: dict = None):
    """
    Execute a Supabase stored procedure (RPC).

    Args:
        function_name: Name of the stored procedure
        params: Parameters to pass to the function

    Returns:
        Response from the stored procedure
    """
    client = get_supabase_client()
    return client.rpc(function_name, params or {}).execute()


# Example usage and documentation
if __name__ == "__main__":
    # This will only run if the script is executed directly (for testing)
    print("Supabase Client Module")
    print("=====================")
    print(f"SUPABASE_URL: {SUPABASE_URL[:30]}..." if SUPABASE_URL else "Not set")
    print(f"SUPABASE_KEY: {'*' * 20}..." if SUPABASE_KEY else "Not set")

    try:
        client = get_supabase_client()
        print("\n✅ Supabase client initialized successfully")

        # Test connection
        health = health_check()
        print(f"\n🏥 Health check: {health}")

    except ValueError as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Tip: Create a .env file in the backend directory with:")
        print("   SUPABASE_URL=https://xxxxx.supabase.co")
        print("   SUPABASE_KEY=your-service-role-key")
