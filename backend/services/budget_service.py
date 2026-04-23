from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from datetime import date
from typing import Optional

from backend.models.transaction import Transaction, TransactionType
from backend.models.budget import Budget
from backend.models.category import Category


def get_current_month_spend(db: Session, category_id) -> float:
    today = date.today()
    result = db.query(func.sum(Transaction.amount)).filter(
        and_(
            Transaction.category_id == category_id,
            Transaction.type == TransactionType.expense,
            extract("month", Transaction.date) == today.month,
            extract("year", Transaction.date) == today.year,
        )
    ).scalar()
    return float(result or 0)


def check_budget_warning(db: Session, category_id, transaction_type: str) -> Optional[dict]:
    if transaction_type != "expense":
        return None

    budget = db.query(Budget).filter(Budget.category_id == category_id).first()
    if not budget:
        return None

    current_spend = get_current_month_spend(db, category_id)
    limit = float(budget.amount_limit)
    percentage = (current_spend / limit * 100) if limit > 0 else 0

    if percentage < 70:
        return None

    category = db.query(Category).filter(Category.id == category_id).first()
    category_name = category.name if category else str(category_id)

    if percentage >= 100:
        status = "exceeded"
        exceeded_by = current_spend - limit
    else:
        status = "approaching"
        exceeded_by = 0.0

    return {
        "category": category_name,
        "limit": limit,
        "current_spend": current_spend,
        "exceeded_by": exceeded_by,
        "percentage_used": round(percentage, 1),
        "status": status,
    }


def get_budget_status(percentage_used: Optional[float]) -> str:
    if percentage_used is None:
        return "no_budget"
    if percentage_used >= 90:
        return "exceeded"
    if percentage_used >= 70:
        return "approaching"
    return "safe"
