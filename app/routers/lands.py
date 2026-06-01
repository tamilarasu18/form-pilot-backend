from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import get_current_user
from app.models.land import Land, LandSection
from app.models.user import User
from app.schemas.land import (
    LandCreate, LandUpdate, LandResponse,
    SectionCreate, SectionUpdate, SectionResponse,
)

router = APIRouter(prefix="/api/lands", tags=["Lands"])


# --- Land CRUD ---

@router.get("", response_model=list[LandResponse])
async def list_lands(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List all lands for the current farmer."""
    result = await db.execute(
        select(Land)
        .options(selectinload(Land.sections))
        .where(Land.user_id == current_user.id)
        .order_by(Land.created_at.desc())
    )
    lands = result.scalars().all()

    response = []
    for land in lands:
        land_dict = {
            "id": land.id,
            "user_id": land.user_id,
            "name": land.name,
            "total_area_acres": land.total_area_acres,
            "boundary_points": land.boundary_points,
            "canvas_metadata": land.canvas_metadata,
            "address": land.address,
            "sections_count": len(land.sections),
            "created_at": land.created_at,
            "updated_at": land.updated_at,
        }
        response.append(LandResponse(**land_dict))
    return response


@router.post("", response_model=LandResponse, status_code=status.HTTP_201_CREATED)
async def create_land(
    data: LandCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create a new land parcel."""
    land = Land(
        user_id=current_user.id,
        name=data.name,
        address=data.address,
        total_area_acres=data.total_area_acres,
    )
    db.add(land)
    await db.flush()
    await db.refresh(land)

    return LandResponse(
        id=land.id,
        user_id=land.user_id,
        name=land.name,
        total_area_acres=land.total_area_acres,
        boundary_points=land.boundary_points,
        canvas_metadata=land.canvas_metadata,
        address=land.address,
        sections_count=0,
        created_at=land.created_at,
        updated_at=land.updated_at,
    )


@router.get("/{land_id}", response_model=LandResponse)
async def get_land(
    land_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get a specific land by ID."""
    result = await db.execute(
        select(Land)
        .options(selectinload(Land.sections))
        .where(Land.id == land_id, Land.user_id == current_user.id)
    )
    land = result.scalar_one_or_none()
    if not land:
        raise HTTPException(status_code=404, detail="Land not found")

    return LandResponse(
        id=land.id,
        user_id=land.user_id,
        name=land.name,
        total_area_acres=land.total_area_acres,
        boundary_points=land.boundary_points,
        canvas_metadata=land.canvas_metadata,
        address=land.address,
        sections_count=len(land.sections),
        created_at=land.created_at,
        updated_at=land.updated_at,
    )


@router.put("/{land_id}", response_model=LandResponse)
async def update_land(
    land_id: str,
    data: LandUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update a land parcel (including boundary points)."""
    result = await db.execute(
        select(Land)
        .options(selectinload(Land.sections))
        .where(Land.id == land_id, Land.user_id == current_user.id)
    )
    land = result.scalar_one_or_none()
    if not land:
        raise HTTPException(status_code=404, detail="Land not found")

    update_data = data.model_dump(exclude_unset=True)
    if "boundary_points" in update_data and update_data["boundary_points"]:
        update_data["boundary_points"] = [p.model_dump() if hasattr(p, 'model_dump') else p for p in data.boundary_points]

    for field, value in update_data.items():
        if field == "boundary_points":
            setattr(land, field, [p if isinstance(p, dict) else p.model_dump() for p in (data.boundary_points or [])])
        else:
            setattr(land, field, value)

    db.add(land)
    await db.flush()
    await db.refresh(land)

    return LandResponse(
        id=land.id,
        user_id=land.user_id,
        name=land.name,
        total_area_acres=land.total_area_acres,
        boundary_points=land.boundary_points,
        canvas_metadata=land.canvas_metadata,
        address=land.address,
        sections_count=len(land.sections),
        created_at=land.created_at,
        updated_at=land.updated_at,
    )


@router.delete("/{land_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_land(
    land_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete a land parcel and all its sections."""
    result = await db.execute(
        select(Land).where(Land.id == land_id, Land.user_id == current_user.id)
    )
    land = result.scalar_one_or_none()
    if not land:
        raise HTTPException(status_code=404, detail="Land not found")

    await db.delete(land)


# --- Section CRUD ---

@router.get("/{land_id}/sections", response_model=list[SectionResponse])
async def list_sections(
    land_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List all sections for a land."""
    # Verify land ownership
    land_result = await db.execute(
        select(Land).where(Land.id == land_id, Land.user_id == current_user.id)
    )
    if not land_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Land not found")

    result = await db.execute(
        select(LandSection)
        .options(selectinload(LandSection.crop))
        .where(LandSection.land_id == land_id)
        .order_by(LandSection.created_at)
    )
    sections = result.scalars().all()

    return [
        SectionResponse(
            id=s.id,
            land_id=s.land_id,
            name=s.name,
            color=s.color,
            area_acres=s.area_acres,
            boundary_points=s.boundary_points,
            current_crop_id=s.current_crop_id,
            crop_name=s.crop.name if s.crop else None,
            crop_emoji=s.crop.icon_emoji if s.crop else None,
            created_at=s.created_at,
        )
        for s in sections
    ]


@router.post("/{land_id}/sections", response_model=SectionResponse, status_code=status.HTTP_201_CREATED)
async def create_section(
    land_id: str,
    data: SectionCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create a new section within a land."""
    land_result = await db.execute(
        select(Land).where(Land.id == land_id, Land.user_id == current_user.id)
    )
    if not land_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Land not found")

    section = LandSection(
        land_id=land_id,
        name=data.name,
        color=data.color,
        area_acres=data.area_acres,
        boundary_points=[p.model_dump() for p in data.boundary_points] if data.boundary_points else None,
        current_crop_id=data.current_crop_id,
    )
    db.add(section)
    await db.flush()
    await db.refresh(section)

    return SectionResponse(
        id=section.id,
        land_id=section.land_id,
        name=section.name,
        color=section.color,
        area_acres=section.area_acres,
        boundary_points=section.boundary_points,
        current_crop_id=section.current_crop_id,
        crop_name=None,
        crop_emoji=None,
        created_at=section.created_at,
    )


@router.put("/sections/{section_id}", response_model=SectionResponse)
async def update_section(
    section_id: str,
    data: SectionUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update a land section."""
    result = await db.execute(
        select(LandSection)
        .options(selectinload(LandSection.land), selectinload(LandSection.crop))
        .where(LandSection.id == section_id)
    )
    section = result.scalar_one_or_none()
    if not section or section.land.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Section not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "boundary_points" and value:
            setattr(section, field, [p if isinstance(p, dict) else p.model_dump() for p in data.boundary_points])
        else:
            setattr(section, field, value)

    db.add(section)
    await db.flush()
    await db.refresh(section)

    # Reload crop relationship
    result = await db.execute(
        select(LandSection)
        .options(selectinload(LandSection.crop))
        .where(LandSection.id == section_id)
    )
    section = result.scalar_one()

    return SectionResponse(
        id=section.id,
        land_id=section.land_id,
        name=section.name,
        color=section.color,
        area_acres=section.area_acres,
        boundary_points=section.boundary_points,
        current_crop_id=section.current_crop_id,
        crop_name=section.crop.name if section.crop else None,
        crop_emoji=section.crop.icon_emoji if section.crop else None,
        created_at=section.created_at,
    )


@router.delete("/sections/{section_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_section(
    section_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete a land section."""
    result = await db.execute(
        select(LandSection)
        .options(selectinload(LandSection.land))
        .where(LandSection.id == section_id)
    )
    section = result.scalar_one_or_none()
    if not section or section.land.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Section not found")

    await db.delete(section)
