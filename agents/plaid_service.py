import os
from typing import Optional
from plaid.api import plaid_api
from plaid import Configuration, ApiClient
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from plaid.model.investments_holdings_get_request import InvestmentsHoldingsGetRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions


def get_client() -> Optional[plaid_api.PlaidApi]:
    client_id = os.getenv("PLAID_CLIENT_ID")
    secret = os.getenv("PLAID_SECRET")
    if not client_id or not secret:
        return None
    configuration = Configuration(host="https://sandbox.plaid.com", api_key={"clientId": client_id, "secret": secret})
    api_client = ApiClient(configuration)
    return plaid_api.PlaidApi(api_client)


def fetch_account_balance(access_token: str) -> Optional[float]:
    client = get_client()
    if not client:
        return None
    try:
        request = AccountsBalanceGetRequest(access_token=access_token)
        response = client.accounts_balance_get(request)
        accounts = response["accounts"]
        if not accounts:
            return None
        return accounts[0]["balances"].get("available") or accounts[0]["balances"].get("current")
    except Exception:
        return None


def fetch_investment_holdings(access_token: str):
    """Retrieve current investment positions with market value."""
    client = get_client()
    if not client:
        return None
    try:
        request = InvestmentsHoldingsGetRequest(access_token=access_token)
        response = client.investments_holdings_get(request)
        holdings = []
        securities = {s["security_id"]: s for s in response.get("securities", [])}
        for h in response.get("holdings", []):
            sec = securities.get(h.get("security_id"), {})
            holdings.append({
                "ticker": sec.get("ticker_symbol"),
                "quantity": h.get("quantity"),
                "market_value": h.get("institution_value"),
            })
        return holdings
    except Exception:
        return None


def fetch_recent_transactions(access_token: str, start_date: str, end_date: str):
    """Fetch raw transactions within a date range."""
    client = get_client()
    if not client:
        return None
    try:
        request = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date,
            options=TransactionsGetRequestOptions(count=500, offset=0),
        )
        response = client.transactions_get(request)
        return response.get("transactions", [])
    except Exception:
        return None


def summarize_recurring_expenses(transactions):
    """Summarize recurring monthly expenses from transaction data."""
    from collections import defaultdict
    from datetime import datetime
    import statistics

    if not transactions:
        return {}

    groups = defaultdict(list)
    for txn in transactions:
        name = txn.get("name")
        amount = txn.get("amount")
        date_str = txn.get("date")
        if not (name and amount and date_str):
            continue
        groups[name].append((amount, date_str))

    recurring = {}
    for name, entries in groups.items():
        if len(entries) < 2:
            continue
        # sort by date
        entries.sort(key=lambda x: x[1])
        dates = [datetime.fromisoformat(d) for _, d in entries]
        diffs = [abs((dates[i] - dates[i-1]).days) for i in range(1, len(dates))]
        if not diffs:
            continue
        avg_diff = sum(diffs) / len(diffs)
        if 25 <= avg_diff <= 35:
            amounts = [amt for amt, _ in entries]
            recurring[name] = round(statistics.mean(amounts), 2)

    return recurring
