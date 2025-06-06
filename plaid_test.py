from plaid.api import plaid_api
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_account_filters import LinkTokenAccountFilters
# from plaid.model.accounts_filter import AccountsFilter
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_response import TransactionsGetResponse
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from plaid.model.transactions_sync_response import TransactionsSyncResponse

from plaid import Configuration, ApiClient
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta


load_dotenv()

# Configure Plaid client
configuration = Configuration(
    host="https://sandbox.plaid.com",
    api_key={
        'clientId': os.getenv("PLAID_CLIENT_ID"),
        'secret': os.getenv("PLAID_SECRET")
    }
)
api_client = ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

# Access token you got earlier
access_token = os.getenv("ACCESS_TOKEN")

# Create request object
start_date = datetime.now().date() - timedelta(days=30)
end_date = datetime.now().date()

request = TransactionsGetRequest(
    access_token=access_token,
    start_date=start_date,
    end_date=end_date,
    options=TransactionsGetRequestOptions(count=10, offset=0)
)


# Make API call
response = client.transactions_get(request)
transactions = response['transactions']

# Print transactions
for txn in transactions:
    print(f"{txn.date} - {txn.name} - ${txn.amount}")
