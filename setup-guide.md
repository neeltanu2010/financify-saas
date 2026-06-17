# Financify Tools Subscription Setup

This folder protects only the Financify tools, not your whole blog.

## What this includes

- Supabase user/subscription storage
- SureCart webhook for ₹499/month Pro plan
- 5 free runs per tool every month
- 100 Pro runs per tool every month
- Streamlit integration file to paste into your existing tools

## Current protected tools

- bubble-sniffer
- honey-scanner
- macro-dance-floor
- portfolio-hive-check
- premium-stock-valuation

## Setup

1. Run `docs/supabase-schema.sql` in Supabase SQL editor.
2. Enable Supabase Email login and Google login.
3. Deploy `backend` on Railway/Render.
4. Add backend environment variables from `backend/.env.example`.
5. Create SureCart ₹499/month product.
6. Add SureCart webhook URL:

```text
https://your-backend-domain.com/surecart/webhook
```

7. Copy `streamlit-integration/auth_client.py` into your existing tools project.
8. Add this at the top of each existing tool app:

```python
from auth_client import require_tool_access, record_tool_use

TOOL_NAME = "bubble-sniffer"
email, status = require_tool_access(TOOL_NAME)
```

9. After successful tool run, record usage:

```python
record_tool_use(email, TOOL_NAME)
```

Use the correct tool name for each app.

## Important

Do not put the login check on normal blog pages. Only put it inside the Streamlit/Python tool apps.
