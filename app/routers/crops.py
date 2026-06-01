from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.crop import Crop, DEFAULT_CROPS
from app.models.user import User
from app.schemas.crop import CropResponse, CropCreate

router = APIRouter(prefix="/api/crops", tags=["Crops"])


@router.get("", response_model=list[CropResponse])
async def list_crops(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    """List all available crops in the catalog."""
    result = await db.execute(select(Crop).order_by(Crop.name))
    crops = result.scalars().all()
    return crops


@router.post("", response_model=CropResponse, status_code=status.HTTP_201_CREATED)
async def create_crop(
    data: CropCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    """Add a new crop to the catalog."""
    # Check for duplicate
    result = await db.execute(select(Crop).where(Crop.name == data.name))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Crop already exists")

    crop = Crop(**data.model_dump())
    db.add(crop)
    await db.flush()
    await db.refresh(crop)
    return crop
