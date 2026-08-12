import os
import asyncio
import logging
from aiohttp import web

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode

import config
import keyboards

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()


# --- Хэндлеры бота ---

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
    await callback.answer()
    
    # Отправляем анимированный игровой автомат
    msg = await callback.message.answer_dice(emoji="🎰")
    
    # Задержка 2.5 секунды для просмотра анимации вращения
    await asyncio.sleep(2.5)
    
    val = msg.dice.value
    
    # Распределение беспроигрышных призов по значениям комбинации
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


@dp.callback_query(F.data.startswith("buy_"))
async def buy_handler(callback: types.CallbackQuery):
    await callback.answer("Заявка принята!", show_alert=True)
    await callback.message.answer(
        "🎉 **Менеджер свяжется с вами в течение 5 минут для подтверждения брони!**"
    )


# --- Веб-сервер для поддержки активности (UptimeRobot / Render Ping) ---

async def handle_ping(request):
    return web.Response(text="OK", status=200)


async def main():
    # Запуск поллинга бота в фоновом режиме
    asyncio.create_task(dp.start_polling(bot))
    
    # Запуск веб-сервера aiohttp для ответа на пинг от UptimeRobot
    app = web.Application()
    app.router.add_get("/", handle_ping)
    
    port = int(os.getenv("PORT", 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    
    # Удержание процесса в активном состоянии
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
