from __future__ import annotations
from datetime import date
from typing import Literal
from pydantic import BaseModel, Field

class ProfileUpdate(BaseModel):
    full_name: str = Field(min_length=1,max_length=120)
    date_of_birth: date | None = None
    height_cm: float | None = Field(default=None,ge=50,le=250)
    weight_kg: float | None = Field(default=None,ge=10,le=400)
    avatar_data: str | None = Field(default=None,max_length=2800000)


