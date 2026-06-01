from pydantic import BaseModel, Field


class CropResponse(BaseModel):
    id: str
    name: str
    variety: str | None = None
    season: str | None = None
    growth_duration_days: int | None = None
    icon_emoji: str = "🌱"

    model_config = {"from_attributes": True}


class CropCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    variety: str | None = Field(None, max_length=255)
    season: str | None = Field(None, max_length=50)
    growth_duration_days: int | None = None
    icon_emoji: str = Field("🌱", max_length=10)
