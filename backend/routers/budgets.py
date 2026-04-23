from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from datetime import date
import uuid

from backend.core.dependencies import get_current_user, get_db
from backend.models.user import User
from backend.models.category import Category, CategoryType
from backend.models.transaction import Transaction, TransactionType
from backend.models.budget import Budget
from backend.schemas.budget import BudgetUpdate, BudgetsResponse
from backend.services.budget_service import get_budget_status

router = APIRouter(prefix="/budgets", tags=["budgets"])


def _current_month_spend(db: Session, category_id) -> float:
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


@router.get("", response_model=BudgetsResponse)
def list_budgets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expense_cats = db.query(Category).filter(
        Category.type == CategoryType.expense
    ).order_by(Category.name).all()

    budgets_list = []
    over_count = 0
    approaching_count = 0

    for cat in expense_cats:
        budget = cat.budget
        current_spend = _current_month_spend(db, cat.id)
        currency = budget.currency if budget else "UZS"

        if budget:
            limit = float(budget.amount_limit)
            pct = round(current_spend / limit * 100, 1) if limit > 0 else 0
            status = get_budget_status(pct)
            remaining = max(0.0, limit - current_spend)
        else:
            limit = None
            pct = None
            status = "no_budget"
            remaining = None

        if status == "exceeded":
            over_count += 1
        elif status == "approaching":
            approaching_count += 1

        budgets_list.append({
            "category_id": cat.id,
            "category_name": cat.name,
            "budget_limit": limit,
            "current_spend": current_spend,
            "currency": currency,
            "percentage_used": pct,
            "status": status,
            "remaining": remaining,
        })

    return {
        "summary": {
            "over_budget_count": over_count,
            "approaching_limit_count": approaching_count,
        },
        "budgets": budgets_list,
    }


@router.put("/{category_id}")
def upsert_budget(
    category_id: uuid.UUID,
    data: BudgetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    if cat.type != CategoryType.expense:
        raise HTTPException(status_code=400, detail="Budgets can only be set for expense categories")

    budget = db.query(Budget).filter(Budget.category_id == category_id).first()
    if budget:
        budget.amount_limit = data.amount_limit
        budget.currency = data.currency
    else:
        budget = Budget(
            category_id=category_id,
            amount_limit=data.amount_limit,
            currency=data.currency,
        )
        db.add(budget)

    db.commit()
    db.refresh(budget)

    return {
        "id": budget.id,
        "category_id": budget.category_id,
        "category_name": cat.name,
        "amount_limit": float(budget.amount_limit),
        "currency": budget.currency,
    }
