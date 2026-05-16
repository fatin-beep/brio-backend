from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import PlainTextResponse
import os
import json
import requests
from database import save_contact, save_conversation, save_message, save_lead
from ai_agent import get_ai_reply
from notifications import notify_new_lead, notify_escalation
from booking import get_booking_message

router = APIRouter()


# ── HELPER — Send WhatsApp message ──────────────────────────
def send_whatsapp_message(phone_number: str, message: str):
    token = os.getenv("WHATSAPP_ACCESS_TOKEN")
    phone_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

    url = f"https://graph.facebook.com/v18.0/{phone_id}/messages"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    body = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "text",
        "text": {"body": message}
    }

    response = requests.post(url, headers=headers, json=body)

    if response.status_code == 200:
        print(f"✅ Reply sent to {phone_number}")
    else:
        print(f"❌ Failed to send: {response.text}")

    return response


# ── ENDPOINT 1 — Webhook verification ───────────────────────
@router.get("/whatsapp/webhook")
def verify_webhook(
    hub_mode: str = None,
    hub_verify_token: str = None,
    hub_challenge: str = None
):
    VERIFY_TOKEN = os.getenv("WEBHOOK_VERIFY_TOKEN")

    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        print("✅ Webhook verified!")
        return PlainTextResponse(content=hub_challenge)
    else:
        raise HTTPException(status_code=403, detail="Verification failed")


# ── ENDPOINT 2 — Receive & process message ──────────────────
@router.post("/whatsapp/webhook")
async def receive_message(request: Request):
    try:
        body = await request.body()
        data = json.loads(body)

        entry = data.get("entry", [])
        if not entry:
            return {"status": "ok"}

        changes = entry[0].get("changes", [])
        if not changes:
            return {"status": "ok"}

        value = changes[0].get("value", {})
        messages = value.get("messages", [])

        if not messages:
            return {"status": "ok"}

        message = messages[0]
        phone_number = message.get("from")
        message_type = message.get("type")

        # Get owner email for notifications
        owner_email = os.getenv("BUSINESS_OWNER_EMAIL", "")

        if message_type == "text":
            text = message["text"]["body"]
            print(f"📩 Message from {phone_number}: {text}")

            # Step 1 — Save contact
            contact_id = save_contact(phone_number)

            # Step 2 — Save conversation
            conversation_id = save_conversation(contact_id)

            # Step 3 — Save incoming message
            save_message(
                conversation_id=conversation_id,
                content=text,
                direction="in"
            )

            # Step 4 — Get AI reply
            ai_response = await get_ai_reply(text, phone_number)
            reply = ai_response["reply"]
            intent = ai_response["intent"]
            escalate = ai_response["escalate"]

            # Step 5 — If booking request send Cal.com link
            if intent == "BOOKING_REQUEST":
                reply = get_booking_message()
                print(f"📅 Booking link sent to {phone_number}")

            # Step 6 — Save outgoing message
            save_message(
                conversation_id=conversation_id,
                content=reply,
                direction="out",
                intent=intent
            )

            # Step 7 — Save lead
            save_lead(contact_id, intent=intent)

            # Step 8 — Send new lead notification email
            if owner_email:
                notify_new_lead(owner_email, phone_number, intent)

            # Step 9 — Send escalation email if needed
            if escalate and owner_email:
                notify_escalation(owner_email, phone_number, text)
                reply = """I understand this needs special attention.
I've notified our team and someone will get back to you shortly.
Thank you for your patience! 🙏"""

            # Step 10 — Send reply on WhatsApp
            send_whatsapp_message(phone_number, reply)

        return {"status": "ok"}

    except Exception as e:
        print(f"⚠️ Error: {e}")
        return {"status": "ok"}


# ── ENDPOINT 3 — Manual send ─────────────────────────────────
@router.post("/whatsapp/send")
async def send_message(request: Request):
    try:
        data = await request.json()
        phone_number = data.get("phone_number")
        message = data.get("message")

        if not phone_number or not message:
            raise HTTPException(
                status_code=400,
                detail="phone_number and message are required"
            )

        response = send_whatsapp_message(phone_number, message)
        return {"status": "ok", "whatsapp_response": response.text}

    except Exception as e:
        return {"status": "error", "detail": str(e)}