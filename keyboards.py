from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
import config


def get_subscription_keyboard(channel_url: str):
    """Клавиатура с подпиской и запуском рулетки"""
    builder = InlineKeyboardBuilder()
    builder.button(text="📢 Подписаться на канал", url=channel_url)
    builder.button(text="🎰 Испытать удачу", callback_data="spin_slots")
    builder.adjust(1)
    return builder.as_markup()


def get_categories_keyboard():
    """Клавиатура выбора категории/игры"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🕵️‍♂️ Мафия Чикаго 30-х", callback_data="category_mafia")
    builder.button(text="🏠 Главное меню", callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()


def get_booking_keyboard(category: str):
    """Клавиатура детализации игры и бронирования"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🎟 Забронировать место (900 ₽)", callback_data=f"buy_{category}")
    builder.button(text="❓ Задать вопрос организатору", url=config.SUPPORT_CHAT_URL)
    builder.button(text="🏠 Главное меню", callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()


def get_phone_keyboard():
    """Кнопка для отправки номера телефона"""
    builder = ReplyKeyboardBuilder()
    builder.button(text="📱 Поделиться номером телефона", request_contact=True)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def get_organizer_redirect_keyboard():
    """Финальная клавиатура после регистрации заявки"""
    builder = InlineKeyboardBuilder()
    builder.button(text="💬 Написать организатору", url=config.SUPPORT_CHAT_URL)
    builder.button(text="🏠 Главное меню", callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()
