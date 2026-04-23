from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date

from backend.core.dependencies import get_current_user, get_db
from backend.models.user import User
from backend.models.transaction import Transaction
from backend.models.category import Category
from backend.services.analytics_service import (
    get_period_bounds,
    get_totals,
    get_last_6_months,
    get_expense_by_category,
    safe_percent_change,
)

router = APIRouter(tags=["overview"])


@router.get("/overview")
def get_overview(
    period: str = Query(default="month", pattern="^(month|week|quarter|year)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = date.today()
    start, end, prev_start, prev_end = get_period_bounds(period, today)

    curr_income, curr_expenses = get_totals(db, start, end)
    prev_income, prev_expenses = get_totals(db, prev_start, prev_end)

    curr_net = curr_income - curr_expenses
    prev_net = prev_income - prev_expenses

    monthly_chart = get_last_6_months(db, today)
    expense_by_cat = get_expense_by_category(db, start, end)

    recent_txs = (
        db.query(Transaction)
        .join(Transaction.category)
        .join(Transaction.user)
        .filter(Transaction.date >= start, Transaction.date <= end)
        .order_by(Transaction.date.desc(), Transaction.created_at.desc())
        .limit(10)
        .all()
    )

    recent = [
        {
            "id": str(tx.id),
            "date": tx.date.isoformat(),
            "category": tx.category.name if tx.category else "",
            "note": tx.note,
            "amount": float(tx.amount),
            "currency": tx.currency,
            "type": tx.type.value,
            "added_by": tx.user.phone_number if tx.user else "",
        }
        for tx in recent_txs
    ]

    return {
        "current_period": {
            "total_income": curr_income,
            "total_expenses": curr_expenses,
            "net_balance": curr_net,
            "currency": "UZS",
        },
        "previous_period": {
            "total_income": prev_income,
            "total_expenses": prev_expenses,
            "net_balance": prev_net,
        },
        "comparison": {
            "income_change_percent": safe_percent_change(curr_income, prev_income),
            "expense_change_percent": safe_percent_change(curr_expenses, prev_expenses),
            "net_change_percent": safe_percent_change(curr_net, prev_net),
        },
        "monthly_chart": monthly_chart,
        "expense_by_category": expense_by_cat,
        "recent_transactions": recent,
    }
