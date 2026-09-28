from fastapi import FastAPI

from app.api.analysis import router as analysis_router
from app.api.upload import router as upload_router
from app.auth.routes import router as auth_router
from app.core.config import APP_NAME, APP_VERSION
from app.database.database import create_database_tables


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

create_database_tables()


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=(
        "AI-powered data analysis platform that allows users "
        "to upload datasets and query them using natural language."
    ),
)


# ============================================================
# ROUTER REGISTRATION
# ============================================================

app.include_router(
    upload_router
)

app.include_router(
    auth_router
)

app.include_router(
    analysis_router
)


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get(
    "/health",
    tags=["System"],
)
def health_check():
    return {
        "status": "healthy",
        "application": APP_NAME,
        "version": APP_VERSION,
    }