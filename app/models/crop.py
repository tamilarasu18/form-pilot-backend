import uuid

from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Crop(Base):
    """Crop catalog entry."""

    __tablename__ = "crops"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    variety: Mapped[str | None] = mapped_column(String(255), nullable=True)
    season: Mapped[str | None] = mapped_column(String(50), nullable=True)
    growth_duration_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    icon_emoji: Mapped[str] = mapped_column(String(10), nullable=False, default="🌱")

    # Relationships
    sections = relationship("LandSection", back_populates="crop")


# Default crops to seed
DEFAULT_CROPS = [
    {"name": "Rice", "variety": "Paddy", "season": "Kharif", "growth_duration_days": 120, "icon_emoji": "🌾"},
    {"name": "Wheat", "variety": "Common", "season": "Rabi", "growth_duration_days": 150, "icon_emoji": "🌾"},
    {"name": "Corn", "variety": "Sweet Corn", "season": "Kharif", "growth_duration_days": 90, "icon_emoji": "🌽"},
    {"name": "Cotton", "variety": "Upland", "season": "Kharif", "growth_duration_days": 180, "icon_emoji": "🧶"},
    {"name": "Sugarcane", "variety": "Tropical", "season": "Year-round", "growth_duration_days": 365, "icon_emoji": "🎋"},
    {"name": "Tomato", "variety": "Cherry", "season": "Rabi", "growth_duration_days": 75, "icon_emoji": "🍅"},
    {"name": "Potato", "variety": "Russet", "season": "Rabi", "growth_duration_days": 100, "icon_emoji": "🥔"},
    {"name": "Onion", "variety": "Red", "season": "Rabi", "growth_duration_days": 130, "icon_emoji": "🧅"},
    {"name": "Chili", "variety": "Green", "season": "Kharif", "growth_duration_days": 90, "icon_emoji": "🌶️"},
    {"name": "Soybean", "variety": "Common", "season": "Kharif", "growth_duration_days": 100, "icon_emoji": "🫘"},
    {"name": "Groundnut", "variety": "Runner", "season": "Kharif", "growth_duration_days": 120, "icon_emoji": "🥜"},
    {"name": "Banana", "variety": "Cavendish", "season": "Year-round", "growth_duration_days": 300, "icon_emoji": "🍌"},
    {"name": "Mango", "variety": "Alphonso", "season": "Summer", "growth_duration_days": 150, "icon_emoji": "🥭"},
    {"name": "Coconut", "variety": "Tall", "season": "Year-round", "growth_duration_days": 365, "icon_emoji": "🥥"},
    {"name": "Turmeric", "variety": "Common", "season": "Kharif", "growth_duration_days": 270, "icon_emoji": "🟡"},
]
