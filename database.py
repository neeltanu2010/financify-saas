import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise RuntimeError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

FREE_LIMIT_PER_TOOL = 5
PRO_LIMIT_PER_TOOL = 100
PRICE_INR = 499

ALLOWED_TOOLS = {
    "bubble-sniffer",
    "honey-scanner",
    "macro-dance-floor",
    "portfolio-hive-check",
    "premium-stock-valuation",
}


def current_month() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m")


def validate_tool(tool_name: str):
    if tool_name not in ALLOWED_TOOLS:
        raise ValueError(f"Unknown tool_name: {tool_name}")


def get_or_create_user(email: str):
    email = email.strip().lower()
    found = supabase.table("users").select("*").eq("email", email).execute()
    if found.data:
        return found.data[0]

    created = supabase.table("users").insert({
        "email": email,
        "plan": "free",
        "subscription_status": "inactive"
    }).execute()
    return created.data[0]


def get_or_create_tool_usage(email: str, tool_name: str, usage_month: str = None):
    validate_tool(tool_name)
    email = email.strip().lower()
    usage_month = usage_month or current_month()

    result = (
        supabase.table("tool_usage")
        .select("*")
        .eq("email", email)
        .eq("tool_name", tool_name)
        .eq("usage_month", usage_month)
        .execute()
    )
    if result.data:
        return result.data[0]

    created = supabase.table("tool_usage").insert({
        "email": email,
        "tool_name": tool_name,
        "usage_month": usage_month,
        "usage_count": 0
    }).execute()
    return created.data[0]


def check_limit(email: str, tool_name: str):
    email = email.strip().lower()
    usage_month = current_month()
    user = get_or_create_user(email)
    usage = get_or_create_tool_usage(email, tool_name, usage_month)

    is_pro = user["plan"] == "pro" and user["subscription_status"] == "active"
    limit = PRO_LIMIT_PER_TOOL if is_pro else FREE_LIMIT_PER_TOOL
    allowed = usage["usage_count"] < limit

    return {
        "allowed": allowed,
        "email": email,
        "tool_name": tool_name,
        "usage_month": usage_month,
        "plan": user["plan"],
        "subscription_status": user["subscription_status"],
        "usage_count": usage["usage_count"],
        "limit": limit,
        "remaining": max(limit - usage["usage_count"], 0),
        "blog_access": "public",
        "tools_access": "protected"
    }


def record_usage(email: str, tool_name: str):
    email = email.strip().lower()
    status = check_limit(email, tool_name)
    if not status["allowed"]:
        return status

    usage_month = status["usage_month"]
    usage = get_or_create_tool_usage(email, tool_name, usage_month)
    new_count = usage["usage_count"] + 1

    supabase.table("tool_usage").update({
        "usage_count": new_count,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }).eq("email", email).eq("tool_name", tool_name).eq("usage_month", usage_month).execute()

    supabase.table("usage_logs").insert({
        "email": email,
        "tool_name": tool_name,
        "usage_month": usage_month
    }).execute()

    status["usage_count"] = new_count
    status["remaining"] = max(status["limit"] - new_count, 0)
    status["allowed"] = new_count < status["limit"]
    return status


def activate_subscription(email: str, customer_id: str = None, order_id: str = None):
    email = email.strip().lower()
    get_or_create_user(email)

    supabase.table("users").update({
        "plan": "pro",
        "subscription_status": "active",
        "surecart_customer_id": customer_id,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }).eq("email", email).execute()

    supabase.table("subscriptions").insert({
        "email": email,
        "plan": "pro",
        "amount": PRICE_INR,
        "status": "active",
        "surecart_customer_id": customer_id,
        "surecart_order_id": order_id
    }).execute()


def cancel_subscription(email: str):
    email = email.strip().lower()
    supabase.table("users").update({
        "plan": "free",
        "subscription_status": "inactive",
        "updated_at": datetime.now(timezone.utc).isoformat()
    }).eq("email", email).execute()
