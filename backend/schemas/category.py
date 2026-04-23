from pydantic import BaseModel, field_validator
from typing import List
import uuid


class CategoryCreate(BaseModel):
    name: str
    type: str

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v not in ("income", "expense"):
            raise ValueError("Type must be income or expense")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Name cannot be empty")
        return v


class CategoryItem(BaseModel):
    id: uuid.UUID
    name: str
    type: str
    is_default: bool
    transaction_count: int

    model_config = {"from_attributes": True}


class CategoriesResponse(BaseModel):
    income: List[CategoryItem]
    expense: List[CategoryItem]
