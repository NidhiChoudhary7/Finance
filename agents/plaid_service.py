import os
from typing import Optional, List, Dict, Any
from plaid.api import plaid_api
from plaid import Configuration, ApiClient
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from plaid.model.investments_holdings_get_request import InvestmentsHoldingsGetRequest
from plaid.model.transactions_get_request import TransactionsGetRequest


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


def fetch_investment_holdings(access_token: str) -> Optional[List[Dict[str, Any]]]:
    """Return simplified holdings information for the given access token."""
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
            quantity = h.get("quantity") or 0
            price = h.get("institution_price") or 0
            holdings.append({
                "ticker": sec.get("ticker_symbol"),
                "quantity": quantity,
                "market_value": quantity * price,
                "type": sec.get("type")
            })
        return holdings
    except Exception:
        return None


def fetch_recent_transactions(access_token: str, start_date: str, end_date: str) -> Optional[List[Dict[str, Any]]]:
    """Fetch recent transactions within the date range."""
    client = get_client()
    if not client:
        return None
    try:
        request = TransactionsGetRequest(access_token=access_token, start_date=start_date, end_date=end_date)
        response = client.transactions_get(request)
        txs = []
        for tx in response.get("transactions", []):
            txs.append({
                "name": tx.get("name"),
                "amount": tx.get("amount"),
                "date": tx.get("date"),
                "category": tx.get("category")
            })
        return txs
    except Exception:
        return None
