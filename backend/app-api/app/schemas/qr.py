from __future__ import annotations
from datetime import date
from typing import Literal
from pydantic import BaseModel, Field

class QrScan(BaseModel):
    content: str = Field(min_length=1,max_length=1000)


