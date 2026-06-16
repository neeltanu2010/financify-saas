import os
import requests
import streamlit as st
from supabase import create_client

SUPABASE_URL = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL", ""))
SUPABASE_ANON_KEY = st.secrets.get("SUPABASE_ANON_KEY", os.getenv("SUPABASE_ANON_KEY", ""))
BACKEND_URL = st.secrets.get("BACKEND_URL", os.getenv("BACKEND_URL", "http://localhost:8000"))
SURECART_CHECKOUT_URL = st.secrets.get("SURECART_CHECKOUT_URL", os.getenv("SURECART_CHECKOUT_URL", ""))
APP_URL = st.secrets.get("APP_URL", os.getenv("APP_URL", ""))

supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


def login_box():
    st.sidebar.subheader("Financify Login")

    if "user_email" in st.session_state:
        st.sidebar.success(st.session_state["user_email"])
        if st.sidebar.button("Logout"):
            st.session_state.clear()
            st.rerun()
        return st.session_state["user_email"]

    st.sidebar.caption("Login is required only for tools. Your blog can stay public.")

    email = st.sidebar.text_input("Email")
    if st.sidebar.button("Send Email Login Link"):
        if not email:
            st.sidebar.error("Enter your email first.")
        else:
            supabase.auth.sign_in_with_otp({"email": email})
            st.sidebar.success("Login link sent. Open it from your email.")

    google_url = f"{SUPABASE_URL}/auth/v1/authorize?provider=google&redirect_to={APP_URL}"
    st.sidebar.link_button("Login with Google", google_url)

    st.sidebar.markdown("---")
    manual_email = st.sidebar.text_input("After login, enter same account email")
    if st.sidebar.button("Continue") and manual_email:
        clean_email = manual_email.strip().lower()
        st.session_state["user_email"] = clean_email
        requests.post(f"{BACKEND_URL}/user", json={"email": clean_email}, timeout=15)
        st.rerun()

    st.warning("Please login to use this Financify tool.")
    st.stop()


def require_tool_access(tool_name: str):
    email = login_box()
    response = requests.post(
        f"{BACKEND_URL}/usage/check",
        json={"email": email, "tool_name": tool_name},
        timeout=15,
    )
    data = response.json()

    st.sidebar.info(
        f"{tool_name}\n\nPlan: {data['plan'].upper()}\n\nUsed this month: {data['usage_count']}/{data['limit']}"
    )

    if not data.get("allowed"):
        st.error("Your free limit is finished for this tool. Upgrade to Pro for 100 uses per tool.")
        if SURECART_CHECKOUT_URL:
            st.link_button("Upgrade to Pro ₹499/month", SURECART_CHECKOUT_URL)
        st.stop()

    return email, data


def record_tool_use(email: str, tool_name: str):
    response = requests.post(
        f"{BACKEND_URL}/usage/record",
        json={"email": email, "tool_name": tool_name},
        timeout=15,
    )
    data = response.json()
    if not data.get("allowed") and data.get("remaining", 0) <= 0:
        st.warning("This was your last allowed run for this tool this month.")
    return data
