from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


# --- Auth Schemas ---

class UserRegister(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=6, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=255)
    phone: str | None = Field(None, max_length=20)


class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: str


# --- User Profile Schemas ---

class UserProfile(BaseModel):
    id: str
    email: str
    full_name: str
    phone: str | None = None
    address: str | None = None
    profile_image_url: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserProfileUpdate(BaseModel):
    full_name: str | None = Field(None, min_length=1, max_length=255)
    phone: str | None = Field(None, max_length=20)
    address: str | None = Field(None, max_length=500)
    profile_image_url: str | None = Field(None, max_length=500)
