from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, get_current_user, require_role
from app.models.models import User
from app.schemas.schemas import UserResponse, UserCreate, Token
from datetime import timedelta
from app.core.config import settings

router = APIRouter()

from fastapi import Request

@router.post("/login", response_model=Token)
async def login_for_access_token(
    request: Request,
    db: Session = Depends(get_db)
):
    content_type = request.headers.get("content-type", "")
    username = ""
    password = ""
    if "application/json" in content_type:
        body = await request.json()
        username = body.get("username", "")
        password = body.get("password", "")
    else:
        form = await request.form()
        username = form.get("username", "")
        password = form.get("password", "")

    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
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

@router.post("/register", response_model=UserResponse)
def register_user(user_in: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role(["ADMINISTRATOR"]))):
    user = db.query(User).filter(User.username == user_in.username).first()
    if user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    new_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
