import os
import asyncio
import logging
from datetime import datetime, timedelta

from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode, ChatMemberStatus
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, CallbackQuery
from aiogram.client.default import DefaultBotProperties
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import config
import keyboards

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
scheduler = AsyncIOScheduler()

# Обработчик для проверки состояния сервиса на Render (Health Check)
async def handle_health_check(request):
    return web.Response(text="Bot is running OK")

async def is_user_subscribed(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=config.CHANNEL_ID, user_id=user_id)
        return member.status not in (ChatMemberStatus.LEFT, ChatMemberStatus.KICKED)
    except Exception as e:
        logging.error(f"Ошибка проверки подписки: {e}")
        return False

async def send_followup_message(user_id: int):
    text = (
        "⏳ <b>Ваш промокод сгорит через несколько часов!</b>\n\n"
        "Вы еще можете успеть забронировать стол со скидкой 300 ₽ на ближайшую игру.\n"
        "Атмосфера, стильные фото и отличная компания гарантированы!"
    )
    try:
        await bot.send_message(chat_id=user_id, text=text)
    except Exception as e:
        logging.error(f"Не удалось отправить догрев: {e}")

@dp.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject):
    source = command.args if command.args else "direct"
    logging.info(f"Пользователь {message.from_user.id} зашел с источника: {source}")

    text = (
        f"Привет, {message.from_user.first_name}! 👋\n\n"
        "Мы организуем атмосферные вечера в заведениях города: от гангстерской Мафии до интеллектуальных битв.\n\n"
        "🎁 <b>Ваш промокод на 300 ₽ почти готов!</b>\n"
        "Чтобы активировать скидку, подпишитесь на наш основной Telegram-канал с анонсами."
    )
    await message.answer(
        text=text,
        reply_markup=keyboards.get_subscription_keyboard(config.CHANNEL_URL)
    )

@dp.callback_query(F.data == "check_subscription")
async def process_check_subscription(callback: CallbackQuery):
    user_id = callback.from_user.id
    if await is_user_subscribed(user_id):
        await callback.answer("Подтверждено! Скидка активирована 🎉")
        text = (
            "✅ <b>Подписка подтверждена!</b>\n"
            "Ваш промокод: <code>GANGSTER2026</code> (дает скидку 300 ₽).\n\n"
            "Отметьте, какие мероприятия вам наиболее интересны:"
        )
        await callback.message.edit_text(
            text=text,
            reply_markup=keyboards.get_categories_keyboard()
        )
    else:
        await callback.answer(
            "❌ Вы еще не подписались на канал! Подпишитесь и нажмите кнопку снова.", 
            show_alert=True
        )

@dp.callback_query(F.data.startswith("category_"))
async def process_category_selection(callback: CallbackQuery):
    category = callback.data.split("_")[1]
    user_id = callback.from_user.id

    events_info = {
        "mafia": "🕵️ <b>Мафия в стиле Чикаго 30-х</b>\n📅 Пятница, 19:30 | Ресторан 'Gatsbys'\nДресс-код, фотограф, атмосферная музыка.",
        "chgk": "🧠 <b>Что? Где? Когда?</b>\n📅 Четверг, 19:00 | Бар 'Шерлок'\nИнтеллектуальная битва для команд и соло-игроков.",
        "lectures": "🎓 <b>Лекция: Тайны истории кино</b>\n📅 Воскресенье, 17:00 | Кофейня 'Модерн'\nУвлекательный разбор от эксперта.",
        "all": "🔥 <b>Ближайшее мероприятие: Мафия Чикаго 30-х</b>\n📅 Пятница, 19:30 | Ресторан 'Gatsbys'"
    }

    selected_text = events_info.get(category, events_info["all"])
    
    text = (
        f"{selected_text}\n\n"
        "🎟 <b>Обычный билет:</b> 1200 ₽\n"
        "🔥 <b>Цена для вас (со скидкой 300 ₽):</b> 900 ₽\n\n"
        "<i>Скидка забронирована за вами на 24 часа.</i>"
    )

    await callback.message.edit_text(
        text=text,
        reply_markup=keyboards.get_booking_keyboard(category)
    )

    scheduler.add_job(
        send_followup_message,
        trigger="date",
        run_date=datetime.now() + timedelta(hours=2),
        args=[user_id],
        id=f"followup_{user_id}",
        replace_existing=True
    )

@dp.callback_query(F.data.startswith("buy_"))
async def process_buy(callback: CallbackQuery):
    user_id = callback.from_user.id
    if scheduler.get_job(f"followup_{user_id}"):
        scheduler.remove_job(f"followup_{user_id}")

    await callback.message.answer(
        "🎉 <b>Менеджер свяжется с вами в течение 5 минут для подтверждения брони!</b>"
    )
    await callback.answer()

async def main():
    # Запуск легкого веб-сервера для закрытия порта на Render
    app = web.Application()
    app.router.add_get('/', handle_health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    scheduler.start()
    logging.info("Бот успешно запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
