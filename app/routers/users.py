from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserProfile, UserProfileUpdate

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/me", response_model=UserProfile)
async def get_profile(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get the current farmer's profile."""
    return current_user


@router.put("/me", response_model=UserProfile)
async def update_profile(
    data: UserProfileUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update the current farmer's profile."""
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)

    db.add(current_user)
    await db.flush()
    await db.refresh(current_user)
    return current_user
