from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.config import get_settings
from app.database import init_db, async_session, Base
from app.models.crop import Crop, DEFAULT_CROPS
from app.models.user import User  # noqa: F401 - imported for table creation
from app.models.land import Land, LandSection  # noqa: F401
from app.models.daily_log import DailyLog, Expense  # noqa: F401
from app.routers import auth, users, lands, crops, daily_logs

settings = get_settings()


async def seed_crops():
    """Seed default crops if the catalog is empty."""
    async with async_session() as session:
        result = await session.execute(select(Crop).limit(1))
        if result.scalar_one_or_none() is None:
            for crop_data in DEFAULT_CROPS:
                session.add(Crop(**crop_data))
            await session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    await init_db()
    await seed_crops()
    yield


app = FastAPI(
    title="FarmPilot API",
    description="Backend API for FarmPilot — Farming Management Platform",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(lands.router)
app.include_router(crops.router)
app.include_router(daily_logs.router)


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "FarmPilot API"}
