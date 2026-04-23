from pydantic import BaseModel, field_validator
from typing import Optional, List
import uuid


class BudgetUpdate(BaseModel):
    amount_limit: float
    currency: str = "UZS"

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        if v not in ("UZS", "USD"):
            raise ValueError("Currency must be UZS or USD")
        return v

    @field_validator("amount_limit")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Budget limit must be positive")
        return v


class BudgetItem(BaseModel):
    category_id: uuid.UUID
    category_name: str
    budget_limit: Optional[float] = None
    current_spend: float
    currency: str
    percentage_used: Optional[float] = None
    status: str
    remaining: Optional[float] = None


class BudgetSummary(BaseModel):
    over_budget_count: int
    approaching_limit_count: int


class BudgetsResponse(BaseModel):
    summary: BudgetSummary
    budgets: List[BudgetItem]
