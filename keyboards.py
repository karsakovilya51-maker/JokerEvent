from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_subscription_keyboard(channel_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="1. Подписаться на канал 📢", url=channel_url)],
            [InlineKeyboardButton(text="2. Забрать скидку 🎁", callback_data="check_subscription")]
        ]
    )

def get_categories_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🕵️ Мафия в стиле Чикаго 30-х", callback_data="category_mafia")],
            [InlineKeyboardButton(text="🧠 Что? Где? Когда?", callback_data="category_chgk")],
            [InlineKeyboardButton(text="🎓 Образовательные лекции", callback_data="category_lectures")],
            [InlineKeyboardButton(text="🔥 Интересно всё!", callback_data="category_all")]
        ]
    )

def get_booking_keyboard(event_code: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎟 Забронировать место (900 ₽)", callback_data=f"buy_{event_code}")],
            [InlineKeyboardButton(text="❓ Задать вопрос организатору", url="https://t.me/your_admin_contact")]
        ]
    )
