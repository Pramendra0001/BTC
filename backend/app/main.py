from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.models.models import User, RoleEnum
from app.core.security import get_password_hash
from app.api.router import api_router
from app.schemas.schemas import HealthResponse
import logging
import time

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger("btcshield.app")


def bootstrap_admin_user():
    """Environment-driven administrative user initialization.
    
    In production mode:
    - Never uses predictable credentials like 'admin/admin123'.
    - Only initializes an administrator if a strong ADMIN_PASSWORD is provided in environment variables.
    - If no password is provided in production, automatic creation is safely skipped.
    
    In development/offline mode:
    - Automatically provisions local default credentials for offline testing and demonstration.
    """
    db = SessionLocal()
    try:
        is_prod = settings.ENVIRONMENT.lower() == "production"
        if is_prod:
            if not settings.ADMIN_PASSWORD:
                logger.info("Production mode: ADMIN_PASSWORD not configured. Skipping automatic administrator bootstrap.")
                return
            if settings.ADMIN_PASSWORD == "admin123" or len(settings.ADMIN_PASSWORD) < 12:
                logger.warning("Production mode: Provided ADMIN_PASSWORD is weak. Admin bootstrap skipped for security.")
                return

            admin = db.query(User).filter(User.username == settings.ADMIN_USERNAME).first()
            if not admin:
                new_admin = User(
                    username=settings.ADMIN_USERNAME,
                    email=settings.ADMIN_EMAIL,
                    hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
                    role=RoleEnum.ADMINISTRATOR,
                    is_active=True
                )
                db.add(new_admin)
                db.commit()
                logger.info("Production administrator '%s' successfully bootstrapped from environment.", settings.ADMIN_USERNAME)
            else:
                logger.info("Administrator '%s' already registered in production database.", settings.ADMIN_USERNAME)
        else:
            # Development/offline default credentials
            dev_pass = settings.ADMIN_PASSWORD or "admin123"
            admin = db.query(User).filter(User.username == settings.ADMIN_USERNAME).first()
            if not admin:
                new_admin = User(
                    username=settings.ADMIN_USERNAME,
                    email=settings.ADMIN_EMAIL,
                    hashed_password=get_password_hash(dev_pass),
                    role=RoleEnum.ADMINISTRATOR,
                    is_active=True
                )
                db.add(new_admin)
                db.commit()
                logger.info("Development administrator '%s' initialized.", settings.ADMIN_USERNAME)
    except Exception as e:
        logger.error("Error during administrator bootstrap: %s", type(e).__name__)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for schema verification and bootstrap."""
    is_prod = settings.ENVIRONMENT.lower() == "production"
    logger.info("Starting BTC-SHIELD backend in %s mode...", settings.ENVIRONMENT)

    if is_prod:
        # In production, schema is verified and aligned safely
        logger.info("Production mode active: Ensuring schema and index alignment.")
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                conn.execute(text("ALTER TABLE wallets ADD COLUMN IF NOT EXISTS wallet_type VARCHAR;"))
                conn.execute(text("ALTER TABLE wallets ADD COLUMN IF NOT EXISTS country VARCHAR;"))
                conn.execute(text("ALTER TABLE wallets ADD COLUMN IF NOT EXISTS synthetic_balance_sats DOUBLE PRECISION;"))

                # Performance indexes for high-volume 100k queries
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_graph_edges_src ON graph_edges (source_id);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_graph_edges_tgt ON graph_edges (target_id);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_graph_edges_src_tgt ON graph_edges (source_id, target_id);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_tx_inputs_txid ON transaction_inputs (transaction_id);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_tx_outputs_txid ON transaction_outputs (transaction_id);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_transactions_ts ON transactions (timestamp DESC);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_wallets_tx_cnt ON wallets (tx_count DESC);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_alerts_entity ON alerts (entity_type, entity_id);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON alerts (created_at DESC);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_alerts_priority ON alerts (priority);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts (status);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs (created_at DESC);"))
                conn.commit()
            logger.info("Production database connection verified, schema aligned, and performance indexes ensured.")
        except Exception as e:
            logger.warning("Production schema/index alignment notice: %s", e)
    else:
        # Development / offline mode: Ensure local SQLite schema
        logger.info("Development mode active: Ensuring local SQLite tables with create_all().")
        Base.metadata.create_all(bind=engine)

    # Environment-driven admin bootstrap
    bootstrap_admin_user()

    yield

    logger.info("BTC-SHIELD backend shutting down.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

@app.middleware("http")
async def performance_timing_middleware(request: Request, call_next):
    """Controlled backend performance timing instrumentation logging slow paths (>1s)."""
    start_time = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start_time

    if duration > 1.0:
        logger.warning(f"[PERF] {request.method} {request.url.path} completed in {duration:.2f}s (SLOW)")
    else:
        logger.info(f"[PERF] {request.method} {request.url.path} completed in {duration:.2f}s")

    response.headers["X-Process-Time"] = f"{duration:.3f}s"
    return response

if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Health"])
def root():
    return {
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health():
    return {"status": "ok"}
