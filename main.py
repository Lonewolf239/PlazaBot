import uvicorn
import logging
import asyncio

from aiocryptopay import Networks
from fastapi import FastAPI
from contextlib import asynccontextmanager
import config
from bot_app.database import DatabaseInterface
from bot_app import BotInterface
from bot_app.payments import CryptoPay
from bot_app.payments import config as payment_config
from aiohttp import web
from aiocryptopay.models.update import Update
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
crypto_pay: CryptoPay
dp: Dispatcher
bot_task = None
clone_tasks = []
web_app: web.Application
web_app_runner: web.AppRunner


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


def register_crypto_handlers(crypto_instance: CryptoPay):
    global web_app, web_app_runner

    web_app = web.Application()

    @crypto_instance.crypto.pay_handler()
    async def invoice_paid(update: Update, app) -> None:
        await crypto_pay.invoice_paid(update)

    async def close_session() -> None:
        await crypto_instance.crypto.close()

    web_app.add_routes([
        web.post(f'/crypto/{payment_config.CRYPTOPAY_WEBHOOK}', crypto_instance.crypto.get_updates)
    ])
    web_app.on_shutdown.append(close_session)


async def start_webhook_server():
    global web_app_runner
    if web_app:
        web_app_runner = web.AppRunner(web_app)
        await web_app_runner.setup()
        site = web.TCPSite(web_app_runner, 'localhost', 3001)
        await site.start()
        logger.info("Webhook server started on http://localhost:3001")


async def stop_webhook_server():
    global web_app_runner
    if web_app_runner:
        await web_app_runner.cleanup()
        logger.info("Webhook server stopped")


@asynccontextmanager
async def lifespan(app: FastAPI):
    global db, bot, crypto_pay, dp, bot_task, clone_tasks
    db = DatabaseInterface(logger)
    await db.create()
    await db.create_config([(0, "honest"), (1, "honest"), (2, "honest"), (3, "honest"), (4, "honest"), (5, "honest"),])
    bot = BotInterface(db, config.TOKEN, config.ADMIN_IDS, logger)
    if payment_config.TEST:
        crypto_pay = CryptoPay(payment_config.CRYPTOPAY_TEST_API_TOKEN, bot, db, Networks.TEST_NET)
    else:
        crypto_pay = CryptoPay(payment_config.CRYPTOPAY_API_TOKEN, bot, db)
    await crypto_pay.initialize()
    register_crypto_handlers(crypto_pay)
    await start_webhook_server()
    bot.initialize(crypto_pay)
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
        clone_bot_interface = BotInterface(db, clone_token, config.ADMIN_IDS, logger)
        clone_bot_interface.initialize(crypto_pay)
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
    await stop_webhook_server()
    logger.info("Приложение завершено")


app = FastAPI(lifespan=lifespan)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
