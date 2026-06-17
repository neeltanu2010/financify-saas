import hmac
import hashlib
import os
from fastapi import FastAPI, Request, HTTPException, Header
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
from auth_security import create_otp, verify_otp, verify_session_token

app = FastAPI(title="Financify Tools Subscription API")

allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class EmailRequest(BaseModel):
    email: EmailStr


class VerifyOtpRequest(BaseModel):
    email: EmailStr
    otp: str


class UsageRequest(BaseModel):
    email: EmailStr
    tool_name: str
    session_token: str


def require_valid_session(email: str, session_token: str):
    verified_email = verify_session_token(session_token)
    if not verified_email or verified_email != email.strip().lower():
        raise HTTPException(status_code=401, detail="Invalid or expired login session")
    return verified_email


@app.get("/")
def home():
    return {
        "status": "ok",
        "app": "Financify Tools Subscription API",
        "login": "email OTP session enabled",
        "blog": "public/free",
        "tools": sorted(list(ALLOWED_TOOLS)),
        "free_limit_per_tool": 5,
        "pro_limit_per_tool": 100,
        "price": "₹499/month",
    }


@app.post("/auth/request-otp")
def request_otp(req: EmailRequest):
    try:
        return create_otp(req.email)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/auth/verify-otp")
def otp_verify(req: VerifyOtpRequest):
    result = verify_otp(req.email, req.otp)
    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result.get("message", "Login failed"))
    return result


@app.post("/user")
def user(req: EmailRequest, authorization: str | None = Header(default=None)):
    # Backward compatible user creation endpoint. Auth required if Authorization header is sent.
    if authorization:
        token = authorization.replace("Bearer ", "").strip()
        require_valid_session(req.email, token)
    return get_or_create_user(req.email)


@app.get("/tools")
def tools():
    return {"tools": sorted(list(ALLOWED_TOOLS))}


@app.post("/usage/check")
def usage_check(req: UsageRequest):
    require_valid_session(req.email, req.session_token)
    try:
        return check_limit(req.email, req.tool_name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/usage/record")
def usage_record(req: UsageRequest):
    require_valid_session(req.email, req.session_token)
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
