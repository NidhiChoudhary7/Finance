import os
from typing import Optional
from plaid.api import plaid_api
from plaid import Configuration, ApiClient
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest


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
