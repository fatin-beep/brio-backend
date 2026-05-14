import os


# ── GET BOOKING LINK ─────────────────────────────────────────
# Returns the Cal.com booking link for the business
# ────────────────────────────────────────────────────────────
def get_booking_link() -> str:
    # Sarmad will provide the real Cal.com link
    cal_link = os.getenv(
        "CAL_COM_LINK",
        "https://cal.com/neuraflux/demo"
    )
    return cal_link


# ── GET BOOKING MESSAGE ──────────────────────────────────────
# Returns the full message to send when customer wants booking
# ────────────────────────────────────────────────────────────
def get_booking_message() -> str:
    link = get_booking_link()
    return f"""Great! I'd love to help you book an appointment. 📅

Please use this link to choose a time that works for you:
{link}

Once you book, you'll receive a confirmation email automatically. 
Is there anything else I can help you with?"""