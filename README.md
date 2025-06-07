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

### Interactive CLI

To try a quick interactive session with a basic user profile, run:

```bash
python cli.py
```

The script collects a few onboarding details (risk tolerance, goal, time
horizon) and then lets you type questions until you enter `exit`.

### Plaid Integration

If `PLAID_CLIENT_ID`, `PLAID_SECRET`, and `ACCESS_TOKEN` are provided, the
`InvestmentAgent` will fetch your sandbox account balance via Plaid when a
query explicitly confirms an investment action (e.g. "invest now"). The
projected balance after allocation is included in the response.

When `include_holdings` or `include_expenses` is set in the context the agent
will pull investment positions and recent transactions. Recurring expenses are
summarized to estimate available cash flow for new contributions.
