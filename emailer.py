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

      <table width="100%" cellpadding="0" cellspacing="0"
             style="background:#0b0b0b;padding:40px 12px;">

        <tr>
          <td align="center">

            <table width="100%" cellpadding="0" cellspacing="0"
                   style="max-width:600px;background:#111111;border:1px solid #2c2208;border-radius:20px;overflow:hidden;">

              <tr>
                <td align="center"
                    style="padding:35px 25px 25px 25px;">

                  <img
                    src="https://financify.blog/wp-content/uploads/2026/05/cropped-2b30e967-7085-4096-b228-4a5cd1e258c9.png"
                    alt="Financify"
                    width="220"
                    style="display:block;margin:0 auto 20px auto;"
                  >

                  <div style="color:#d4af37;font-size:13px;font-weight:bold;letter-spacing:3px;text-transform:uppercase;">
                    Secure Login Verification
                  </div>

                </td>
              </tr>

              <tr>
                <td align="center" style="padding:10px 35px 35px 35px;">

                  <h2 style="margin:0;color:#ffffff;font-size:28px;">
                    Your Login Code
                  </h2>

                  <p style="margin-top:15px;color:#cfcfcf;font-size:16px;line-height:1.6;">
                    Use the verification code below to securely access your Financify dashboard.
                  </p>

                  <div style="
                      margin:30px auto;
                      display:inline-block;
                      padding:18px 32px;
                      border:2px solid #d4af37;
                      border-radius:14px;
                      background:#090909;
                  ">
                    <span style="
                        color:#d4af37;
                        font-size:38px;
                        font-weight:800;
                        letter-spacing:8px;
                    ">
                      {otp}
                    </span>
                  </div>

                  <p style="color:#9f9f9f;font-size:14px;margin-top:20px;">
                    This code expires in 10 minutes.
                  </p>

                </td>
              </tr>

              <tr>
                <td style="
                    background:#0a0a0a;
                    border-top:1px solid #2c2208;
                    padding:20px;
                    text-align:center;
                ">
                  <p style="margin:0;color:#777777;font-size:12px;">
                    If you didn't request this code, you can safely ignore this email.
                  </p>

                  <p style="margin-top:12px;color:#d4af37;font-size:13px;font-weight:bold;">
                    Financify • Money Bees Intelligence
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

    }

    return resend.Emails.send(params)
