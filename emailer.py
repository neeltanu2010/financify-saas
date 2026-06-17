import os
import smtplib
from email.message import EmailMessage

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USER)


def send_otp_email(to_email: str, otp: str):
    if not SMTP_USER or not SMTP_PASSWORD:
        raise RuntimeError("SMTP_USER and SMTP_PASSWORD are required to send OTP emails")

    msg = EmailMessage()
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg["Subject"] = "Your Financify login code"
    msg.set_content(
        f"Your Financify login code is: {otp}\n\n"
        "This code expires in 10 minutes.\n"
        "If you did not request this, ignore this email."
    )

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
