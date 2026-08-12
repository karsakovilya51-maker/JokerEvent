import os
import time
import random
import asyncio
import logging
from aiohttp import web

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import config
import keyboards

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

# Кулдаун лотереи
user_cooldowns = {}
COOLDOWN_SECONDS = 300

# Понятные названия категорий для карточки заявки
CATEGORY_NAMES = {
    "mafia": "Мафия Чикаго 30-х",
    "chgk": "Что? Где? Когда?",
    "lecture_movie": "Лекция / Кино",
    "speed_dating": "Скоростные свидания (10 девушек за 1 час)",
}

# Список предсказаний Оракула
ORACLE_PREDICTIONS = [
    "✨ **Сегодня вы встретите человека, который поможет вам решить накопившиеся проблемы.** Будьте внимательны к окружению — не упустите этот знак!",
    "🔥 **Удача любит смелых!** Вечер в хорошей компании принесет вам неожиданное, но крайне выгодное предложение. Время действовать!",
    "🚪 **Звезды говорят, что сегодня отличный день, чтобы рискнуть и попробовать что-то новое.** Шаг за пределы привычного откроет перед вами нужную дверь.",
    "🤝 **В ближайшее время вас ждет знакомство, которое изменит ваши планы на ближайший месяц.** Будьте открыты к новым людям!",
    "🌟 **Ваш внутренний магнетизм сегодня на пике!** Самое время оказаться в центре внимания и проявить себя.",
    "🎁 **Судьба готовит вам приятный сюрприз.** Чтобы запустить цепочку счастливых событий, сделайте первый шаг навстречу новым впечатлениям уже сегодня.",
    "🗝 **Тайна, которая вас беспокоила, откроется в непринужденной беседе.** Позвольте себе расслабиться и провести вечер среди единомышленников.",
    "⚡️ **Ключ к вашему успеху на этой неделе — новые социальные связи.** Заведите разговор с тем, с кем давно хотели познакомиться.",
    "🔋 **Интуиция подсказывает: пора отвлечься от рутины.** Смена обстановки и азарт игры подзарядят вашу энергию на 100%.",
    "🏆 **Сегодня любой ваш риск превратится в триумф.** Доверьтесь случаю и не бойтесь быть в самом центре событий!"
]


# Состояния формы бронирования
class BookingForm(StatesGroup):
    waiting_for_phone = State()


# --- Хэндлеры бота ---

@dp.message(Command("id"))
async def cmd_id(message: types.Message):
    """Команда для быстрого получения ID группы"""
    await message.answer(f"🆔 ID этого чата: `{message.chat.id}`", parse_mode=ParseMode.MARKDOWN)


@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    text = (
        "🎩 **Добро пожаловать в Joker Club!**\n\n"
        "Испытайте удачу в бесплатной лотерее, "
        "чтобы забрать свой гарантированный бонус на ближайшую игру!"
    )
    await message.answer(
        text,
        reply_markup=keyboards.get_start_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )


@dp.callback_query(F.data == "main_menu")
async def main_menu_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()

    text = (
        "🎩 **Главное меню Joker Club**\n\n"
        "Выберите интересующее мероприятие, загляните к Оракулу или подпишитесь на наш канал:"
    )
    await callback.message.answer(
        text,
        reply_markup=keyboards.get_categories_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )


# --- Раздел «Предсказания Оракула» ---

@dp.callback_query(F.data == "oracle_start")
async def oracle_start_handler(callback: types.CallbackQuery):
    await callback.answer()
    text = (
        "🔮 **Оракул Joker Club готов открыть тайны судьбы...**\n\n"
        "Доверьтесь своей интуиции и выберите **одну из трех карт**:"
    )
    await callback.message.answer(
        text,
        reply_markup=keyboards.get_oracle_cards_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )


@dp.callback_query(F.data.startswith("oracle_card_"))
async def oracle_card_handler(callback: types.CallbackQuery):
    await callback.answer()
    card_num = callback.data.split("oracle_card_")[1]
    prediction = random.choice(ORACLE_PREDICTIONS)

    text = (
        f"🎴 **Карта №{card_num} открыта!**\n\n"
        f"📜 **Откровение Оракула:**\n\n"
        f"{prediction}"
    )
    await callback.message.answer(
        text,
        reply_markup=keyboards.get_oracle_result_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )


# --- Рулетка и Мероприятия ---

@dp.callback_query(F.data == "spin_slots")
async def spin_slots_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    now = time.time()

    if user_id in user_cooldowns:
        elapsed = now - user_cooldowns[user_id]
        if elapsed < COOLDOWN_SECONDS:
            remaining_seconds = int(COOLDOWN_SECONDS - elapsed)
            minutes = remaining_seconds // 60
            seconds = remaining_seconds % 60

            time_str = f"{minutes} мин {seconds} сек" if minutes > 0 else f"{seconds} сек"

            await callback.answer(
                f"⏳ Испытать удачу снова можно через {time_str}!",
                show_alert=True
            )
            return

    user_cooldowns[user_id] = now
    await callback.answer()

    msg = await callback.message.answer_dice(emoji="🎰")
    await asyncio.sleep(2.5)

    val = msg.dice.value

    if val == 64:
        text = (
            "🔥 **ДЖЕКПОТ! ТРИ СЕМЕРКИ!** 🔥\n\n"
            "Невероятная удача! Вы выбили максимальный куш:\n"
            "🎁 **Скидка 500 ₽** на билет + **Welcome-drink** на баре!\n\n"
            "Выберите мероприятие для бронирования:"
        )
    elif val in [1, 22, 43]:
        text = (
            "🎉 **СУПЕР-ВЫИГРЫШ!** 🎉\n\n"
            "Отличная комбинация! Сегодня удача на вашей стороне:\n"
            "🎁 Ваш бонус: **Скидка 400 ₽** на входной билет!\n\n"
            "Выберите мероприятие для бронирования:"
        )
    else:
        text = (
            "🃏 **ВЫ В ИГРЕ!** 🃏\n\n"
            "В клубе Джокера проигравших не бывает!\n"
            "🎁 Вы выиграли гарантированную **скидку 300 ₽** на ближайший вечер!\n\n"
            "Выберите мероприятие для бронирования:"
        )

    await callback.message.answer(
        text,
        reply_markup=keyboards.get_categories_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )


@dp.callback_query(F.data.startswith("category_"))
async def category_handler(callback: types.CallbackQuery):
    await callback.answer()
    category = callback.data.split("category_")[1]

    if category == "mafia":
        text = (
            "🔥 **Ближайшее мероприятие: Мафия Чикаго 30-х**\n"
            "📅 **Пятница, 19:30 | Ресторан 'Gatsby's'**\n\n"
            "🎟 Обычный билет: 1200 ₽\n"
            "🔥 **Цена для вас (со скидкой): 900 ₽**\n\n"
            "_Скидка забронирована за вами на 24 часа._"
        )
    elif category == "chgk":
        text = (
            "🧠 **Ближайшее мероприятие: Что? Где? Когда?**\n"
            "📅 **Суббота, 18:00 | Ресторан 'Gatsby's'**\n\n"
            "🎟 Обычный билет: 1000 ₽\n"
            "🔥 **Цена для вас (со скидкой): 700 ₽**\n\n"
            "_Скидка забронирована за вами на 24 часа._"
        )
    elif category == "lecture_movie":
        text = (
            "🎬 **Ближайшее мероприятие: Лекция / Кино**\n"
            "📅 **Воскресенье, 17:00 | Joker Club**\n\n"
            "🎟 Обычный билет: 800 ₽\n"
            "🔥 **Цена для вас (со скидкой): 500 ₽**\n\n"
            "_Скидка забронирована за вами на 24 часа._"
        )
    elif category == "speed_dating":
        text = (
            "💘 **Ближайшее мероприятие: Скоростные свидания**\n"
            "🔥 **10 девушек за 1 час!**\n"
            "📅 **Суббота, 20:00 | Joker Club**\n\n"
            "🎟 Обычный билет: 1500 ₽\n"
            "🔥 **Цена для вас (со скидкой): 1200 ₽**\n\n"
            "_Скидка забронирована за вами на 24 часа._"
        )
    else:
        text = (
            "✨ **Ближайшее мероприятие Joker Club**\n\n"
            "🔥 **Цена для вас со скидкой активна!**\n\n"
            "_Скидка забронирована за вами на 24 часа._"
        )

    await callback.message.answer(
        text,
        reply_markup=keyboards.get_booking_keyboard(category),
        parse_mode=ParseMode.MARKDOWN
    )


# --- Пошаговый сценарий бронирования ---

@dp.callback_query(F.data.startswith("buy_"))
async def buy_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    category = callback.data.split("buy_")[1]

    await state.update_data(category=category)
    await state.set_state(BookingForm.waiting_for_phone)

    await callback.message.answer(
        "📱 **Укажите ваш номер телефона для фиксации брони:**\n\n"
        "Нажмите кнопку ниже, чтобы поделиться контактом, или введите номер вручную в чат:",
        reply_markup=keyboards.get_phone_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )


@dp.message(BookingForm.waiting_for_phone)
async def process_phone_step(message: types.Message, state: FSMContext):
    if message.contact:
        phone = message.contact.phone_number
    else:
        phone = message.text

    user_data = await state.get_data()
    category_code = user_data.get("category", "Не указана")
    category_name = CATEGORY_NAMES.get(category_code, category_code)
    await state.clear()

    username_str = f"@{message.from_user.username}" if message.from_user.username else "без username"
    lead_text = (
        f"🔥 **НОВЫЙ ГОСТЬ И ЗАЯВКА НА БРОНЬ!**\n\n"
        f"👤 **Гость:** {message.from_user.full_name} ({username_str})\n"
        f"📞 **Телефон:** `{phone}`\n"
        f"🎯 **Категория:** {category_name}"
    )

    # Пересылаем карточку гостя в рабочий чат
    target_chat = config.CHANNEL_ID or config.ADMIN_ID
    if target_chat:
        try:
            await bot.send_message(chat_id=target_chat, text=lead_text, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logging.error(f"Ошибка отправки лида в чат {target_chat}: {e}")

    # Подтверждение гостю
    user_text = (
        "✅ **Заявка зарегистрирована!**\n\n"
        "Перейдите в рабочий чат проекта и напишите организатору:\n"
        "👉 **«Хочу забронировать место»**"
    )
    await message.answer(
        user_text,
        reply_markup=keyboards.get_organizer_redirect_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )


# --- Веб-сервер для поддержки активности на Render ---

async def handle_ping(request):
    return web.Response(text="OK", status=200)


async def main():
    asyncio.create_task(dp.start_polling(bot))

    app = web.Application()
    app.router.add_get("/", handle_ping)

    port = int(os.getenv("PORT", 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
