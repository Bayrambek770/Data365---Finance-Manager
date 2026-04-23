from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from backend.core.dependencies import get_current_user, get_db
from backend.models.user import User
from backend.schemas.analytics import AnalyticsResponse
from backend.services.analytics_service import (
    get_period_bounds,
    get_period_label,
    get_income_vs_expense_over_time,
    get_top_categories,
    get_category_breakdown,
    get_by_weekday,
    get_average_transaction_size,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("", response_model=AnalyticsResponse)
def get_analytics(
    period: str = Query(default="month", pattern="^(week|month|quarter|year)$"),
    from_date: Optional[date] = Query(default=None),
    to_date: Optional[date] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = date.today()

    if from_date and to_date:
        start, end = from_date, to_date
        prev_start, prev_end = start, end  # no prev period for custom range
        label = f"{start.isoformat()} — {end.isoformat()}"
    else:
        start, end, prev_start, prev_end = get_period_bounds(period, today)
        label = get_period_label(period, today)

    over_time = get_income_vs_expense_over_time(db, period, start, end)
    top_expense = get_top_categories(db, "expense", start, end)
    top_income = get_top_categories(db, "income", start, end)
    breakdown = get_category_breakdown(db, start, end, prev_start, prev_end)
    by_weekday = get_by_weekday(db, start, end)
    avg_size = get_average_transaction_size(db, start, end)

    return {
        "period_label": label,
        "income_vs_expense_over_time": over_time,
        "top_expense_categories": top_expense,
        "top_income_categories": top_income,
        "category_breakdown": breakdown,
        "by_weekday": by_weekday,
        "average_transaction_size": avg_size,
    }
