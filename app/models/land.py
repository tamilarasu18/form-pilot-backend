import uuid
from datetime import datetime

from sqlalchemy import String, Float, DateTime, ForeignKey, Text, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Land(Base):
    """A piece of land owned by a farmer."""

    __tablename__ = "lands"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    total_area_acres: Mapped[float | None] = mapped_column(Float, nullable=True)
    boundary_points: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    canvas_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="lands")
    sections = relationship("LandSection", back_populates="land", cascade="all, delete-orphan")


class LandSection(Base):
    """A section within a land parcel for growing a specific crop."""

    __tablename__ = "land_sections"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    land_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("lands.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    color: Mapped[str] = mapped_column(String(7), nullable=False, default="#40916C")
    area_acres: Mapped[float | None] = mapped_column(Float, nullable=True)
    boundary_points: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    current_crop_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("crops.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Relationships
    land = relationship("Land", back_populates="sections")
    crop = relationship("Crop", back_populates="sections")
    daily_logs = relationship("DailyLog", back_populates="section", cascade="all, delete-orphan")
