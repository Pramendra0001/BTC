from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User
from app.schemas.schemas import DashboardResponse
from app.services.dashboard_service import get_dashboard

router = APIRouter()

@router.get("/", response_model=DashboardResponse)
def get_dashboard_data(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_dashboard(db)
