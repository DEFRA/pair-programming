# User models for pair programming app
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr


class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    paired_with: list[str] = []


class PairRequest(BaseModel):
    email: EmailStr


class PairResponse(BaseModel):
    paired_with: Optional[UserResponse]
    message: str
