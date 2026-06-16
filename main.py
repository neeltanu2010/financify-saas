import hmac
import hashlib
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from database import (
    ALLOWED_TOOLS,
    check_limit,
    record_usage,
    activate_subscription,
    cancel_subscription,
    get_or_create_user,
)

app = FastAPI(title="Financify Tools Subscription API")

allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class UserRequest(BaseModel):
    email: EmailStr


class UsageRequest(BaseModel):
    email: EmailStr
    tool_name: str


@app.get("/")
def home():
    return {
        "status": "ok",
        "app": "Financify Tools Subscription API",
        "blog": "public/free",
        "tools": sorted(list(ALLOWED_TOOLS)),
        "free_limit_per_tool": 5,
        "pro_limit_per_tool": 100,
        "price": "₹499/month"
    }


@app.post("/user")
def user(req: UserRequest):
    return get_or_create_user(req.email)


@app.get("/tools")
def tools():
    return {"tools": sorted(list(ALLOWED_TOOLS))}


@app.post("/usage/check")
def usage_check(req: UsageRequest):
    try:
        return check_limit(req.email, req.tool_name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/usage/record")
def usage_record(req: UsageRequest):
    try:
        return record_usage(req.email, req.tool_name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/surecart/webhook")
async def surecart_webhook(request: Request):
    body = await request.body()
    secret = os.getenv("SURECART_WEBHOOK_SECRET", "")
    signature = request.headers.get("surecart-signature") or request.headers.get("x-surecart-signature")

    if secret and signature:
        expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, signature):
            raise HTTPException(status_code=401, detail="Invalid webhook signature")

    payload = await request.json()
    event_type = payload.get("type", "") or payload.get("event", "")
    data = payload.get("data", {}) or {}

    customer = data.get("customer", {}) or {}
    email = (
        data.get("email")
        or data.get("customer_email")
        or customer.get("email")
        or data.get("billing_email")
    )
    customer_id = customer.get("id") or data.get("customer_id")
    order_id = data.get("id") or data.get("order_id")

    if not email:
        return {"received": True, "message": "No email found in webhook payload."}

    active_events = {
        "order.paid",
        "purchase.created",
        "subscription.created",
        "subscription.activated",
        "subscription.active",
    }
    cancel_events = {
        "subscription.canceled",
        "subscription.cancelled",
        "subscription.revoked",
        "subscription.expired",
        "subscription.deleted",
    }

    if event_type in active_events:
        activate_subscription(email, customer_id, order_id)
        return {"received": True, "status": "activated", "email": email}

    if event_type in cancel_events:
        cancel_subscription(email)
        return {"received": True, "status": "cancelled", "email": email}

    return {"received": True, "ignored_event_type": event_type}
