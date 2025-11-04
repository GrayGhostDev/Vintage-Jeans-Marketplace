"""Authentication and authorization service."""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
import os
from dotenv import load_dotenv

from research.models.seller import Seller
from research.db.session import get_session

load_dotenv()

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password for storing."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """Decode and verify a JWT access token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def authenticate_seller(email: str, password: str, session: Session) -> Optional[Seller]:
    """Authenticate a seller with email and password."""
    statement = select(Seller).where(Seller.email == email)
    seller = session.exec(statement).first()

    if not seller:
        return None
    if not verify_password(password, seller.hashed_password):
        return None

    return seller


async def get_current_seller(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
) -> Seller:
    """Get the current authenticated seller from the token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        seller_id: int = payload.get("sub")
        if seller_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    statement = select(Seller).where(Seller.id == seller_id)
    seller = session.exec(statement).first()

    if seller is None:
        raise credentials_exception

    if not seller.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seller account is inactive"
        )

    return seller


async def get_current_active_seller(
    current_seller: Seller = Depends(get_current_seller)
) -> Seller:
    """Get the current active seller."""
    if not current_seller.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seller account is inactive"
        )
    return current_seller


async def get_current_admin(
    current_seller: Seller = Depends(get_current_seller)
) -> Seller:
    """Get the current seller, ensuring they have admin role."""
    if current_seller.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_seller


def generate_referral_code(seller_id: int, full_name: str) -> str:
    """Generate a unique referral code for a seller."""
    import hashlib
    import time

    # Create a unique string from seller info and timestamp
    unique_string = f"{seller_id}-{full_name}-{time.time()}"
    hash_object = hashlib.sha256(unique_string.encode())
    hash_hex = hash_object.hexdigest()[:8].upper()

    return f"VJ{hash_hex}"
