from typing import Annotated
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import get_current_user
from app.models.daily_log import DailyLog, Expense
from app.models.land import LandSection
from app.models.user import User
from app.schemas.daily_log import (
    DailyLogCreate, DailyLogResponse, DailyLogUpdate,
    ExpenseCreate, ExpenseResponse,
)

router = APIRouter(prefix="/api", tags=["Daily Logs"])


def _build_log_response(log: DailyLog) -> DailyLogResponse:
    """Build a DailyLogResponse from a DailyLog model instance."""
    expenses = [
        ExpenseResponse(
            id=e.id,
            daily_log_id=e.daily_log_id,
            section_id=e.section_id,
            category=e.category,
            description=e.description,
            amount=e.amount,
            currency=e.currency,
            created_at=e.created_at,
        )
        for e in log.expenses
    ]
    return DailyLogResponse(
        id=log.id,
        section_id=log.section_id,
        user_id=log.user_id,
        log_date=log.log_date,
        activity_type=log.activity_type,
        notes=log.notes,
        temperature_c=log.temperature_c,
        humidity_pct=log.humidity_pct,
        rainfall_mm=log.rainfall_mm,
        weather_condition=log.weather_condition,
        crop_stage=log.crop_stage,
        crop_health_notes=log.crop_health_notes,
        expenses=expenses,
        total_expense=sum(e.amount for e in log.expenses),
        created_at=log.created_at,
    )


@router.post("/sections/{section_id}/logs", response_model=DailyLogResponse, status_code=status.HTTP_201_CREATED)
async def create_daily_log(
    section_id: str,
    data: DailyLogCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create a daily log entry for a section, optionally with inline expenses."""
    # Verify section ownership
    result = await db.execute(
        select(LandSection)
        .options(selectinload(LandSection.land))
        .where(LandSection.id == section_id)
    )
    section = result.scalar_one_or_none()
    if not section or section.land.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Section not found")

    log = DailyLog(
        section_id=section_id,
        user_id=current_user.id,
        log_date=data.log_date,
        activity_type=data.activity_type,
        notes=data.notes,
        temperature_c=data.temperature_c,
        humidity_pct=data.humidity_pct,
        rainfall_mm=data.rainfall_mm,
        weather_condition=data.weather_condition,
        crop_stage=data.crop_stage,
        crop_health_notes=data.crop_health_notes,
    )
    db.add(log)
    await db.flush()

    # Add inline expenses if provided
    if data.expenses:
        for expense_data in data.expenses:
            expense = Expense(
                daily_log_id=log.id,
                section_id=section_id,
                category=expense_data.category,
                description=expense_data.description,
                amount=expense_data.amount,
                currency=expense_data.currency,
            )
            db.add(expense)
        await db.flush()

    # Reload with expenses
    result = await db.execute(
        select(DailyLog)
        .options(selectinload(DailyLog.expenses))
        .where(DailyLog.id == log.id)
    )
    log = result.scalar_one()
    return _build_log_response(log)


@router.get("/sections/{section_id}/logs", response_model=list[DailyLogResponse])
async def list_daily_logs(
    section_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
):
    """List daily logs for a section with optional date filters."""
    # Verify ownership
    result = await db.execute(
        select(LandSection)
        .options(selectinload(LandSection.land))
        .where(LandSection.id == section_id)
    )
    section = result.scalar_one_or_none()
    if not section or section.land.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Section not found")

    query = (
        select(DailyLog)
        .options(selectinload(DailyLog.expenses))
        .where(DailyLog.section_id == section_id)
        .order_by(DailyLog.log_date.desc())
    )

    if date_from:
        query = query.where(DailyLog.log_date >= date_from)
    if date_to:
        query = query.where(DailyLog.log_date <= date_to)

    result = await db.execute(query)
    logs = result.scalars().all()
    return [_build_log_response(log) for log in logs]


@router.get("/logs", response_model=list[DailyLogResponse])
async def list_all_daily_logs(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
):
    """List all daily logs for the current user."""
    query = (
        select(DailyLog)
        .options(selectinload(DailyLog.expenses))
        .where(DailyLog.user_id == current_user.id)
        .order_by(DailyLog.log_date.desc())
    )

    if date_from:
        query = query.where(DailyLog.log_date >= date_from)
    if date_to:
        query = query.where(DailyLog.log_date <= date_to)

    result = await db.execute(query)
    logs = result.scalars().all()
    return [_build_log_response(log) for log in logs]


@router.get("/logs/{log_id}", response_model=DailyLogResponse)
async def get_daily_log(
    log_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get a specific daily log entry."""
    result = await db.execute(
        select(DailyLog)
        .options(selectinload(DailyLog.expenses))
        .where(DailyLog.id == log_id, DailyLog.user_id == current_user.id)
    )
    log = result.scalar_one_or_none()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return _build_log_response(log)


@router.put("/logs/{log_id}", response_model=DailyLogResponse)
async def update_daily_log(
    log_id: str,
    data: DailyLogUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update a daily log entry."""
    result = await db.execute(
        select(DailyLog)
        .options(selectinload(DailyLog.expenses))
        .where(DailyLog.id == log_id, DailyLog.user_id == current_user.id)
    )
    log = result.scalar_one_or_none()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(log, field, value)

    db.add(log)
    await db.flush()
    await db.refresh(log)

    # Reload with expenses
    result = await db.execute(
        select(DailyLog)
        .options(selectinload(DailyLog.expenses))
        .where(DailyLog.id == log.id)
    )
    log = result.scalar_one()
    return _build_log_response(log)


@router.delete("/logs/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_daily_log(
    log_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete a daily log entry and its expenses."""
    result = await db.execute(
        select(DailyLog).where(DailyLog.id == log_id, DailyLog.user_id == current_user.id)
    )
    log = result.scalar_one_or_none()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    await db.delete(log)


@router.post("/logs/{log_id}/expenses", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def add_expense(
    log_id: str,
    data: ExpenseCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Add an expense to an existing daily log."""
    result = await db.execute(
        select(DailyLog).where(DailyLog.id == log_id, DailyLog.user_id == current_user.id)
    )
    log = result.scalar_one_or_none()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")

    expense = Expense(
        daily_log_id=log_id,
        section_id=log.section_id,
        category=data.category,
        description=data.description,
        amount=data.amount,
        currency=data.currency,
    )
    db.add(expense)
    await db.flush()
    await db.refresh(expense)
    return expense
