# Financify Foolproof Login + Paid Tool Access

This package replaces manual email entry with a secure 6-digit email OTP login.

## Backend changes
Upload these files to your Render backend repo:
- `backend/main.py`
- `backend/auth_security.py`
- `backend/emailer.py`
- `backend/database.py`
- `backend/requirements.txt`

Add Render environment variables from `backend/.env.example`.

## Supabase
Run `docs/supabase-login-schema.sql` in Supabase SQL Editor. It adds the `login_otps` table and keeps subscription/usage tables.

## Streamlit tools
Copy `streamlit-integration/protect_tool.py` into each Streamlit app repo, or into a shared `common/` folder.

At the top of each tool:

```python
from protect_tool import require_tool_access, record_tool_use

TOOL_NAME = "bubble-sniffer"
user = require_tool_access(TOOL_NAME)
```

When the user clicks the real run/analyze button:

```python
record_tool_use(TOOL_NAME)
```

Use these names exactly:
- `bubble-sniffer`
- `honey-scanner`
- `macro-dance-floor`
- `portfolio-hive-check`
- `premium-stock-valuation`

## Streamlit secrets

```toml
BACKEND_URL = "https://financify-saas.onrender.com"
SURECART_CHECKOUT_URL = "https://your-surecart-checkout-url"
```
