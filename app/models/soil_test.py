import uuid
from datetime import date, datetime

from sqlalchemy import String, Float, Date, DateTime, ForeignKey, Text, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SoilTest(Base):
    """Manual soil test record for a land or section."""

    __tablename__ = "soil_tests"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    land_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("lands.id", ondelete="CASCADE"), nullable=False, index=True
    )
    section_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("land_sections.id", ondelete="SET NULL"), nullable=True, index=True
    )
    
    # Metadata
    test_date: Mapped[date] = mapped_column(Date, nullable=False)
    lab_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sample_depth: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    measurement_unit: Mapped[str] = mapped_column(String(20), nullable=False, default="ppm")

    # Basic Characteristics
    ph_level: Mapped[float | None] = mapped_column(Float, nullable=True)
    ec_level: Mapped[float | None] = mapped_column(Float, nullable=True)
    organic_carbon: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Macronutrients (NPK)
    nitrogen: Mapped[float | None] = mapped_column(Float, nullable=True)
    phosphorus: Mapped[float | None] = mapped_column(Float, nullable=True)
    potassium: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Secondary/Micronutrients
    micronutrients: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Relationships
    user = relationship("User")
    land = relationship("Land")
    section = relationship("LandSection")
