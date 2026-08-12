import os
import time
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


# Состояния формы бронирования
class BookingForm(StatesGroup):
    waiting_for_phone = State()


# --- Хэндлеры бота ---

@dp.message(Command("id"))
async def cmd_id(message: types.Message):
    """Команда для быстрого получения ID группы"""
    await message.answer(f"🆔 ID этого чата: `{message.chat.id}`", parse_mode=ParseMode.MARKDOWN)


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    text = (
        "🎩 **Добро пожаловать в Joker Club!**\n\n"
        "Подпишитесь на наш канал и испытайте удачу в бесплатной "
        "лотерее, чтобы забрать свой гарантированный бонус на ближайшую игру!"
    )
    await message.answer(
        text,
        reply_markup=keyboards.get_subscription_keyboard(config.CHANNEL_URL),
        parse_mode=ParseMode.MARKDOWN
    )


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
    category = callback.data.split("_")[1]

    text = (
        "🔥 **Ближайшее мероприятие: Мафия Чикаго 30-х**\n"
        "📅 **Пятница, 19:30 | Ресторан 'Gatsby's'**\n\n"
        "🎟 Обычный билет: 1200 ₽\n"
        "🔥 **Цена для вас (со скидкой): 900 ₽**\n\n"
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
    category = callback.data.split("_")[1]

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
    category = user_data.get("category", "Не указана")
    await state.clear()

    username_str = f"@{message.from_user.username}" if message.from_user.username else "без username"
    lead_text = (
        f"🔥 **НОВЫЙ ГОСТЬ И ЗАЯВКА НА БРОНЬ!**\n\n"
        f"👤 **Гость:** {message.from_user.full_name} ({username_str})\n"
        f"📞 **Телефон:** `{phone}`\n"
        f"🎯 **Категория:** {category}"
    )

    # Пересылаем карточку гостя в группу
    target_chat = config.CHANNEL_ID or config.ADMIN_ID
    if target_chat:
        try:
            await bot.send_message(chat_id=target_chat, text=lead_text, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logging.error(f"Ошибка отправки лида в чат {target_chat}: {e}")

    # Сообщение с подтверждением гостю
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


# --- Веб-сервер для Render ---

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
