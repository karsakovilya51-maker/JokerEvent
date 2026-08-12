from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import config

def get_subscription_keyboard(channel_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="1. Подписаться на канал 📢", url=channel_url)],
            [InlineKeyboardButton(text="2. 🎰 Испытать удачу в лотерее", callback_data="spin_slots")]
        ]
    )

def get_categories_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🕵️ Мафия Чикаго", callback_data="category_mafia")],
            [InlineKeyboardButton(text="🧠 Что? Где? Когда?", callback_data="category_chgk")],
            [InlineKeyboardButton(text="🎓 Лекции и кино", callback_data="category_lectures")],
            [InlineKeyboardButton(text="🔥 Показать все варианты", callback_data="category_all")]
        ]
    )

def get_booking_keyboard(category: str) -> InlineKeyboardMarkup:
    support_url = getattr(config, 'SUPPORT_CHAT_URL', 'https://t.me/+JlpYTznXUw01OWQy')
    if not support_url.startswith("http"):
        support_url = f"https://{support_url}"

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎟 Забронировать место (900 ₽)", 
                    callback_data=f"buy_{category}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❓ Задать вопрос организатору", 
                    url=support_url
                )
            ]
        ]
    )
