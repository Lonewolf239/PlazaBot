import uvicorn
import logging
import asyncio
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
import config
from bot_app.database import DatabaseInterface
from bot_app import BotInterface
from bot_app.payments import PaymentGateway
from aiogram import Dispatcher, types, F
from aiogram.filters import CommandStart
from bot_app.referral import ReferralManager

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

db: DatabaseInterface
bot: BotInterface
payment_gateway: PaymentGateway
dp: Dispatcher
bot_task = None
clone_tasks = []


def register_bot_handlers(dp: Dispatcher, bot_instance: BotInterface):
    @dp.message(CommandStart())
    async def handle_commands(message: types.Message):
        await bot_instance.on_start_command(message)

    @dp.message(F.text)
    async def handle_text(message: types.Message):
        await bot_instance.on_text(message)

    @dp.callback_query()
    async def handle_inline_button(callback_query: types.CallbackQuery):
        await bot_instance.on_inline_button(callback_query)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global db, bot, payment_gateway, dp, bot_task, clone_tasks
    db = DatabaseInterface(logger)
    await db.create()
    bot = BotInterface(db, config.TOKEN, config.ADMINS_ID, logger)
    payment_gateway = PaymentGateway(db, bot.get_bot(), logger)
    await payment_gateway.initialize()
    bot.initialize(payment_gateway)
    await bot.referral_manager.load_active_bots()
    dp = Dispatcher()
    register_bot_handlers(dp, bot)
    bot_task = asyncio.create_task(dp.start_polling(bot.get_bot()))
    clone_tasks = []
    for bot_id, clone_bot in bot.referral_manager.active_bots.items():
        clone_token = await bot.referral_manager.get_bot_token(bot_id)
        if not clone_token:
            logger.warning(f"Не найден токен для клон-бота {bot_id}")
            continue
        clone_bot_interface = BotInterface(db, clone_token, config.ADMINS_ID, logger)
        clone_bot_interface.initialize(payment_gateway)
        await ReferralManager.copy_bot_commands(logger, bot.bot, clone_bot_interface.bot)
        clone_dp = Dispatcher()
        register_bot_handlers(clone_dp, clone_bot_interface)
        task = asyncio.create_task(clone_dp.start_polling(clone_bot))
        clone_tasks.append(task)
        logger.info(f"Запущен клон-бот {bot_id}")
    yield
    if bot_task:
        bot_task.cancel()
        try:
            await bot_task
        except asyncio.CancelledError:
            pass
    for task in clone_tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    if bot and bot.referral_manager:
        try:
            await bot.referral_manager.cleanup()
        except Exception as e:
            logger.error(f"Ошибка при cleanup ReferralManager: {e}")
    if bot:
        try:
            await bot.get_bot().session.close()
        except Exception as e:
            logger.error(f"Ошибка при закрытии сессии основного бота: {e}")

    logger.info("Приложение завершено")


app = FastAPI(lifespan=lifespan)


# TODO: Сделать рабочие вебхуки

@app.post("/payment/yookassa/webhook")
async def yookassa_webhook(request: Request):
    body = await request.body()
    headers = dict(request.headers)
    result = await payment_gateway.handle_yookassa_webhook(
        request_body=body.decode('utf-8'),
        request_headers=headers
    )
    return result


@app.post("/payment/cryptomus/webhook")
async def cryptomus_webhook(request: Request):
    body = await request.body()
    headers = dict(request.headers)
    result = await payment_gateway.handle_cryptomus_webhook(
        request_body=body.decode('utf-8'),
        request_headers=headers
    )
    return result


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
