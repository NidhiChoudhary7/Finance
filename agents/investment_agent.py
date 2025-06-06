"""Simple investment strategy generation."""

from typing import Dict, Any
from .openai_utils import generate_response


class InvestmentAgent:
    """Provides a basic portfolio recommendation."""

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        context = state.get("context", {}) or {}
        amount_str = context.get("amount")

        try:
            amount = float(amount_str) if amount_str else None
        except ValueError:
            amount = None

        if amount is not None:
            stocks = amount * 0.6
            bonds = amount * 0.3
            cash = amount - stocks - bonds
            base = (
                f"Invest ${stocks:.2f} in stocks, ${bonds:.2f} in bonds, and "
                f"keep ${cash:.2f} in cash or equivalents."
            )
            result = generate_response(
                f"Provide a short investment suggestion based on: {base}"
            )
        else:
            base = "Recommend 60% stocks, 30% bonds and 10% cash for a balanced portfolio."
            result = generate_response(base)

        return {
            "result": result,
            "confidence_score": 0.88,
            "metadata": {"amount": amount},
        }
