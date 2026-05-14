import os
import requests
from datetime import datetime


# ── SEND EMAIL VIA BREVO ─────────────────────────────────────
# This is the main function that sends all emails
# ────────────────────────────────────────────────────────────
def send_email(to_email: str, subject: str, content: str):
    try:
        api_key = os.getenv("BREVO_API_KEY")

        url = "https://api.brevo.com/v3/smtp/email"

        headers = {
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json"
        }

        body = {
            "sender": {
                "name": "BRIO Assistant",
                "email": "noreply@neuraflux.io"
            },
            "to": [
                {
                    "email": to_email,
                    "name": "Business Owner"
                }
            ],
            "subject": subject,
            "htmlContent": f"""
                <html>
                <body style="font-family: Arial, sans-serif; 
                             background: #030B07; 
                             color: #E8F4FC; 
                             padding: 20px;">
                    <div style="max-width: 600px; 
                                margin: 0 auto;
                                background: #061410;
                                padding: 30px;
                                border-radius: 12px;
                                border: 1px solid #00E676;">
                        <h2 style="color: #00E676;">BRIO Notification</h2>
                        <p>{content}</p>
                        <hr style="border-color: #00E676; opacity: 0.3;">
                        <p style="color: #7BA8C4; font-size: 12px;">
                            Sent by BRIO — WhatsApp AI Brain by NeuraFlux
                        </p>
                    </div>
                </body>
                </html>
            """
        }

        response = requests.post(url, headers=headers, json=body)

        if response.status_code == 201:
            print(f"✅ Email sent to {to_email}: {subject}")
        else:
            print(f"❌ Email failed: {response.text}")

        return response

    except Exception as e:
        print(f"⚠️ Email error: {e}")
        return None


# ── EMAIL 1 — New Lead ───────────────────────────────────────
# Sent when a new customer messages for first time
# ────────────────────────────────────────────────────────────
def notify_new_lead(
    owner_email: str,
    customer_phone: str,
    intent: str
):
    subject = f"🔥 New Lead from WhatsApp — {customer_phone}"
    content = f"""
        <h3>A new lead just came in!</h3>
        <p><strong>Phone:</strong> {customer_phone}</p>
        <p><strong>Intent:</strong> {intent}</p>
        <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        <p>Login to your BRIO dashboard to see the full conversation.</p>
    """
    send_email(owner_email, subject, content)


# ── EMAIL 2 — Escalation Needed ─────────────────────────────
# Sent when customer needs human help
# ────────────────────────────────────────────────────────────
def notify_escalation(
    owner_email: str,
    customer_phone: str,
    last_message: str
):
    subject = f"🚨 URGENT: Customer needs human help — {customer_phone}"
    content = f"""
        <h3 style="color: #EF4444;">Immediate attention required!</h3>
        <p><strong>Customer:</strong> {customer_phone}</p>
        <p><strong>Last message:</strong> {last_message}</p>
        <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        <p>Please respond to this customer as soon as possible.</p>
    """
    send_email(owner_email, subject, content)


# ── EMAIL 3 — Booking Confirmed ──────────────────────────────
# Sent when customer books an appointment
# ────────────────────────────────────────────────────────────
def notify_booking(
    owner_email: str,
    customer_phone: str,
    booking_date: str
):
    subject = f"📅 New Booking via BRIO — {customer_phone}"
    content = f"""
        <h3 style="color: #00E676;">New appointment booked!</h3>
        <p><strong>Customer:</strong> {customer_phone}</p>
        <p><strong>Scheduled:</strong> {booking_date}</p>
        <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        <p>Check your Cal.com dashboard for full booking details.</p>
    """
    send_email(owner_email, subject, content)


# ── EMAIL 4 — Daily Summary ──────────────────────────────────
# Sent every night at 8pm with daily stats
# ────────────────────────────────────────────────────────────
def send_daily_summary(
    owner_email: str,
    messages_count: int,
    leads_count: int,
    bookings_count: int
):
    subject = f"📊 BRIO Daily Summary — {datetime.now().strftime('%Y-%m-%d')}"
    content = f"""
        <h3>Here's what BRIO did today:</h3>
        <table style="width: 100%; border-collapse: collapse;">
            <tr style="background: #0A1E16;">
                <td style="padding: 12px; color: #7BA8C4;">
                    Messages Handled
                </td>
                <td style="padding: 12px; 
                           color: #00E676; 
                           font-size: 24px; 
                           font-weight: bold;">
                    {messages_count}
                </td>
            </tr>
            <tr>
                <td style="padding: 12px; color: #7BA8C4;">
                    Leads Captured
                </td>
                <td style="padding: 12px; 
                           color: #C0F53D; 
                           font-size: 24px; 
                           font-weight: bold;">
                    {leads_count}
                </td>
            </tr>
            <tr style="background: #0A1E16;">
                <td style="padding: 12px; color: #7BA8C4;">
                    Bookings Made
                </td>
                <td style="padding: 12px; 
                           color: #00E676; 
                           font-size: 24px; 
                           font-weight: bold;">
                    {bookings_count}
                </td>
            </tr>
        </table>
        <p style="margin-top: 20px;">
            BRIO worked 24/7 so you didn't have to. 💚
        </p>
    """
    send_email(owner_email, subject, content)