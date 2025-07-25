from fastapi import HTTPException, Header, Depends
from typing import Optional
import httpx
import os
from sqlalchemy.orm import Session
from app.models.schemas import UserResponse

async def get_current_user(authorization: Optional[str] = Header(None)) -> UserResponse:
    """
    Extract and validate user from JWT token
    For now, this is a simplified version - we'll integrate with Keycloak properly later
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    token = authorization.split(" ")[1]
    
    # For development, accept any token and return a mock user
    # TODO: Integrate with Keycloak in next step
    return UserResponse(
        id="user_001",
        email="attorney@verdict360.org",
        name="Sarah Advocate", 
        role="attorney",
        firm_name="Example Legal Firm"
    )

async def get_optional_user(authorization: Optional[str] = Header(None)) -> Optional[UserResponse]:
    """Optional user authentication for public endpoints"""
    try:
        return await get_current_user(authorization)
    except HTTPException:
        return None

# Database dependency (will be set by main.py)
SessionLocal = None

def get_db() -> Session:
    """Dependency for getting database session"""
    if not SessionLocal:
        raise HTTPException(status_code=500, detail="Database not configured")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def set_session_local(session_local):
    """Set the SessionLocal from main.py"""
    global SessionLocal
    SessionLocal = session_local
