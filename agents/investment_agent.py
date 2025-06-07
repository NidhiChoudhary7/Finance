"""Investment portfolio recommendation logic.

This agent can optionally pull account balance, holdings, and recent
transactions using Plaid. When holdings and expenses are provided it
calculates available cash flow and adjusts recommendations to account
for existing assets."""

from typing import Dict, Any
import os
from .openai_utils import generate_response
from datetime import datetime, timedelta
from .plaid_service import (
    fetch_account_balance,
    fetch_investment_holdings,
    fetch_recent_transactions,
)
from .finance_utils import summarize_recurring_expenses, derive_monthly_income


class InvestmentAgent:
    """Provides a basic portfolio recommendation."""

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        context = state.get("context", {}) or {}
        amount_str = context.get("amount")
        execute_plaid = context.get("execute_plaid", False)
        include_holdings = context.get("include_holdings", False)
        include_expenses = context.get("include_expenses", False)
        override_expenses = context.get("override_fixed_expenses", {}) or {}

        risk = context.get("risk_tolerance", "medium")
        goal = context.get("goal")
        esg = context.get("esg", False)
        timeframe = context.get("timeframe")

        access_token = os.getenv("ACCESS_TOKEN") if execute_plaid else None
        starting_balance = fetch_account_balance(access_token) if access_token else None
        current_holdings = fetch_investment_holdings(access_token) if access_token and include_holdings else []

        transactions = []
        if access_token and include_expenses:
            end_date = datetime.utcnow().date()
            start_date = end_date - timedelta(days=90)
            transactions = fetch_recent_transactions(
                access_token, start_date.isoformat(), end_date.isoformat()
            ) or []
        fixed_expenses = summarize_recurring_expenses(transactions)
        fixed_expenses.update(override_expenses)
        monthly_income = derive_monthly_income(transactions)
        available_for_investment = (
            monthly_income - sum(fixed_expenses.values()) if monthly_income else None
        )

        try:
            amount = float(amount_str) if amount_str else None
        except ValueError:
            amount = None

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

        # Compute portfolio context if holdings are available
        total_portfolio_value = (
            (starting_balance or 0) + sum(h.get("market_value", 0) for h in current_holdings)
        )
        current_stock_value = sum(
            h.get("market_value", 0)
            for h in current_holdings
            if str(h.get("type")).lower() in ["equity", "etf", "stock"]
        )
        current_bond_value = sum(
            h.get("market_value", 0) for h in current_holdings if str(h.get("type")).lower() == "bond"
        )
        current_cash_value = starting_balance or 0
        current_stock_pct = current_stock_value / total_portfolio_value if total_portfolio_value else 0
        current_bond_pct = current_bond_value / total_portfolio_value if total_portfolio_value else 0
        current_cash_pct = current_cash_value / total_portfolio_value if total_portfolio_value else 0

        stock_deficit = max(0.0, stock_pct - current_stock_pct) * total_portfolio_value
        bond_deficit = max(0.0, bond_pct - current_bond_pct) * total_portfolio_value

        if amount is not None:
            stocks = amount * stock_pct
            bonds = amount * bond_pct
            cash = amount * cash_pct

            base = (
                f"Invest ${stocks:.2f} in stocks, ${bonds:.2f} in bonds, and "
                f"keep ${cash:.2f} in cash or equivalents."
            )

            if execute_plaid and starting_balance is not None:
                projected = starting_balance + amount
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
        elif available_for_investment is not None:
            stocks = available_for_investment * stock_pct
            bonds = available_for_investment * bond_pct
            cash = available_for_investment * cash_pct
            base = (
                f"Each month invest ${stocks:.2f} in stocks, ${bonds:.2f} in bonds, "
                f"and keep ${cash:.2f} in cash from your available funds."
            )
            if current_holdings:
                base += (
                    f" Your portfolio is currently {current_stock_pct*100:.0f}% stocks, "
                    f"{current_bond_pct*100:.0f}% bonds, {current_cash_pct*100:.0f}% cash."
                )
                base += (
                    f" To reach the target {stock_pct*100:.0f}/{bond_pct*100:.0f}/{cash_pct*100:.0f}, "
                    f"direct new contributions toward ${stock_deficit:.2f} in stocks "
                    f"and ${bond_deficit:.2f} in bonds."
                )
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
            "risk": risk,
            "goal": goal,
            "horizon": horizon,
            "stock_pct": stock_pct,
            "bond_pct": bond_pct,
            "cash_pct": cash_pct,
            "holdings": current_holdings,
            "fixed_expenses": fixed_expenses,
            "monthly_income": monthly_income,
            "available_for_investment": available_for_investment,
        }
        if starting_balance is not None:
            metadata["starting_balance"] = starting_balance

        return {
            "result": result,
            "confidence_score": 0.88,
            "metadata": metadata,
        }
