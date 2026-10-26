from pydantic import BaseModel, Field


class Login(BaseModel):
    account: str = Field(min_length=1, max_length=254)
    password: str = Field(min_length=1, max_length=72)


