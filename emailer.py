import os
import resend

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL", "Financify <onboarding@resend.dev>")

resend.api_key = RESEND_API_KEY


def send_otp_email(to_email: str, otp: str):
    params = {
        "from": FROM_EMAIL,
        "to": [to_email],
        "subject": "Your Financify login code",
        "html": f"""
        <h2>Your Financify Login Code</h2>
        <p>Your OTP is:</p>
        <h1>{otp}</h1>
        <p>This code expires in 10 minutes.</p>
        """
    }

    return resend.Emails.send(params)
