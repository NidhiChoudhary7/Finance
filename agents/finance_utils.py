from collections import defaultdict
from datetime import datetime
from typing import List, Dict, Any, Optional


def summarize_recurring_expenses(transactions: Optional[List[Dict[str, Any]]]) -> Dict[str, float]:
    """Return average monthly cost for recurring payees."""
    recurring = {}
    if not transactions:
        return recurring
    grouped = defaultdict(list)
    for tx in transactions:
        name = tx.get("name")
        if not name:
            continue
        amount = abs(tx.get("amount", 0))
        date = tx.get("date")
        if not date:
            continue
        grouped[name].append((date, amount))
    for name, entries in grouped.items():
        months = defaultdict(float)
        for date, amount in entries:
            month = date[:7]
            months[month] += amount
        if len(months) >= 2:
            avg = sum(months.values()) / len(months)
            recurring[name] = avg
    return recurring


def derive_monthly_income(transactions: Optional[List[Dict[str, Any]]]) -> float:
    """Estimate average monthly income from positive transactions."""
    if not transactions:
        return 0.0
    monthly = defaultdict(float)
    for tx in transactions:
        amount = tx.get("amount", 0)
        if amount > 0:
            date = tx.get("date")
            if not date:
                continue
            month = date[:7]
            monthly[month] += amount
    if not monthly:
        return 0.0
    return sum(monthly.values()) / len(monthly)


def detect_recent_bonus(transactions: Optional[List[Dict[str, Any]]]) -> Optional[Dict[str, Any]]:
    """Return info about a recent bonus deposit if detected."""
    if not transactions:
        return None

    sorted_txs = sorted(
        transactions,
        key=lambda tx: tx.get("date", ""),
        reverse=True,
    )
    for tx in sorted_txs:
        amount = tx.get("amount", 0)
        if amount and amount >= 5000 and tx.get("name"):
            name_lower = str(tx.get("name", "")).lower()
            categories = [c.lower() for c in (tx.get("category") or [])]
            if "bonus" in name_lower or "bonus" in categories:
                return {
                    "amount": amount,
                    "date": tx.get("date"),
                    "name": tx.get("name"),
                }
    return None
