from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.models.models import User, RoleEnum
from app.core.security import get_password_hash
from app.api.router import api_router
import logging

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

def create_admin_user():
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            new_admin = User(
                username="admin",
                email="admin@btcshield.gov",
                hashed_password=get_password_hash("admin123"),
                role=RoleEnum.ADMINISTRATOR,
                is_active=True
            )
            db.add(new_admin)
            db.commit()
            logger.info("Admin user created.")
    except Exception as e:
        logger.error(f"Error creating admin user: {e}")
    finally:
        db.close()

Base.metadata.create_all(bind=engine)
create_admin_user()

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")

if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": "Welcome to BTC-SHIELD API"}
