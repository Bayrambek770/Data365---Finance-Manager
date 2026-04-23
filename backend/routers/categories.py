from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
import uuid

from backend.core.dependencies import get_current_user, get_db
from backend.models.user import User
from backend.models.category import Category, CategoryType
from backend.models.transaction import Transaction
from backend.schemas.category import CategoryCreate, CategoryItem, CategoriesResponse

router = APIRouter(prefix="/categories", tags=["categories"])


def _build_item(cat: Category, db: Session) -> dict:
    count = db.query(func.count(Transaction.id)).filter(
        Transaction.category_id == cat.id
    ).scalar() or 0
    return {
        "id": cat.id,
        "name": cat.name,
        "type": cat.type.value,
        "is_default": cat.is_default,
        "transaction_count": count,
    }


@router.get("", response_model=CategoriesResponse)
def list_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    categories = db.query(Category).order_by(Category.is_default.desc(), Category.name).all()
    income = [_build_item(c, db) for c in categories if c.type == CategoryType.income]
    expense = [_build_item(c, db) for c in categories if c.type == CategoryType.expense]
    return {"income": income, "expense": expense}


@router.post("", response_model=CategoryItem, status_code=201)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = db.query(Category).filter(
        func.lower(Category.name) == data.name.lower()
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category with this name already exists")

    cat = Category(name=data.name, type=data.type, is_default=False)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return _build_item(cat, db)


@router.delete("/{category_id}")
def delete_category(
    category_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    if cat.is_default:
        raise HTTPException(status_code=400, detail="Default categories cannot be deleted")

    tx_count = db.query(func.count(Transaction.id)).filter(
        Transaction.category_id == category_id
    ).scalar() or 0
    if tx_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Category has {tx_count} transactions. Reassign them before deleting.",
        )

    db.delete(cat)
    db.commit()
    return {"success": True}
