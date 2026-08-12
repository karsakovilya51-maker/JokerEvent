import os

def parse_id(val):
    if not val:
        return None
    val = str(val).strip()
    try:
        return int(val)
    except ValueError:
        return val

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/+JlpYTznXUw01OWQy")
SUPPORT_CHAT_URL = os.getenv("SUPPORT_CHAT_URL", "https://t.me/PravovedVayur")

ADMIN_ID = parse_id(os.getenv("ADMIN_ID"))
CHANNEL_ID = parse_id(os.getenv("CHANNEL_ID")) or ADMIN_ID
