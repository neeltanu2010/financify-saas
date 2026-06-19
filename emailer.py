import os
import resend

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL", "Financify <onboarding@resend.dev>")

resend.api_key = RESEND_API_KEY

def financify_login_email_html(otp: str):
    return f"""
    <!DOCTYPE html>
    <html>
    <body style="margin:0;padding:0;background:#0b0b0b;font-family:Arial,Helvetica,sans-serif;">
      <table width="100%" cellpadding="0" cellspacing="0" style="background:#0b0b0b;padding:32px 12px;">
        <tr>
          <td align="center">
            <table width="100%" cellpadding="0" cellspacing="0"
                   style="max-width:560px;background:#111111;border:1px solid #2c2208;border-radius:22px;overflow:hidden;">

              <tr>
                <td style="padding:30px;text-align:center;">
                  <img src="https://financify.blog/logo.png"
                       width="170">

                  <h1 style="color:#ffffff;">
                    Your Financify Login Code
                  </h1>
                </td>
              </tr>

              <tr>
                <td style="padding:30px;text-align:center;">
                  <p style="color:#d7d7d7;">
                    Use the code below to sign in.
                  </p>

                  <div style="padding:20px;border:1px solid #d4af37;border-radius:12px;display:inline-block;">
                    <span style="font-size:36px;color:#d4af37;font-weight:bold;letter-spacing:6px;">
                      {otp}
                    </span>
                  </div>

                  <p style="color:#999;margin-top:20px;">
                    This code expires in 10 minutes.
                  </p>
                </td>
              </tr>

            </table>
          </td>
        </tr>
      </table>
    </body>
    </html>
    """
def send_otp_email(to_email: str, otp: str):
    params = {
        "from": FROM_EMAIL,
        "to": [to_email],
        "subject": "Your Financify login code",
        "html": financify_login_email_html(otp)
        """
    }

    return resend.Emails.send(params)
