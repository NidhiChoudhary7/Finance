"""Simple investment strategy generation.

This agent optionally uses the Plaid API in sandbox mode to fetch the
current account balance when the user confirms an investment action. It
then projects the balance after the suggested allocation."""

from typing import Dict, Any
import os
from .openai_utils import generate_response
from .plaid_service import fetch_account_balance


class InvestmentAgent:
    """Provides a basic portfolio recommendation."""

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        context = state.get("context", {}) or {}
        amount_str = context.get("amount")
        execute_plaid = context.get("execute_plaid", False)

        access_token = os.getenv("ACCESS_TOKEN") if execute_plaid else None
        starting_balance = fetch_account_balance(access_token) if access_token else None

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

            if execute_plaid and starting_balance is not None:
                projected = starting_balance + amount
                base += f" Your new balance could be around ${projected:.2f}."

            result = generate_response(
                f"Provide a short investment suggestion based on: {base}"
            )
        else:
            base = "Recommend 60% stocks, 30% bonds and 10% cash for a balanced portfolio."
            result = generate_response(base)

        metadata = {"amount": amount}
        if starting_balance is not None:
            metadata["starting_balance"] = starting_balance

        return {
            "result": result,
            "confidence_score": 0.88,
            "metadata": metadata,
        }
