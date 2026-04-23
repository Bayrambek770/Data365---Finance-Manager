"""Run once on startup when categories table is empty."""
import sys
from backend.database import SessionLocal
from backend.models.category import Category, CategoryType

DEFAULT_CATEGORIES = [
    ("Sales", CategoryType.income),
    ("Services", CategoryType.income),
    ("Investment", CategoryType.income),
    ("Other", CategoryType.income),
    ("Salaries", CategoryType.expense),
    ("Logistics", CategoryType.expense),
    ("Rent", CategoryType.expense),
    ("Marketing", CategoryType.expense),
    ("Utilities", CategoryType.expense),
    ("Taxes", CategoryType.expense),
    ("Other", CategoryType.expense),
]


def seed():
    db = SessionLocal()
    try:
        existing = db.query(Category).count()
        if existing > 0:
            print("Seed: categories already exist, skipping.")
            return

        for name, cat_type in DEFAULT_CATEGORIES:
            db.add(Category(name=name, type=cat_type, is_default=True))

        db.commit()
        print(f"Seed: inserted {len(DEFAULT_CATEGORIES)} default categories.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
