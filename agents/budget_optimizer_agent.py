"""Simple budget optimization logic."""

from typing import Dict, Any
from .openai_utils import generate_response


class BudgetOptimizerAgent:
    """Suggests a basic allocation for disposable income."""

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        context = state.get("context", {}) or {}
        amount_str = context.get("amount")

        try:
            amount = float(amount_str) if amount_str else None
        except ValueError:
            amount = None

        if amount is not None:
            savings = amount * 0.5
            investing = amount * 0.3
            fun = amount - savings - investing
            base = (
                f"Allocate ${savings:.2f} to savings, ${investing:.2f} to investments, "
                f"and ${fun:.2f} for discretionary spending."
            )
            result = generate_response(
                f"Suggest a short budgeting tip based on: {base}"
            )
        else:
            base = (
                "Optimize by allocating 50% to savings, 30% to investments and 20% to discretionary spending."
            )
            result = generate_response(base)

        return {
            "result": result,
            "confidence_score": 0.82,
            "metadata": {"amount": amount},
        }
