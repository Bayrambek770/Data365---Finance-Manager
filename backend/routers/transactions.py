from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
import uuid

from backend.core.dependencies import get_current_user, get_db
from backend.models.user import User
from backend.models.transaction import Transaction
from backend.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    PaginatedTransactions,
)
from backend.services import transaction_service

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("", response_model=PaginatedTransactions)
def list_transactions(
    from_date: Optional[date] = Query(default=None),
    to_date: Optional[date] = Query(default=None),
    category_id: Optional[uuid.UUID] = Query(default=None),
    type: Optional[str] = Query(default=None, pattern="^(income|expense)$"),
    search: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return transaction_service.get_transactions(
        db=db,
        from_date=from_date,
        to_date=to_date,
        category_id=category_id,
        type_filter=type,
        search=search,
        page=page,
        page_size=page_size,
        requesting_user_id=current_user.id,
    )


@router.post("", response_model=TransactionResponse, status_code=201)
def create_transaction(
    data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return transaction_service.create_transaction(
        db=db,
        data=data,
        user_id=current_user.id,
        source="dashboard",
    )


@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: uuid.UUID,
    data: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if str(tx.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=403,
            detail="You can only edit your own transactions",
        )
    return transaction_service.update_transaction(db, tx, data)


@router.delete("/{transaction_id}")
def delete_transaction(
    transaction_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if str(tx.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=403,
            detail="You can only edit your own transactions",
        )
    transaction_service.delete_transaction(db, tx)
    return {"success": True}
