from datetime import date, datetime
from pydantic import BaseModel, Field


# --- Expense Schemas ---

class ExpenseCreate(BaseModel):
    category: str = Field(..., min_length=1, max_length=50)
    description: str | None = Field(None, max_length=500)
    amount: float = Field(..., gt=0)
    currency: str = Field("INR", max_length=10)


class ExpenseResponse(BaseModel):
    id: str
    daily_log_id: str
    section_id: str
    category: str
    description: str | None = None
    amount: float
    currency: str
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Daily Log Schemas ---

class DailyLogCreate(BaseModel):
    log_date: date
    activity_type: str = Field(..., min_length=1, max_length=50)
    notes: str | None = None

    # Climate data
    temperature_c: float | None = None
    humidity_pct: float | None = Field(None, ge=0, le=100)
    rainfall_mm: float | None = Field(None, ge=0)
    weather_condition: str | None = Field(None, max_length=50)

    # Crop health
    crop_stage: str | None = Field(None, max_length=50)
    crop_health_notes: str | None = None

    # Inline expenses
    expenses: list[ExpenseCreate] | None = None


class DailyLogResponse(BaseModel):
    id: str
    section_id: str
    user_id: str
    log_date: date
    activity_type: str
    notes: str | None = None
    temperature_c: float | None = None
    humidity_pct: float | None = None
    rainfall_mm: float | None = None
    weather_condition: str | None = None
    crop_stage: str | None = None
    crop_health_notes: str | None = None
    expenses: list[ExpenseResponse] = []
    total_expense: float = 0.0
    created_at: datetime

    model_config = {"from_attributes": True}


class DailyLogUpdate(BaseModel):
    activity_type: str | None = Field(None, min_length=1, max_length=50)
    notes: str | None = None
    temperature_c: float | None = None
    humidity_pct: float | None = Field(None, ge=0, le=100)
    rainfall_mm: float | None = Field(None, ge=0)
    weather_condition: str | None = Field(None, max_length=50)
    crop_stage: str | None = Field(None, max_length=50)
    crop_health_notes: str | None = None
