from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
import config


def get_start_keyboard():
    """Клавиатура для первого экрана при сканировании QR-кода (только рулетка)"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🎰 Испытать удачу", callback_data="spin_slots")
    return builder.as_markup()


def get_categories_keyboard():
    """Главное меню с мероприятиями и кнопкой подписки на канал"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🕵️‍♂️ Мафия Чикаго 30-х", callback_data="category_mafia")
    builder.button(text="🧠 Что? Где? Когда?", callback_data="category_chgk")
    builder.button(text="🎬 Лекция / Кино", callback_data="category_lecture_movie")
    builder.button(text="💘 Скоростные свидания (10 девушек за 1 час)", callback_data="category_speed_dating")
    builder.button(text="📢 Подписаться на канал", url=config.CHANNEL_URL)
    builder.button(text="🏠 Главное меню", callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()


def get_booking_keyboard(category: str):
    """Клавиатура детализации игры и бронирования"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🎟 Забронировать место", callback_data=f"buy_{category}")
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
