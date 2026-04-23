from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
import uuid

from backend.models.transaction import Transaction, TransactionSource
from backend.schemas.transaction import TransactionCreate, TransactionUpdate
from backend.services.budget_service import check_budget_warning


def build_transaction_item(tx: Transaction, requesting_user_id) -> dict:
    return {
        "id": tx.id,
        "date": tx.date,
        "category_id": tx.category_id,
        "category_name": tx.category.name if tx.category else "",
        "category_type": tx.category.type.value if tx.category else "",
        "note": tx.note,
        "amount": float(tx.amount),
        "currency": tx.currency,
        "type": tx.type.value,
        "source": tx.source.value,
        "added_by_phone": tx.user.phone_number if tx.user else "",
        "is_mine": str(tx.user_id) == str(requesting_user_id),
        "created_at": tx.created_at,
    }


def build_transaction_response(tx: Transaction, budget_warning: Optional[dict] = None) -> dict:
    return {
        "id": tx.id,
        "date": tx.date,
        "category_id": tx.category_id,
        "category_name": tx.category.name if tx.category else "",
        "note": tx.note,
        "amount": float(tx.amount),
        "currency": tx.currency,
        "type": tx.type.value,
        "source": tx.source.value,
        "budget_warning": budget_warning,
    }


def get_transactions(
    db: Session,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    category_id: Optional[uuid.UUID] = None,
    type_filter: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    requesting_user_id=None,
) -> dict:
    query = db.query(Transaction).join(Transaction.category).join(Transaction.user)

    if from_date:
        query = query.filter(Transaction.date >= from_date)
    if to_date:
        query = query.filter(Transaction.date <= to_date)
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    if type_filter:
        query = query.filter(Transaction.type == type_filter)
    if search:
        query = query.filter(Transaction.note.ilike(f"%{search}%"))

    total = query.count()
    total_pages = max(1, (total + page_size - 1) // page_size)
    transactions = (
        query.order_by(Transaction.date.desc(), Transaction.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": [build_transaction_item(tx, requesting_user_id) for tx in transactions],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


def create_transaction(
    db: Session,
    data: TransactionCreate,
    user_id,
    source: str = "dashboard",
) -> dict:
    tx_date = data.date or date.today()
    tx = Transaction(
        user_id=user_id,
        amount=data.amount,
        currency=data.currency,
        type=data.type,
        category_id=data.category_id,
        date=tx_date,
        note=data.note,
        source=source,
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)

    warning = check_budget_warning(db, data.category_id, data.type)
    return build_transaction_response(tx, warning)


def update_transaction(db: Session, tx: Transaction, data: TransactionUpdate) -> dict:
    if data.amount is not None:
        tx.amount = data.amount
    if data.currency is not None:
        tx.currency = data.currency
    if data.type is not None:
        tx.type = data.type
    if data.category_id is not None:
        tx.category_id = data.category_id
    if data.date is not None:
        tx.date = data.date
    if data.note is not None:
        tx.note = data.note

    db.commit()
    db.refresh(tx)
    return build_transaction_response(tx)


def delete_transaction(db: Session, tx: Transaction) -> None:
    db.delete(tx)
    db.commit()
