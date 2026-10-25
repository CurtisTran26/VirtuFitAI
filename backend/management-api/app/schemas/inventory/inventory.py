from pydantic import BaseModel, Field


class AdjustIn(BaseModel):
    delta: int = Field(ne=0)
    reason: str = Field(min_length=3, max_length=500)
