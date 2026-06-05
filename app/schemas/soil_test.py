from datetime import date, datetime
from typing import Optional, Dict
from pydantic import BaseModel


class SoilTestBase(BaseModel):
    land_id: str
    section_id: Optional[str] = None
    
    test_date: date
    lab_name: Optional[str] = None
    sample_depth: Optional[str] = None
    notes: Optional[str] = None
    measurement_unit: str = "ppm"

    ph_level: Optional[float] = None
    ec_level: Optional[float] = None
    organic_carbon: Optional[float] = None

    nitrogen: Optional[float] = None
    phosphorus: Optional[float] = None
    potassium: Optional[float] = None

    micronutrients: Optional[Dict[str, float]] = None


class SoilTestCreate(SoilTestBase):
    pass


class SoilTestResponse(SoilTestBase):
    id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True
