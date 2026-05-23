from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
import os
import json
import requests
from database import save_contact, save_conversation, save_message, save_lead, get_business_id
from ai_agent import get_ai_reply
from notifications import notify_new_lead, notify_escalation
from booking import get_booking_message

router = APIRouter()


# ── REQUEST MODEL ────────────────────────────────────────────
class SendMessageRequest(BaseModel):
    phone_number: str
    message: str


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
# Meta sends hub.mode, hub.verify_token, hub.challenge with DOTS
# Query aliases handle this correctly
# ────────────────────────────────────────────────────────────
@router.get("/whatsapp/webhook")
def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    VERIFY_TOKEN = os.getenv("WEBHOOK_VERIFY_TOKEN")

    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        print("✅ Webhook verified!")
        return PlainTextResponse(content=hub_challenge, status_code=200)
    else:
        print(f"❌ Verification failed — token mismatch")
        raise HTTPException(status_code=403, detail="Verification token mismatch")


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
            print(f"\n{'='*60}")
            print(f"📩 Message from {phone_number}: {text}")
            print(f"{'='*60}\n")

            # ── STEP 0: Get business ID ─────────────────────────────────────
            business_id = get_business_id()
            if not business_id:
                print("❌ CRITICAL: Failed to get business_id")
                return {"status": "error", "detail": "No business found"}
            print(f"✅ STEP 0 COMPLETE: BUSINESS_ID = {business_id}\n")

            # ── STEP 1: Save contact ────────────────────────────────────────
            contact_id = save_contact(phone_number, business_id)
            if not contact_id:
                print("❌ CRITICAL: Failed to save contact")
                return {"status": "error", "detail": "Contact creation failed"}
            print(f"✅ STEP 1 COMPLETE: CONTACT_ID = {contact_id}\n")

            # ── STEP 2: Save conversation ───────────────────────────────────
            conversation_id = save_conversation(contact_id, business_id)
            if not conversation_id:
                print("❌ CRITICAL: Failed to create conversation")
                return {"status": "error", "detail": "Conversation creation failed"}
            print(f"✅ STEP 2 COMPLETE: CONVERSATION_ID = {conversation_id}\n")

            # ── STEP 3: Save incoming message ───────────────────────────────
            msg_saved = save_message(
                conversation_id=conversation_id,
                content=text,
                direction="in"
            )
            if not msg_saved:
                print("❌ WARNING: Failed to save incoming message")
            else:
                print(f"✅ STEP 3 COMPLETE: Incoming message saved\n")

            # ── STEP 4: Get AI reply ────────────────────────────────────────
            ai_response = await get_ai_reply(text, phone_number)
            reply = ai_response["reply"]
            intent = ai_response["intent"]
            escalate = ai_response["escalate"]
            print(f"✅ STEP 4 COMPLETE: AI reply = '{reply[:30]}...', intent = {intent}\n")

            # ── STEP 5: If booking request send Cal.com link ────────────────
            if intent == "BOOKING_REQUEST":
                reply = get_booking_message()
                print(f"📅 Booking link sent to {phone_number}\n")

            # ── STEP 6: Save outgoing message ───────────────────────────────
            msg_saved = save_message(
                conversation_id=conversation_id,
                content=reply,
                direction="out",
                intent=intent
            )
            if not msg_saved:
                print("❌ WARNING: Failed to save outgoing message")
            else:
                print(f"✅ STEP 6 COMPLETE: Outgoing message saved\n")

            # ── STEP 7: Save lead ───────────────────────────────────────────
            lead_id = save_lead(contact_id, business_id, intent=intent)
            if not lead_id:
                print("❌ WARNING: Failed to save lead")
            else:
                print(f"✅ STEP 7 COMPLETE: LEAD_ID = {lead_id}\n")

            # ── STEP 8: Send new lead notification email ────────────────────
            if owner_email:
                notify_new_lead(owner_email, phone_number, intent)
                print(f"✅ STEP 8 COMPLETE: Notification sent to {owner_email}\n")

            # ── STEP 9: Send escalation email if needed ─────────────────────
            if escalate and owner_email:
                notify_escalation(owner_email, phone_number, text)
                reply = """I understand this needs special attention.
I've notified our team and someone will get back to you shortly.
Thank you for your patience! 🙏"""
                print(f"✅ STEP 9 COMPLETE: Escalation sent\n")

            # ── STEP 10: Send reply on WhatsApp ─────────────────────────────
            send_whatsapp_message(phone_number, reply)
            print(f"✅ STEP 10 COMPLETE: Reply sent on WhatsApp\n")
            print(f"{'='*60}\n")

        return {"status": "ok"}

    except Exception as e:
        print(f"⚠️ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "detail": str(e)}


# ── ENDPOINT 3 — Manual send ─────────────────────────────────
@router.post("/whatsapp/send")
async def send_message(request_data: SendMessageRequest):
    try:
        response = send_whatsapp_message(
            request_data.phone_number,
            request_data.message
        )
        return {"status": "ok", "whatsapp_response": response.text}

    except Exception as e:
        return {"status": "error", "detail": str(e)}