"""
BTC-SHIELD User & RBAC Management Endpoints
Manage users, assign roles (ADMINISTRATOR, INVESTIGATOR, ANALYST, VIEWER), and update accounts.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import User, RoleEnum
from app.core.security import get_password_hash
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

router = APIRouter()

class UserUpdateRequest(BaseModel):
    role: Optional[str] = None
    is_active: Optional[bool] = None

class UserCreateRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Optional[str] = "VIEWER"

@router.get("")
def list_users(db: Session = Depends(get_db)):
    """List all registered system users with roles and status."""
    users = db.query(User).order_by(User.id.asc()).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "role": u.role,
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat() if u.created_at else None
        }
        for u in users
    ]

@router.post("", status_code=status.HTTP_201_CREATED)
def create_user(req: UserCreateRequest, db: Session = Depends(get_db)):
    """Create a new user account with assigned RBAC role."""
    existing = db.query(User).filter((User.username == req.username) | (User.email == req.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already registered")

    valid_roles = [r.value for r in RoleEnum]
    if req.role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of {valid_roles}")

    new_user = User(
        username=req.username,
        email=req.email,
        hashed_password=get_password_hash(req.password),
        role=req.role,
        is_active=True,
        created_at=datetime.utcnow()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "role": new_user.role,
        "is_active": new_user.is_active,
        "created_at": new_user.created_at.isoformat()
    }

@router.patch("/{user_id}")
def update_user_role_or_status(
    user_id: int,
    req: UserUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update role or activate/deactivate user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if req.role is not None:
        valid_roles = [r.value for r in RoleEnum]
        if req.role not in valid_roles:
            raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of {valid_roles}")
        user.role = req.role

    if req.is_active is not None:
        user.is_active = req.is_active

    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active
    }
