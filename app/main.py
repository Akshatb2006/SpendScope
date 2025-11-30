from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import get_settings
from app.logging_config import setup_logging
from app.database import init_db
from app.jobs.scheduler import start_scheduler, stop_scheduler
from app.routers import (
    auth_router,
    accounts_router,
    transactions_router,
    budgets_router,
    categories_router,
    anomalies_router,
    sync_router
)
import logging

setup_logging()
logger = logging.getLogger(__name__)
settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")
    init_db()
    start_scheduler()
    logger.info("Application started successfully")
    
    yield
    
    logger.info("Shutting down application...")
    stop_scheduler()
    logger.info("Application shut down")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.API_VERSION,
    description="Personal Finance Aggregator - Plaid-style Mock Platform",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(accounts_router.router)
app.include_router(transactions_router.router)
app.include_router(budgets_router.router)
app.include_router(categories_router.router)
app.include_router(anomalies_router.router)
app.include_router(sync_router.router)

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.API_VERSION,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/providers")
def list_providers():
    from app.providers.provider_registry import provider_registry
    return {"providers": provider_registry.list_providers()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        workers=settings.MAX_WORKERS if not settings.DEBUG else 1
    )