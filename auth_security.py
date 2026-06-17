import base64
import hashlib
import hmac
import json
import os
import random
import time
from datetime import datetime, timedelta, timezone

from database import supabase, get_or_create_user
from emailer import send_otp_email

APP_SECRET = os.getenv("APP_SECRET", "change-this-secret-now")
OTP_TTL_MINUTES = int(os.getenv("OTP_TTL_MINUTES", "10"))
SESSION_TTL_DAYS = int(os.getenv("SESSION_TTL_DAYS", "30"))


def _hash(value: str) -> str:
    return hmac.new(APP_SECRET.encode(), value.encode(), hashlib.sha256).hexdigest()


def create_otp(email: str):
    email = email.strip().lower()
    get_or_create_user(email)
    otp = f"{random.randint(100000, 999999)}"
    expires_at = (datetime.now(timezone.utc) + timedelta(minutes=OTP_TTL_MINUTES)).isoformat()

    # Invalidate previous unused OTPs for same email
    supabase.table("login_otps").update({"used": True}).eq("email", email).eq("used", False).execute()
    supabase.table("login_otps").insert({
        "email": email,
        "otp_hash": _hash(email + ":" + otp),
        "expires_at": expires_at,
        "used": False,
        "attempts": 0,
    }).execute()

    send_otp_email(email, otp)
    return {"sent": True, "email": email, "expires_in_minutes": OTP_TTL_MINUTES}


def make_session_token(email: str) -> str:
    payload = {
        "email": email.strip().lower(),
        "exp": int(time.time()) + SESSION_TTL_DAYS * 24 * 60 * 60,
    }
    raw = json.dumps(payload, separators=(",", ":")).encode()
    body = base64.urlsafe_b64encode(raw).decode().rstrip("=")
    sig = hmac.new(APP_SECRET.encode(), body.encode(), hashlib.sha256).hexdigest()
    return f"{body}.{sig}"


def verify_session_token(token: str) -> str | None:
    try:
        body, sig = token.split(".", 1)
        expected = hmac.new(APP_SECRET.encode(), body.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, sig):
            return None
        padded = body + "=" * (-len(body) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded.encode()))
        if int(payload.get("exp", 0)) < int(time.time()):
            return None
        return payload.get("email", "").strip().lower()
    except Exception:
        return None


def verify_otp(email: str, otp: str):
    email = email.strip().lower()
    otp = otp.strip()

    result = (
        supabase.table("login_otps")
        .select("*")
        .eq("email", email)
        .eq("used", False)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    if not result.data:
        return {"ok": False, "message": "No active login code. Request a new code."}

    row = result.data[0]
    if row.get("attempts", 0) >= 5:
        supabase.table("login_otps").update({"used": True}).eq("id", row["id"]).execute()
        return {"ok": False, "message": "Too many attempts. Request a new code."}

    expires_at = datetime.fromisoformat(row["expires_at"].replace("Z", "+00:00"))
    if expires_at < datetime.now(timezone.utc):
        supabase.table("login_otps").update({"used": True}).eq("id", row["id"]).execute()
        return {"ok": False, "message": "Code expired. Request a new code."}

    supabase.table("login_otps").update({"attempts": row.get("attempts", 0) + 1}).eq("id", row["id"]).execute()

    if not hmac.compare_digest(row["otp_hash"], _hash(email + ":" + otp)):
        return {"ok": False, "message": "Invalid code."}

    supabase.table("login_otps").update({"used": True}).eq("id", row["id"]).execute()
    get_or_create_user(email)
    return {"ok": True, "email": email, "session_token": make_session_token(email)}
