"""
Legacy SQLModel session file - DEPRECATED.

All database operations have been migrated to Supabase.
This file is kept for reference but should not be imported.

Use research.db.supabase_client instead.
"""
import warnings

warnings.warn(
    "research.db.session is deprecated. Use research.db.supabase_client instead.",
    DeprecationWarning,
    stacklevel=2
)


def get_session():
    """Deprecated - use Supabase client instead."""
    raise NotImplementedError(
        "SQLModel sessions are deprecated. Use get_supabase_client() instead."
    )


def init_db():
    """Deprecated - use Supabase migrations instead."""
    raise NotImplementedError(
        "init_db() is deprecated. Use Supabase migrations instead."
    )
