"""Investment portfolio recommendation logic.

This agent can optionally pull account balance, holdings, and recent
transactions using Plaid. When holdings and expenses are provided it
calculates available cash flow and adjusts recommendations to account
for existing assets."""

from typing import Dict, Any
import os
from .openai_utils import generate_response, generate_json
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

        allocation_prompt = (
            "Suggest portfolio allocation percentages for stocks, bonds and "
            "cash given a risk tolerance of "
            f"{risk} and an investment horizon of {horizon or 'unknown'} years."
            " Respond only with JSON: {\"stocks\": int, \"bonds\": int, \"cash\": int}"
        )
        alloc = generate_json(allocation_prompt, max_tokens=60)
        if alloc:
            stock_pct = alloc.get("stocks", 60) / 100
            bond_pct = alloc.get("bonds", 30) / 100
            cash_pct = alloc.get("cash", 10) / 100
        else:
            # fallback heuristic
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


        if amount is not None:
            stocks = amount * stock_pct
            bonds = amount * bond_pct
            cash = amount * cash_pct
            info = {
                "invest_amount": amount,
                "stocks": stocks,
                "bonds": bonds,
                "cash": cash,
                "balance": starting_balance,
                "goal": goal,
                "esg": esg,
            }
            prompt = (
                "You are an investment advisor. Using the following context, "
                "provide a concise recommendation in two sentences:\n" f"{info}"
            )
            result = generate_response(prompt, max_tokens=120)
        elif available_for_investment is not None:
            stocks = available_for_investment * stock_pct
            bonds = available_for_investment * bond_pct
            cash = available_for_investment * cash_pct
            info = {
                "monthly_available": available_for_investment,
                "stocks": stocks,
                "bonds": bonds,
                "cash": cash,
                "current_allocation": {
                    "stocks": current_stock_pct,
                    "bonds": current_bond_pct,
                    "cash": current_cash_pct,
                },
            }
            prompt = (
                "Advise the user on monthly investment contributions. "
                "Respond in two sentences:\n" f"{info}"
            )
            result = generate_response(prompt, max_tokens=120)
        else:
            info = {
                "target_allocation": {
                    "stocks": stock_pct,
                    "bonds": bond_pct,
                    "cash": cash_pct,
                }
            }
            prompt = (
                "Suggest a generic investment allocation in one sentence:\n" f"{info}"
            )
            result = generate_response(prompt, max_tokens=80)

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
