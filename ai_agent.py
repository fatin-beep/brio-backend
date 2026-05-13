import httpx
import os

# ── CALL ABDULLAH'S AI ──────────────────────────────────────
# This sends the customer message to Abdullah's AI
# and gets back a smart reply
# ────────────────────────────────────────────────────────────
async def get_ai_reply(message: str, phone_number: str) -> dict:
    try:
        # Abdullah will give us his AI endpoint URL
        # For now we use a placeholder until he shares it
        ai_url = os.getenv("AI_AGENT_URL", "http://localhost:8001/agent")

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                ai_url,
                json={
                    "message": message,
                    "phone_number": phone_number
                }
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "reply": data.get("reply", ""),
                    "intent": data.get("intent", "GENERAL_INQUIRY"),
                    "escalate": data.get("escalate", False)
                }
            else:
                print(f"⚠️ AI error: {response.text}")
                return {
                    "reply": "Thank you for your message! Our team will get back to you shortly.",
                    "intent": "GENERAL_INQUIRY",
                    "escalate": False
                }

    except Exception as e:
        print(f"⚠️ AI connection error: {e}")
        # Fallback reply if AI is down
        return {
            "reply": "Hello! Thanks for messaging us. BRIO is here 24/7 😊",
            "intent": "GENERAL_INQUIRY",
            "escalate": False
        }