from supabase import create_client
import os

# Connect to Supabase using credentials Hamza will share
def get_supabase():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    return create_client(url, key)


# ── SAVE CONTACT ────────────────────────────────────────────
# Every new customer who messages becomes a contact
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
            # Contact exists — just return their id
            print(f"📋 Existing contact: {phone_number}")
            return existing.data[0]["id"]
        else:
            # New contact — save them
            result = supabase.table("contacts").insert({
                "wa_number": phone_number,
                "business_id": business_id,
                "total_messages": 1
            }).execute()
            print(f"✅ New contact saved: {phone_number}")
            return result.data[0]["id"]

    except Exception as e:
        print(f"⚠️ Error saving contact: {e}")
        return None


# ── SAVE CONVERSATION ───────────────────────────────────────
# One conversation = one chat session with a customer
# ────────────────────────────────────────────────────────────
def save_conversation(contact_id: str, business_id: str = "demo"):
    try:
        supabase = get_supabase()

        # Check if open conversation already exists for this contact
        existing = supabase.table("conversations")\
            .select("*")\
            .eq("contact_id", contact_id)\
            .eq("status", "open")\
            .execute()

        if existing.data:
            # Conversation already open — return its id
            return existing.data[0]["id"]
        else:
            # Start a new conversation
            result = supabase.table("conversations").insert({
                "contact_id": contact_id,
                "business_id": business_id,
                "status": "open"
            }).execute()
            print(f"✅ New conversation started")
            return result.data[0]["id"]

    except Exception as e:
        print(f"⚠️ Error saving conversation: {e}")
        return None


# ── SAVE MESSAGE ────────────────────────────────────────────
# Save every single message — both incoming and outgoing
# ────────────────────────────────────────────────────────────
def save_message(
    conversation_id: str,
    content: str,
    direction: str,      # "in" = customer sent, "out" = BRIO sent
    intent: str = None
):
    try:
        supabase = get_supabase()

        supabase.table("messages").insert({
            "conversation_id": conversation_id,
            "content": content,
            "direction": direction,
            "intent_detected": intent
        }).execute()

        print(f"✅ Message saved ({direction}): {content[:30]}...")

    except Exception as e:
        print(f"⚠️ Error saving message: {e}")


# ── SAVE LEAD ───────────────────────────────────────────────
# Save customer as a lead when they show interest
# ────────────────────────────────────────────────────────────
def save_lead(contact_id: str, business_id: str = "demo", intent: str = None):
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
                "status": "new",
                "notes": f"Intent: {intent}"
            }).execute()
            print(f"✅ New lead saved for contact: {contact_id}")

    except Exception as e:
        print(f"⚠️ Error saving lead: {e}")