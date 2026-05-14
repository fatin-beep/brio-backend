from fastapi import APIRouter, HTTPException
from database import get_supabase
from typing import Optional

router = APIRouter()


# ── GET ALL CONVERSATIONS ───────────────────────────────────
# Usman uses this for /conversations page
# Returns list of all conversations with contact info
# ────────────────────────────────────────────────────────────
@router.get("/conversations")
def get_conversations(business_id: str = "demo"):
    try:
        supabase = get_supabase()

        result = supabase.table("conversations")\
            .select("*, contacts(*)")\
            .eq("business_id", business_id)\
            .order("created_at", desc=True)\
            .execute()

        return {"status": "ok", "data": result.data}

    except Exception as e:
        return {"status": "error", "detail": str(e)}


# ── GET SINGLE CONVERSATION THREAD ──────────────────────────
# Usman uses this for /conversations/[id] page
# Returns all messages in one conversation
# ────────────────────────────────────────────────────────────
@router.get("/conversations/{conversation_id}")
def get_conversation_thread(conversation_id: str):
    try:
        supabase = get_supabase()

        # Get conversation details
        conversation = supabase.table("conversations")\
            .select("*, contacts(*)")\
            .eq("id", conversation_id)\
            .execute()

        if not conversation.data:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Get all messages in this conversation
        messages = supabase.table("messages")\
            .select("*")\
            .eq("conversation_id", conversation_id)\
            .order("timestamp", desc=False)\
            .execute()

        return {
            "status": "ok",
            "conversation": conversation.data[0],
            "messages": messages.data
        }

    except Exception as e:
        return {"status": "error", "detail": str(e)}


# ── GET ALL LEADS ────────────────────────────────────────────
# Usman uses this for /leads page
# Returns all leads with contact info
# ────────────────────────────────────────────────────────────
@router.get("/leads")
def get_leads(business_id: str = "demo"):
    try:
        supabase = get_supabase()

        result = supabase.table("leads")\
            .select("*, contacts(*)")\
            .eq("business_id", business_id)\
            .order("created_at", desc=True)\
            .execute()

        return {"status": "ok", "data": result.data}

    except Exception as e:
        return {"status": "error", "detail": str(e)}


# ── GET ANALYTICS ────────────────────────────────────────────
# Usman uses this for /analytics page
# Returns stats: messages today, leads today, etc
# ────────────────────────────────────────────────────────────
@router.get("/analytics")
def get_analytics(business_id: str = "demo"):
    try:
        supabase = get_supabase()
        from datetime import datetime, date

        today = date.today().isoformat()

        # Count messages today
        messages_today = supabase.table("messages")\
            .select("id", count="exact")\
            .gte("timestamp", today)\
            .execute()

        # Count leads today
        leads_today = supabase.table("leads")\
            .select("id", count="exact")\
            .eq("business_id", business_id)\
            .gte("created_at", today)\
            .execute()

        # Count bookings today
        bookings_today = supabase.table("bookings")\
            .select("id", count="exact")\
            .gte("scheduled_at", today)\
            .execute()

        # Count total conversations
        total_conversations = supabase.table("conversations")\
            .select("id", count="exact")\
            .eq("business_id", business_id)\
            .execute()

        return {
            "status": "ok",
            "data": {
                "messages_today": messages_today.count or 0,
                "leads_today": leads_today.count or 0,
                "bookings_today": bookings_today.count or 0,
                "total_conversations": total_conversations.count or 0,
                "avg_response_time_seconds": 3
            }
        }

    except Exception as e:
        return {"status": "error", "detail": str(e)}


# ── GET BUSINESS CONFIG ──────────────────────────────────────
# Usman uses this for /settings page
# Returns current AI configuration
# ────────────────────────────────────────────────────────────
@router.get("/business/config")
def get_business_config(business_id: str = "demo"):
    try:
        supabase = get_supabase()

        result = supabase.table("businesses")\
            .select("*")\
            .eq("id", business_id)\
            .execute()

        if not result.data:
            return {
                "status": "ok",
                "data": {
                    "id": "demo",
                    "name": "Demo Business",
                    "wa_number": "",
                    "knowledge_base": "",
                    "ai_persona": "Professional but warm",
                    "owner_email": ""
                }
            }

        return {"status": "ok", "data": result.data[0]}

    except Exception as e:
        return {"status": "error", "detail": str(e)}


# ── UPDATE BUSINESS CONFIG ───────────────────────────────────
# Usman uses this for /settings page save button
# Updates AI configuration
# ────────────────────────────────────────────────────────────
@router.post("/business/config")
async def update_business_config(request_data: dict):
    try:
        supabase = get_supabase()

        business_id = request_data.get("id", "demo")

        # Check if business exists
        existing = supabase.table("businesses")\
            .select("*")\
            .eq("id", business_id)\
            .execute()

        if existing.data:
            # Update existing
            supabase.table("businesses").update({
                "name": request_data.get("name"),
                "knowledge_base": request_data.get("knowledge_base"),
                "ai_persona": request_data.get("ai_persona"),
                "owner_email": request_data.get("owner_email")
            }).eq("id", business_id).execute()
        else:
            # Create new
            supabase.table("businesses").insert({
                "id": business_id,
                "name": request_data.get("name"),
                "knowledge_base": request_data.get("knowledge_base"),
                "ai_persona": request_data.get("ai_persona"),
                "owner_email": request_data.get("owner_email")
            }).execute()

        return {"status": "ok", "message": "Business config updated"}

    except Exception as e:
        return {"status": "error", "detail": str(e)}