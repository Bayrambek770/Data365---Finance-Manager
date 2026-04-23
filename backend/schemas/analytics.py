from pydantic import BaseModel
from typing import List


class PeriodPoint(BaseModel):
    date: str
    income: float
    expenses: float


class CategoryStat(BaseModel):
    category: str
    amount: float
    percentage: float
    transaction_count: int


class CategoryBreakdown(BaseModel):
    category: str
    type: str
    total_amount: float
    percentage_of_total: float
    transaction_count: int
    trend_vs_last_period: float


class WeekdayStat(BaseModel):
    weekday: str
    transaction_count: int
    total_amount: float


class AnalyticsResponse(BaseModel):
    period_label: str
    income_vs_expense_over_time: List[PeriodPoint]
    top_expense_categories: List[CategoryStat]
    top_income_categories: List[CategoryStat]
    category_breakdown: List[CategoryBreakdown]
    by_weekday: List[WeekdayStat]
    average_transaction_size: float
