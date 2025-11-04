"""
Authentication and authorization service for Supabase.
Replaces SQLModel-based auth with Supabase client.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import os
from dotenv import load_dotenv

from research.db.supabase_client import get_supabase_client

load_dotenv()

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "43200"))  # 30 days

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/sellers/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password for storing."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Data to encode in the token (should include seller_id, email, role)
        expires_delta: Optional expiration time delta

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decode and verify a JWT access token.

    Args:
        token: JWT token to decode

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If token is invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def authenticate_seller(email: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Authenticate a seller with email and password using Supabase.

    Args:
        email: Seller's email address
        password: Plain text password

    Returns:
        Seller data dict if authenticated, None otherwise
    """
    try:
        supabase = get_supabase_client()

        # Fetch seller by email
        response = supabase.table("sellers").select("*").eq("email", email).execute()

        if not response.data or len(response.data) == 0:
            return None

        seller = response.data[0]

        # Verify password
        if not verify_password(password, seller["hashed_password"]):
            return None

        return seller

    except Exception as e:
        print(f"Authentication error: {e}")
        return None


async def get_current_seller(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Get the current authenticated seller from the token using Supabase.

    Args:
        token: JWT token from Authorization header

    Returns:
        Seller data dict

    Raises:
        HTTPException: If authentication fails
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        seller_id: str = payload.get("sub")  # UUID as string
        if seller_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    try:
        supabase = get_supabase_client()

        # Fetch seller by ID
        response = supabase.table("sellers").select("*").eq("id", seller_id).execute()

        if not response.data or len(response.data) == 0:
            raise credentials_exception

        seller = response.data[0]

        # Check if seller is active
        if not seller.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Seller account is inactive"
            )

        return seller

    except Exception as e:
        print(f"Error fetching seller: {e}")
        raise credentials_exception


async def get_current_active_seller(
    current_seller: Dict[str, Any] = Depends(get_current_seller)
) -> Dict[str, Any]:
    """
    Get the current active seller.

    Args:
        current_seller: Current seller from get_current_seller dependency

    Returns:
        Seller data dict

    Raises:
        HTTPException: If seller is inactive
    """
    if not current_seller.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seller account is inactive"
        )
    return current_seller


async def get_current_admin(
    current_seller: Dict[str, Any] = Depends(get_current_seller)
) -> Dict[str, Any]:
    """
    Get the current seller, ensuring they have admin role.

    Args:
        current_seller: Current seller from get_current_seller dependency

    Returns:
        Seller data dict

    Raises:
        HTTPException: If seller is not an admin
    """
    if current_seller.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_seller


def generate_referral_code(seller_id: str, full_name: str) -> str:
    """
    Generate a unique referral code for a seller.

    Args:
        seller_id: Seller's UUID (as string)
        full_name: Seller's full name

    Returns:
        Unique referral code (e.g., "VJABCD1234")
    """
    import hashlib
    import time

    # Create a unique string from seller info and timestamp
    unique_string = f"{seller_id}-{full_name}-{time.time()}"
    hash_object = hashlib.sha256(unique_string.encode())
    hash_hex = hash_object.hexdigest()[:8].upper()

    return f"VJ{hash_hex}"


def update_last_login(seller_id: str) -> None:
    """
    Update the last_login_at timestamp for a seller.

    Args:
        seller_id: Seller's UUID
    """
    try:
        supabase = get_supabase_client()
        supabase.table("sellers").update({
            "last_login_at": datetime.utcnow().isoformat()
        }).eq("id", seller_id).execute()
    except Exception as e:
        print(f"Error updating last login: {e}")
        # Non-critical error, don't raise
