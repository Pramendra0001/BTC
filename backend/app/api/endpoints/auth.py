from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, get_current_user, require_role
from app.models.models import User, RoleEnum
from app.schemas.schemas import UserResponse, UserCreate, Token, UserLogin, UserRegister
from datetime import timedelta
from app.core.config import settings

router = APIRouter()

@router.post("/login", response_model=Token)
def login_for_access_token(
    user_in: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == user_in.username).first()
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    access_token = create_access_token(
        subject=str(user.id), expires_delta=access_token_expires
    )
    from app.services import audit_service
    client_ip = request.client.host if request.client else "127.0.0.1"
    audit_service.log_action(
        db,
        action="USER_LOGIN",
        user_id=user.id,
        entity_type="USER",
        entity_id=str(user.id),
        details={"username": user.username, "role": user.role},
        ip_address=client_ip
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    user_in: UserRegister,
    request: Request,
    db: Session = Depends(get_db)
):
    """Public self-registration endpoint for investigators and jury members.
    
    Forces role to VIEWER. Privileged roles cannot be self-assigned.
    """
    # Check duplicate username -> HTTP 409
    if db.query(User).filter(User.username == user_in.username).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered"
        )
    
    # Check duplicate email -> HTTP 409
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email address already registered"
        )
    
    new_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        role=RoleEnum.VIEWER,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    from app.services import audit_service
    client_ip = request.client.host if request.client else "127.0.0.1"
    audit_service.log_action(
        db,
        action="USER_SELF_REGISTER",
        user_id=new_user.id,
        entity_type="USER",
        entity_id=str(new_user.id),
        details={"username": new_user.username, "role": new_user.role},
        ip_address=client_ip
    )
    return new_user

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
