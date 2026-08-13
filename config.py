import os

# Токен бота от @BotFather
BOT_TOKEN = os.getenv("BOT_TOKEN", "ВАШ_ТОКЕН_БОТА")

# Ваш личный Telegram ID (@PravovedVayur) для логов и уведомлений
ADMIN_ID = 7632952660

# ID рабочего чата/канала для заявок (если нет отдельного чата, отправляет вам)
CHANNEL_ID = int(os.getenv("CHANNEL_ID", ADMIN_ID))

# Ссылки для инлайн-кнопок
CHANNEL_URL = "https://t.me/your_channel_link"      # Ссылка на ваш Telegram-канал
SUPPORT_CHAT_URL = "https://t.me/PravovedVayur"     # Ссылка на диалог с вами
