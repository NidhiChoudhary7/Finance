# FinLife Navigator

A toy multi-agent financial planning assistant built with LangGraph.

## Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment variables**
   - `OPENAI_API_KEY` – OpenAI key for language model responses (optional).
   - `PLAID_CLIENT_ID` and `PLAID_SECRET` – credentials for Plaid API (optional, required for Plaid features).
   - `ACCESS_TOKEN` – Plaid access token for fetching account data.

   You can create a `.env` file and export the keys:
   ```bash
   export OPENAI_API_KEY=YOUR_OPENAI_KEY
   export PLAID_CLIENT_ID=YOUR_PLAID_ID
   export PLAID_SECRET=YOUR_PLAID_SECRET
   export ACCESS_TOKEN=YOUR_ACCESS_TOKEN
   ```

## Running

Execute the demo scenarios:

```bash
python main.py
```

This will run a few sample queries through the FinLife Navigator graph.

### Plaid Integration

If `PLAID_CLIENT_ID`, `PLAID_SECRET`, and `ACCESS_TOKEN` are provided, the
`InvestmentAgent` can pull real account data via Plaid when the query requests it.
Set `include_holdings` or `include_expenses` in the context (or mention them in
the prompt) to fetch investment holdings and summarize recurring expenses. These
values are used to validate that any suggested allocation is affordable.
The account balance is still fetched when a user confirms an investment action
(e.g. "invest now").

### Context Flags for `InvestmentAgent`

You can influence how the investment agent gathers data and tailors
recommendations by supplying optional keys in the `context` object or by
mentioning them in your prompt:

- `risk_tolerance`: `low`, `medium`, or `high` (defaults to `medium`)
- `timeframe`: a tuple like `["5", "year"]` describing your horizon
- `goal`: e.g. `retirement`, `buy_home`, or `emergency_fund`
- `include_holdings`: set to `true` to fetch your existing investments
- `include_expenses`: set to `true` to analyze recurring expenses
- `override_fixed_expenses`: dictionary mapping expense names to amounts

These inputs allow the agent to compute an appropriate allocation and ensure it
fits your actual cash flow.
