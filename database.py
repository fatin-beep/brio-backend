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
def save_contact(phone_number: str, business_id: str = "demo", name: str = None):
    try:
        supabase = get_supabase()

        # Fetch first business to get business_id
        try:
            business = supabase.table('businesses').select('id').limit(1).execute()

            if not business.data:
                print("⚠️ No business found in businesses table, using default")
                final_business_id = business_id
            else:
                final_business_id = business.data[0]['id']
        except Exception as be:
            print(f"⚠️ Error fetching business: {be}, using default")
            final_business_id = business_id

        # Create or update contact using upsert
        try:
            contact_result = supabase.table('contacts').upsert({
                'wa_number': phone_number,
                'name': name if name else 'Unknown',
                'business_id': final_business_id,
                'first_seen': datetime.utcnow().isoformat(),
                'last_seen': datetime.utcnow().isoformat(),
                'total_messages': 1
            }, on_conflict='wa_number').execute()

            print(f"✅ SUCCESS CONTACT: {contact_result.data[0]['id'] if contact_result.data else 'upserted'}")
            return contact_result.data[0]['id'] if contact_result.data else None

        except Exception as ce:
            print(f"❌ CONTACT ERROR: {str(ce)}")
            return None

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
        try:
            existing = supabase.table("conversations")\
                .select("*")\
                .eq("contact_id", contact_id)\
                .eq("status", "open")\
                .execute()

            if existing.data:
                print(f"✅ SUCCESS CONVERSATION: Found existing conversation {existing.data[0]['id']}")
                return existing.data[0]["id"]
        except Exception as qe:
            print(f"❌ CONVERSATION QUERY ERROR: {str(qe)}")
            return None

        # Create new conversation if none exists
        try:
            result = supabase.table("conversations").insert({
                "contact_id": contact_id,
                "business_id": business_id,
                "status": "open",
                "created_at": datetime.utcnow().isoformat()
            }).execute()

            print(f"✅ SUCCESS CONVERSATION: New conversation created {result.data[0]['id'] if result.data else 'unknown'}")
            return result.data[0]["id"] if result.data else None

        except Exception as ie:
            print(f"❌ CONVERSATION INSERT ERROR: {str(ie)}")
            return None

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

        try:
            result = supabase.table("messages").insert({
                "conversation_id": conversation_id,
                "content": content,
                "direction": direction,
                "timestamp": datetime.utcnow().isoformat(),
                "intent_detected": intent
            }).execute()

            print(f"✅ SUCCESS MESSAGE: Saved ({direction}): {content[:30]}")
            return True

        except Exception as ie:
            print(f"❌ MESSAGE INSERT ERROR: {str(ie)}")
            return False

    except Exception as e:
        print(f"⚠️ Error saving message: {e}")
        return False


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
        try:
            existing = supabase.table("leads")\
                .select("*")\
                .eq("contact_id", contact_id)\
                .execute()

            if existing.data:
                print(f"✅ SUCCESS LEAD: Existing lead found for contact {contact_id}")
                return existing.data[0]["id"] if existing.data else None
        except Exception as qe:
            print(f"❌ LEAD QUERY ERROR: {str(qe)}")
            return None

        # Create new lead if none exists
        try:
            result = supabase.table("leads").insert({
                "contact_id": contact_id,
                "business_id": business_id,
                "created_at": datetime.utcnow().isoformat(),
                "status": "new",
                "notes": f"Intent: {intent}"
            }).execute()

            print(f"✅ SUCCESS LEAD: New lead saved for contact {contact_id}")
            return result.data[0]["id"] if result.data else None

        except Exception as ie:
            print(f"❌ LEAD INSERT ERROR: {str(ie)}")
            return None

    except Exception as e:
        print(f"⚠️ Error saving lead: {e}")
        return None


# ── GET BUSINESS CONFIG ─────────────────────────────────----
# Matches Hamza's businesses table:
# id, name, wa_number, wa_token, 
# knowledge_base, ai_persona, owner_email
# ────────────────────────────────────────────────────────────
def get_business_config(business_id: str = "demo"):
    try:
        supabase = get_supabase()

        try:
            result = supabase.table("businesses")\
                .select("*")\
                .eq("id", business_id)\
                .execute()

            if result.data:
                print(f"✅ SUCCESS BUSINESS: Config fetched for {business_id}")
                return result.data[0]
            else:
                print(f"⚠️ BUSINESS NOT FOUND: {business_id}")
                return None

        except Exception as qe:
            print(f"❌ BUSINESS QUERY ERROR: {str(qe)}")
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

        try:
            result = supabase.table("bookings").insert({
                "lead_id": lead_id,
                "cal_com_booking_id": cal_com_booking_id,
                "scheduled_at": scheduled_at,
                "status": "confirmed"
            }).execute()

            print(f"✅ SUCCESS BOOKING: Booking saved for lead {lead_id}")
            return True

        except Exception as ie:
            print(f"❌ BOOKING INSERT ERROR: {str(ie)}")
            return False

    except Exception as e:
        print(f"⚠️ Error saving booking: {e}")
        return False
