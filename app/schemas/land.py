from datetime import datetime
from pydantic import BaseModel, Field


# --- Land Schemas ---

class PointSchema(BaseModel):
    x: float
    y: float
    curve: float | None = None  # 0-100, corner roundness percentage


class LandCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    address: str | None = Field(None, max_length=500)
    total_area_acres: float | None = None


class LandUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    address: str | None = Field(None, max_length=500)
    total_area_acres: float | None = None
    boundary_points: list[PointSchema] | None = None
    canvas_metadata: dict | None = None


class LandResponse(BaseModel):
    id: str
    user_id: str
    name: str
    total_area_acres: float | None = None
    boundary_points: list[PointSchema] | None = None
    canvas_metadata: dict | None = None
    address: str | None = None
    sections_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Land Section Schemas ---

class SectionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    color: str = Field("#40916C", max_length=7)
    area_acres: float | None = None
    boundary_points: list[PointSchema] | None = None
    current_crop_id: str | None = None


class SectionUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    color: str | None = Field(None, max_length=7)
    area_acres: float | None = None
    boundary_points: list[PointSchema] | None = None
    current_crop_id: str | None = None


class SectionResponse(BaseModel):
    id: str
    land_id: str
    name: str
    color: str
    area_acres: float | None = None
    boundary_points: list[PointSchema] | None = None
    current_crop_id: str | None = None
    crop_name: str | None = None
    crop_emoji: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
