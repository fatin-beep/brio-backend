import hmac
import hashlib
import os


# ── VERIFY WHATSAPP SIGNATURE ────────────────────────────────
# Meta sends a signature with every webhook request
# We verify it to make sure request is really from Meta
# ────────────────────────────────────────────────────────────
def verify_whatsapp_signature(payload: bytes, signature: str) -> bool:
    try:
        app_secret = os.getenv("WHATSAPP_APP_SECRET", "")

        if not app_secret:
            print("⚠️ No app secret set — skipping signature check")
            return True

        expected = hmac.new(
            app_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        expected_signature = f"sha256={expected}"

        return hmac.compare_digest(expected_signature, signature)

    except Exception as e:
        print(f"⚠️ Signature error: {e}")
        return False