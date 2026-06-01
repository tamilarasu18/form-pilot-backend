import uuid
from datetime import date, datetime

from sqlalchemy import String, Float, Date, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DailyLog(Base):
    """Daily farming activity log entry for a land section."""

    __tablename__ = "daily_logs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    section_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("land_sections.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    log_date: Mapped[date] = mapped_column(Date, nullable=False)
    activity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Climate data
    temperature_c: Mapped[float | None] = mapped_column(Float, nullable=True)
    humidity_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    rainfall_mm: Mapped[float | None] = mapped_column(Float, nullable=True)
    weather_condition: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Crop health
    crop_stage: Mapped[str | None] = mapped_column(String(50), nullable=True)
    crop_health_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Relationships
    section = relationship("LandSection", back_populates="daily_logs")
    user = relationship("User", back_populates="daily_logs")
    expenses = relationship("Expense", back_populates="daily_log", cascade="all, delete-orphan")


class Expense(Base):
    """Individual expense line item attached to a daily log."""

    __tablename__ = "expenses"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    daily_log_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("daily_logs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    section_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("land_sections.id", ondelete="CASCADE"), nullable=False
    )
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="INR")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Relationships
    daily_log = relationship("DailyLog", back_populates="expenses")
