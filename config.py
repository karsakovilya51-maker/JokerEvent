import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
CHANNEL_URL = os.getenv("CHANNEL_URL")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# Ссылка на рабочий чат для перенаправления лидов
SUPPORT_CHAT_URL = os.getenv("SUPPORT_CHAT_URL", "https://t.me/+JlpYTznXUw01OWQy")

if not BOT_TOKEN or not CHANNEL_ID or not CHANNEL_URL:
    raise ValueError("Ошибка: Не заполнены обязательные переменные окружения!")
