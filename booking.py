import os


def get_booking_link() -> str:
    cal_link = os.getenv(
        "CAL_COM_LINK",
        "https://cal.com/neuraflux/demo"
    )
    return cal_link


def get_booking_message() -> str:
    link = get_booking_link()
    return f"""Great! I'd love to help you book an appointment. 📅

Please use this link to choose a time that works for you:
{link}

Once you book, you'll receive a confirmation email automatically.
Is there anything else I can help you with?"""