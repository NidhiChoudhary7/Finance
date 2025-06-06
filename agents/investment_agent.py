"""Simple investment strategy generation.

This agent optionally uses the Plaid API in sandbox mode to fetch the
current account balance when the user confirms an investment action. It
then projects the balance after the suggested allocation."""

from typing import Dict, Any
import os
from .openai_utils import generate_response
from datetime import date, timedelta
from .plaid_service import (
    fetch_account_balance,
    fetch_investment_holdings,
    fetch_recent_transactions,
    summarize_recurring_expenses,
)


class InvestmentAgent:
    """Provides a basic portfolio recommendation."""

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        context = state.get("context", {}) or {}
        amount_str = context.get("amount")
        execute_plaid = context.get("execute_plaid", False)

        risk = context.get("risk_tolerance", "medium")
        goal = context.get("goal")
        esg = context.get("esg", False)
        timeframe = context.get("timeframe")
        include_holdings = context.get("include_holdings", False)
        include_expenses = context.get("include_expenses", False)
        override_fixed_expenses = context.get("override_fixed_expenses", {}) or {}

        access_token = os.getenv("ACCESS_TOKEN") if execute_plaid else None
        starting_balance = fetch_account_balance(access_token) if access_token else None
        holdings = fetch_investment_holdings(access_token) if (access_token and include_holdings) else None

        fixed_expenses = {}
        if access_token and include_expenses:
            end_date = date.today()
            start_date = end_date - timedelta(days=90)
            txns = fetch_recent_transactions(access_token, start_date.isoformat(), end_date.isoformat())
            fixed_expenses = summarize_recurring_expenses(txns)
            fixed_expenses.update(override_fixed_expenses)

        try:
            amount = float(amount_str) if amount_str else None
        except ValueError:
            amount = None

        available_amount = amount
        total_fixed = sum(fixed_expenses.values()) if include_expenses else 0.0
        if amount is not None and include_expenses:
            available_amount = max(0.0, amount - total_fixed)

        # Determine time horizon in years if provided
        horizon = None
        if timeframe and timeframe[1].startswith("year"):
            try:
                horizon = int(timeframe[0])
            except (ValueError, TypeError):
                horizon = None

        # Dynamic allocation based on risk tolerance and time horizon
        risk_map = {"low": 0.4, "medium": 0.6, "high": 0.8}
        risk_score = risk_map.get(risk, 0.6)
        time_score = min(horizon / 30, 1.0) if horizon else 0.5
        stock_pct = 0.3 + 0.6 * (0.5 * risk_score + 0.5 * time_score)
        cash_pct = 0.1 if horizon and horizon < 5 else 0.05
        bond_pct = max(0.0, 1.0 - stock_pct - cash_pct)

        if available_amount is not None:
            stocks = available_amount * stock_pct
            bonds = available_amount * bond_pct
            cash = available_amount * cash_pct

            base = (
                f"Invest ${stocks:.2f} in stocks, ${bonds:.2f} in bonds, and "
                f"keep ${cash:.2f} in cash or equivalents."
            )
            if include_expenses and total_fixed > 0:
                base += (
                    f" After reserving ${total_fixed:.2f} for recurring expenses,"
                    f" ${available_amount:.2f} remains to invest."
                )

            if execute_plaid and starting_balance is not None:
                projected = starting_balance + available_amount
                base += f" Your new balance could be around ${projected:.2f}."

            # Simple growth projections
            projections = {}
            for yrs in [5, 10, 20]:
                total = (
                    stocks * ((1 + 0.07) ** yrs)
                    + bonds * ((1 + 0.03) ** yrs)
                    + cash * ((1 + 0.02) ** yrs)
                )
                if starting_balance is not None:
                    total += starting_balance
                projections[yrs] = total

            proj_str = ", ".join(
                [f"${projections[y]:.2f} in {y}y" for y in [5, 10, 20]]
            )
            base += f" Potential growth: {proj_str}."

            if esg:
                base += " ESG preferences noted."

            if goal:
                base = f"Goal: {goal}. " + base

            result = generate_response(
                f"Provide a short investment suggestion based on: {base}"
            )
        else:
            base = (
                f"Allocate {stock_pct*100:.0f}% stocks, {bond_pct*100:.0f}% bonds"
                f" and {cash_pct*100:.0f}% cash for a diversified portfolio."
            )
            result = generate_response(base)

        metadata = {
            "amount": amount,
            "available_amount": available_amount,
            "risk": risk,
            "goal": goal,
            "horizon": horizon,
            "stock_pct": stock_pct,
            "bond_pct": bond_pct,
            "cash_pct": cash_pct,
        }
        if starting_balance is not None:
            metadata["starting_balance"] = starting_balance
        if holdings is not None:
            metadata["holdings"] = holdings
        if fixed_expenses:
            metadata["fixed_expenses"] = fixed_expenses

        return {
            "result": result,
            "confidence_score": 0.88,
            "metadata": metadata,
        }
