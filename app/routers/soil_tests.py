from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.soil_test import SoilTest
from app.schemas.soil_test import SoilTestCreate, SoilTestResponse
from app.dependencies import get_current_user
from app.models.user import User
from app.models.land import Land

router = APIRouter(prefix="/api/soil-tests", tags=["Soil Tests"])


@router.post("", response_model=SoilTestResponse, status_code=status.HTTP_201_CREATED)
async def create_soil_test(
    data: SoilTestCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create a new manual soil test record."""
    # Verify land ownership
    land = await db.get(Land, data.land_id)
    if not land or land.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Land not found")

    soil_test = SoilTest(
        user_id=current_user.id,
        **data.model_dump()
    )
    db.add(soil_test)
    await db.flush()
    await db.commit()
    return soil_test


@router.get("/land/{land_id}", response_model=list[SoilTestResponse])
async def get_soil_tests_by_land(
    land_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get all soil tests for a specific land parcel."""
    result = await db.execute(
        select(SoilTest)
        .where(SoilTest.land_id == land_id, SoilTest.user_id == current_user.id)
        .order_by(SoilTest.test_date.desc())
    )
    return list(result.scalars().all())


@router.get("", response_model=list[SoilTestResponse])
async def get_all_soil_tests(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get all soil tests for the current farmer across all lands."""
    result = await db.execute(
        select(SoilTest)
        .where(SoilTest.user_id == current_user.id)
        .order_by(SoilTest.test_date.desc())
    )
    return list(result.scalars().all())


@router.delete("/{test_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_soil_test(
    test_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete a soil test record."""
    soil_test = await db.get(SoilTest, test_id)
    if not soil_test or soil_test.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Soil test not found")

    await db.delete(soil_test)
    await db.commit()
