"""Blog content management for SEO and marketing."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

from research.db.supabase_client import get_supabase_client
from research.services.auth_service_supabase import get_current_admin

router = APIRouter()

# Enum classes as string constant containers (not Python Enums)

class BlogStatus:
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class BlogCategory:
    SELLING_TIPS = "selling_tips"
    VINTAGE_GUIDES = "vintage_guides"
    MARKET_INSIGHTS = "market_insights"
    COLLECTOR_STORIES = "collector_stories"
    SUSTAINABILITY = "sustainability"

# Pydantic models

class BlogPostCreate(BaseModel):
    title: str
    slug: str
    excerpt: str
    content: str
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    featured_image_url: Optional[str] = None
    featured_image_alt: Optional[str] = None
    category: str  # BlogCategory constant
    tags: Optional[str] = None
    read_time_minutes: int = 5
    related_posts: Optional[str] = None
    related_listings: Optional[str] = None

class BlogPostUpdate(BaseModel):
    title: Optional[str] = None
    excerpt: Optional[str] = None
    content: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    featured_image_url: Optional[str] = None
    category: Optional[str] = None  # BlogCategory constant
    tags: Optional[str] = None
    status: Optional[str] = None  # BlogStatus constant
    featured: Optional[bool] = None

class BlogPostResponse(BaseModel):
    id: str  # UUID
    title: str
    slug: str
    excerpt: str
    content: str
    meta_title: Optional[str]
    meta_description: Optional[str]
    category: str
    tags: Optional[str]
    author: str
    author_id: Optional[str]  # UUID
    status: str
    published_at: Optional[str]
    featured: bool
    view_count: int
    read_time_minutes: int
    created_at: str
    updated_at: str

# Public endpoints

@router.get("/", response_model=List[BlogPostResponse])
def list_blog_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    featured: Optional[bool] = None
):
    """List published blog posts (public)."""

    supabase = get_supabase_client()
    query = supabase.table("blog_posts").select("*")

    # Filter for published posts
    query = query.eq("status", BlogStatus.PUBLISHED)

    # Additional filters
    if category:
        query = query.eq("category", category)
    if featured is not None:
        query = query.eq("featured", featured)

    # Pagination and ordering
    end = skip + limit - 1
    response = query.order("published_at", desc=True).range(skip, end).execute()

    if not response.data:
        return []

    return [BlogPostResponse(**post) for post in response.data]


@router.get("/{slug}", response_model=BlogPostResponse)
def get_blog_post(slug: str):
    """Get blog post by slug (public)."""

    supabase = get_supabase_client()

    # Fetch post by slug
    response = supabase.table("blog_posts").select("*").eq("slug", slug).execute()

    if not response.data or len(response.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found"
        )

    post = response.data[0]

    # Increment view count
    new_view_count = post["view_count"] + 1
    supabase.table("blog_posts").update({
        "view_count": new_view_count
    }).eq("id", post["id"]).execute()

    # Update the post dict with new view count for response
    post["view_count"] = new_view_count

    return BlogPostResponse(**post)


# Admin endpoints

@router.post("/", response_model=BlogPostResponse, status_code=status.HTTP_201_CREATED)
async def create_blog_post(
    post_data: BlogPostCreate,
    current_admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Create new blog post (admin only)."""

    supabase = get_supabase_client()

    # Check if slug already exists
    existing_response = supabase.table("blog_posts").select("id").eq("slug", post_data.slug).execute()
    if existing_response.data and len(existing_response.data) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slug already exists"
        )

    # Create new blog post
    blog_post_data = {
        **post_data.model_dump(),
        "author": current_admin["full_name"],
        "author_id": current_admin["id"],
        "status": BlogStatus.DRAFT,
        "featured": False,
        "view_count": 0
    }

    insert_response = supabase.table("blog_posts").insert(blog_post_data).execute()

    if not insert_response.data or len(insert_response.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create blog post"
        )

    new_post = insert_response.data[0]

    return BlogPostResponse(**new_post)


@router.patch("/{post_id}", response_model=BlogPostResponse)
async def update_blog_post(
    post_id: str,  # UUID
    updates: BlogPostUpdate,
    current_admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Update blog post (admin only)."""

    supabase = get_supabase_client()

    # Check if post exists
    post_response = supabase.table("blog_posts").select("*").eq("id", post_id).execute()

    if not post_response.data or len(post_response.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found"
        )

    # Build update data with only provided fields
    update_data = updates.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow().isoformat()

    # Update blog post
    update_response = supabase.table("blog_posts").update(
        update_data
    ).eq("id", post_id).execute()

    if not update_response.data or len(update_response.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update blog post"
        )

    updated_post = update_response.data[0]

    return BlogPostResponse(**updated_post)


@router.post("/{post_id}/publish", response_model=BlogPostResponse)
async def publish_blog_post(
    post_id: str,  # UUID
    current_admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Publish blog post (admin only)."""

    supabase = get_supabase_client()

    # Check if post exists
    post_response = supabase.table("blog_posts").select("*").eq("id", post_id).execute()

    if not post_response.data or len(post_response.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found"
        )

    post = post_response.data[0]

    # Update publish status
    update_data = {
        "status": BlogStatus.PUBLISHED,
        "updated_at": datetime.utcnow().isoformat()
    }

    # Set published_at if not already set
    if not post.get("published_at"):
        update_data["published_at"] = datetime.utcnow().isoformat()

    # Update blog post
    update_response = supabase.table("blog_posts").update(
        update_data
    ).eq("id", post_id).execute()

    if not update_response.data or len(update_response.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to publish blog post"
        )

    published_post = update_response.data[0]

    return BlogPostResponse(**published_post)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_blog_post(
    post_id: str,  # UUID
    current_admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Delete blog post (admin only)."""

    supabase = get_supabase_client()

    # Check if post exists
    post_response = supabase.table("blog_posts").select("id").eq("id", post_id).execute()

    if not post_response.data or len(post_response.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found"
        )

    # Delete blog post
    supabase.table("blog_posts").delete().eq("id", post_id).execute()

    return None
