from datetime import date as date_type
from typing import Optional


def fmt_amount(amount: float, currency: str = "UZS") -> str:
    if currency == "USD":
        return f"${amount:,.2f}"
    return f"{amount:,.0f} {currency}"


def fmt_transaction_confirmation(data: dict) -> str:
    tx_type = data.get("type", "")
    type_label = "💰 Income" if tx_type == "income" else "💸 Expense"
    amount = data.get("amount", 0)
    currency = data.get("currency", "UZS")
    category = data.get("category_name") or data.get("category", "Unknown")
    tx_date = data.get("date") or date_type.today().isoformat()
    note = data.get("note") or "None"

    return (
        f"📋 Please confirm this transaction:\n"
        f"Type: {type_label}\n"
        f"Amount: {fmt_amount(amount, currency)}\n"
        f"Category: {category}\n"
        f"Date: {tx_date}\n"
        f"Note: {note}"
    )


def fmt_budget_warning(warning: dict) -> str:
    status = warning.get("status", "")
    category = warning.get("category", "")
    limit = warning.get("limit", 0)
    spent = warning.get("current_spend", 0)
    pct = warning.get("percentage_used", 0)
    exceeded_by = warning.get("exceeded_by", 0)
    remaining = max(0.0, limit - spent)

    if status == "exceeded" or exceeded_by > 0:
        return (
            f"⚠️ Budget Alert: {category} budget exceeded!\n"
            f"Limit: {fmt_amount(limit)}\n"
            f"Spent: {fmt_amount(spent)}\n"
            f"Over by: {fmt_amount(exceeded_by)}"
        )
    return (
        f"⚡ Heads up: {category} is at {pct}% of budget\n"
        f"Remaining: {fmt_amount(remaining)}"
    )


def fmt_transaction(tx: dict) -> str:
    tx_type = tx.get("type", "")
    emoji = "💰" if tx_type == "income" else "💸"
    amount = tx.get("amount", 0)
    currency = tx.get("currency", "UZS")
    category = tx.get("category_name", "")
    note = tx.get("note", "")
    tx_date = tx.get("date", "")
    note_part = f"\nNote: {note}" if note else ""
    return f"{emoji} {fmt_amount(amount, currency)} — {category} ({tx_date}){note_part}"


def help_text() -> str:
    return (
        "I didn't quite understand that. You can:\n"
        "• Log a transaction: 'Received 500,000 UZS from client'\n"
        "• Ask a question: 'What did we spend this week?'\n"
        "• Delete last: 'Delete last transaction'"
    )
