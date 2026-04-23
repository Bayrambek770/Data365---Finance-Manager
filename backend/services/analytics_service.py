import calendar
from datetime import date, timedelta
from typing import Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract

from backend.models.transaction import Transaction, TransactionType
from backend.models.category import Category


WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def get_period_bounds(period: str, today: Optional[date] = None) -> Tuple[date, date, date, date]:
    if today is None:
        today = date.today()

    if period == "week":
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        prev_start = start - timedelta(days=7)
        prev_end = start - timedelta(days=1)

    elif period == "quarter":
        quarter = (today.month - 1) // 3
        q_start_month = quarter * 3 + 1
        start = date(today.year, q_start_month, 1)
        q_end_month = q_start_month + 2
        end = date(today.year, q_end_month, calendar.monthrange(today.year, q_end_month)[1])
        prev_q_start_month = q_start_month - 3
        if prev_q_start_month <= 0:
            prev_q_start_month += 12
            prev_year = today.year - 1
        else:
            prev_year = today.year
        prev_q_end_month = prev_q_start_month + 2
        prev_start = date(prev_year, prev_q_start_month, 1)
        prev_end = date(
            prev_year, prev_q_end_month, calendar.monthrange(prev_year, prev_q_end_month)[1]
        )

    elif period == "year":
        start = date(today.year, 1, 1)
        end = date(today.year, 12, 31)
        prev_start = date(today.year - 1, 1, 1)
        prev_end = date(today.year - 1, 12, 31)

    else:  # month
        start = today.replace(day=1)
        end = today.replace(day=calendar.monthrange(today.year, today.month)[1])
        prev_month = today.month - 1 if today.month > 1 else 12
        prev_year = today.year if today.month > 1 else today.year - 1
        prev_start = date(prev_year, prev_month, 1)
        prev_end = date(prev_year, prev_month, calendar.monthrange(prev_year, prev_month)[1])

    return start, end, prev_start, prev_end


def get_period_label(period: str, today: Optional[date] = None) -> str:
    if today is None:
        today = date.today()
    if period == "week":
        start = today - timedelta(days=today.weekday())
        return f"Week of {start.strftime('%b %d, %Y')}"
    if period == "quarter":
        q = (today.month - 1) // 3 + 1
        return f"Q{q} {today.year}"
    if period == "year":
        return str(today.year)
    return today.strftime("%B %Y")


def get_totals(db: Session, start: date, end: date) -> Tuple[float, float]:
    rows = db.query(
        Transaction.type,
        func.sum(Transaction.amount).label("total"),
    ).filter(
        and_(Transaction.date >= start, Transaction.date <= end)
    ).group_by(Transaction.type).all()

    income = 0.0
    expenses = 0.0
    for row in rows:
        if row.type == TransactionType.income:
            income = float(row.total or 0)
        else:
            expenses = float(row.total or 0)
    return income, expenses


def safe_percent_change(current: float, previous: float) -> float:
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return round((current - previous) / previous * 100, 1)


def get_last_6_months(db: Session, today: Optional[date] = None) -> list:
    if today is None:
        today = date.today()

    months = []
    for i in range(5, -1, -1):
        m = today.month - i
        y = today.year
        while m <= 0:
            m += 12
            y -= 1
        start = date(y, m, 1)
        end = date(y, m, calendar.monthrange(y, m)[1])
        income, expenses = get_totals(db, start, end)
        months.append({"month": start.strftime("%b %Y"), "income": income, "expenses": expenses})
    return months


def get_expense_by_category(db: Session, start: date, end: date) -> list:
    rows = db.query(
        Category.name,
        func.sum(Transaction.amount).label("total"),
    ).join(Transaction, Transaction.category_id == Category.id).filter(
        and_(
            Transaction.type == TransactionType.expense,
            Transaction.date >= start,
            Transaction.date <= end,
        )
    ).group_by(Category.name).order_by(func.sum(Transaction.amount).desc()).all()

    grand_total = sum(float(r.total or 0) for r in rows)
    return [
        {
            "category": r.name,
            "amount": float(r.total or 0),
            "percentage": round(float(r.total or 0) / grand_total * 100, 1) if grand_total else 0,
        }
        for r in rows
    ]


def get_income_vs_expense_over_time(db: Session, period: str, start: date, end: date) -> list:
    rows = db.query(
        Transaction.date,
        Transaction.type,
        func.sum(Transaction.amount).label("total"),
    ).filter(
        and_(Transaction.date >= start, Transaction.date <= end)
    ).group_by(Transaction.date, Transaction.type).order_by(Transaction.date).all()

    data: dict = {}
    for row in rows:
        key = row.date.isoformat()
        if key not in data:
            data[key] = {"income": 0.0, "expenses": 0.0}
        if row.type == TransactionType.income:
            data[key]["income"] = float(row.total or 0)
        else:
            data[key]["expenses"] = float(row.total or 0)

    if period == "year":
        monthly: dict = {}
        for k, v in data.items():
            month_key = k[:7]
            if month_key not in monthly:
                monthly[month_key] = {"income": 0.0, "expenses": 0.0}
            monthly[month_key]["income"] += v["income"]
            monthly[month_key]["expenses"] += v["expenses"]
        return [{"date": k, **v} for k, v in sorted(monthly.items())]

    return [{"date": k, **v} for k, v in sorted(data.items())]


def get_top_categories(db: Session, tx_type: str, start: date, end: date, limit: int = 5) -> list:
    rows = db.query(
        Category.name,
        func.sum(Transaction.amount).label("total"),
        func.count(Transaction.id).label("cnt"),
    ).join(Transaction, Transaction.category_id == Category.id).filter(
        and_(
            Transaction.type == tx_type,
            Transaction.date >= start,
            Transaction.date <= end,
        )
    ).group_by(Category.name).order_by(func.sum(Transaction.amount).desc()).limit(limit).all()

    grand_total = sum(float(r.total or 0) for r in rows)
    return [
        {
            "category": r.name,
            "amount": float(r.total or 0),
            "percentage": round(float(r.total or 0) / grand_total * 100, 1) if grand_total else 0,
            "transaction_count": r.cnt,
        }
        for r in rows
    ]


def get_category_breakdown(db: Session, start: date, end: date, prev_start: date, prev_end: date) -> list:
    current = db.query(
        Category.name,
        Category.type,
        func.sum(Transaction.amount).label("total"),
        func.count(Transaction.id).label("cnt"),
    ).join(Transaction, Transaction.category_id == Category.id).filter(
        and_(Transaction.date >= start, Transaction.date <= end)
    ).group_by(Category.name, Category.type).all()

    prev = db.query(
        Category.name,
        func.sum(Transaction.amount).label("total"),
    ).join(Transaction, Transaction.category_id == Category.id).filter(
        and_(Transaction.date >= prev_start, Transaction.date <= prev_end)
    ).group_by(Category.name).all()

    prev_map = {r.name: float(r.total or 0) for r in prev}
    grand_total = sum(float(r.total or 0) for r in current)

    result = []
    for r in current:
        amt = float(r.total or 0)
        prev_amt = prev_map.get(r.name, 0)
        trend = safe_percent_change(amt, prev_amt)
        result.append({
            "category": r.name,
            "type": r.type.value,
            "total_amount": amt,
            "percentage_of_total": round(amt / grand_total * 100, 1) if grand_total else 0,
            "transaction_count": r.cnt,
            "trend_vs_last_period": trend,
        })

    return sorted(result, key=lambda x: x["total_amount"], reverse=True)


def get_by_weekday(db: Session, start: date, end: date) -> list:
    rows = db.query(
        extract("dow", Transaction.date).label("dow"),
        func.count(Transaction.id).label("cnt"),
        func.sum(Transaction.amount).label("total"),
    ).filter(
        and_(Transaction.date >= start, Transaction.date <= end)
    ).group_by(extract("dow", Transaction.date)).all()

    # PostgreSQL dow: 0=Sunday → convert to Monday-first (0=Mon..6=Sun)
    dow_map = {0: 6, 1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5}
    data = {i: {"count": 0, "total": 0.0} for i in range(7)}
    for r in rows:
        idx = dow_map[int(r.dow)]
        data[idx] = {"count": r.cnt, "total": float(r.total or 0)}

    return [
        {
            "weekday": WEEKDAYS[i],
            "transaction_count": data[i]["count"],
            "total_amount": data[i]["total"],
        }
        for i in range(7)
    ]


def get_average_transaction_size(db: Session, start: date, end: date) -> float:
    result = db.query(func.avg(Transaction.amount)).filter(
        and_(Transaction.date >= start, Transaction.date <= end)
    ).scalar()
    return round(float(result or 0), 2)
