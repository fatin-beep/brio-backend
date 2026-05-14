from supabase import create_client
import os
from datetime import datetime


def get_supabase():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    return create_client(url, key)


# ── SAVE CONTACT ────────────────────────────────────────────
# Matches Hamza's contacts table:
# id, wa_number, name, first_seen, last_seen, 
# total_messages, business_id
# ────────────────────────────────────────────────────────────
def save_contact(phone_number: str, business_id: str = "demo"):
    try:
        supabase = get_supabase()

        # Check if contact already exists
        existing = supabase.table("contacts")\
            .select("*")\
            .eq("wa_number", phone_number)\
            .execute()

        if existing.data:
            # Contact exists — update last_seen and total_messages
            contact_id = existing.data[0]["id"]
            current_total = existing.data[0]["total_messages"] or 0

            supabase.table("contacts").update({
                "last_seen": datetime.utcnow().isoformat(),
                "total_messages": current_total + 1
            }).eq("id", contact_id).execute()

            print(f"📋 Existing contact updated: {phone_number}")
            return contact_id
        else:
            # New contact — save them
            result = supabase.table("contacts").insert({
                "wa_number": phone_number,
                "business_id": business_id,
                "first_seen": datetime.utcnow().isoformat(),
                "last_seen": datetime.utcnow().isoformat(),
                "total_messages": 1
            }).execute()

            print(f"✅ New contact saved: {phone_number}")
            return result.data[0]["id"]

    except Exception as e:
        print(f"⚠️ Error saving contact: {e}")
        return None


# ── SAVE CONVERSATION ───────────────────────────────────────
# Matches Hamza's conversations table:
# id, contact_id, business_id, created_at, status
# ────────────────────────────────────────────────────────────
def save_conversation(contact_id: str, business_id: str = "demo"):
    try:
        supabase = get_supabase()

        # Check if open conversation already exists
        existing = supabase.table("conversations")\
            .select("*")\
            .eq("contact_id", contact_id)\
            .eq("status", "open")\
            .execute()

        if existing.data:
            return existing.data[0]["id"]
        else:
            result = supabase.table("conversations").insert({
                "contact_id": contact_id,
                "business_id": business_id,
                "status": "open",
                "created_at": datetime.utcnow().isoformat()
            }).execute()

            print(f"✅ New conversation started")
            return result.data[0]["id"]

    except Exception as e:
        print(f"⚠️ Error saving conversation: {e}")
        return None


# ── SAVE MESSAGE ────────────────────────────────────────────
# Matches Hamza's messages table:
# id, conversation_id, direction, content, 
# timestamp, intent_detected
# ────────────────────────────────────────────────────────────
def save_message(
    conversation_id: str,
    content: str,
    direction: str,
    intent: str = None
):
    try:
        supabase = get_supabase()

        supabase.table("messages").insert({
            "conversation_id": conversation_id,
            "content": content,
            "direction": direction,
            "timestamp": datetime.utcnow().isoformat(),
            "intent_detected": intent
        }).execute()

        print(f"✅ Message saved ({direction}): {content[:30]}")

    except Exception as e:
        print(f"⚠️ Error saving message: {e}")


# ── SAVE LEAD ───────────────────────────────────────────────
# Matches Hamza's leads table:
# id, contact_id, business_id, created_at, 
# status, notes, booking_id
# ────────────────────────────────────────────────────────────
def save_lead(
    contact_id: str,
    business_id: str = "demo",
    intent: str = None
):
    try:
        supabase = get_supabase()

        # Check if lead already exists
        existing = supabase.table("leads")\
            .select("*")\
            .eq("contact_id", contact_id)\
            .execute()

        if not existing.data:
            supabase.table("leads").insert({
                "contact_id": contact_id,
                "business_id": business_id,
                "created_at": datetime.utcnow().isoformat(),
                "status": "new",
                "notes": f"Intent: {intent}"
            }).execute()

            print(f"✅ New lead saved")

    except Exception as e:
        print(f"⚠️ Error saving lead: {e}")


# ── GET BUSINESS CONFIG ─────────────────────────────────────
# Matches Hamza's businesses table:
# id, name, wa_number, wa_token, 
# knowledge_base, ai_persona, owner_email
# ────────────────────────────────────────────────────────────
def get_business_config(business_id: str = "demo"):
    try:
        supabase = get_supabase()

        result = supabase.table("businesses")\
            .select("*")\
            .eq("id", business_id)\
            .execute()

        if result.data:
            return result.data[0]
        return None

    except Exception as e:
        print(f"⚠️ Error getting business config: {e}")
        return None


# ── SAVE BOOKING ────────────────────────────────────────────
# Matches Hamza's bookings table:
# id, lead_id, cal_com_booking_id, scheduled_at, status
# ────────────────────────────────────────────────────────────
def save_booking(
    lead_id: str,
    cal_com_booking_id: str,
    scheduled_at: str
):
    try:
        supabase = get_supabase()

        supabase.table("bookings").insert({
            "lead_id": lead_id,
            "cal_com_booking_id": cal_com_booking_id,
            "scheduled_at": scheduled_at,
            "status": "confirmed"
        }).execute()

        print(f"✅ Booking saved")

    except Exception as e:
        print(f"⚠️ Error saving booking: {e}")