import uvicorn
import logging
import asyncio
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
import config
from bot_app.database.db_manager import DatabaseInterface
from bot_app.bot_manager import BotInterface
from bot_app.payments.payment_gateway import PaymentGateway
from aiogram import Dispatcher, types, F
from aiogram.filters import Command

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


def register_bot_handlers(dp: Dispatcher, bot_instance: BotInterface):
    # Обработчик команд
    @dp.message(Command("start"))
    async def handle_commands(message: types.Message):
        await bot_instance.on_command(message)

    # Обработчик текста
    @dp.message(F.text)
    async def handle_text(message: types.Message):
        await bot_instance.on_text(message)

    # Обработчик callback кнопок
    @dp.callback_query()
    async def handle_inline_button(callback_query: types.CallbackQuery):
        await bot_instance.on_inline_button(callback_query)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global db, bot, payment_gateway, dp, bot_task
    db = DatabaseInterface(logger)
    await db.create()
    bot = BotInterface(db, config.TOKEN, config.ADMINS_ID)
    payment_gateway = PaymentGateway(db, bot.get_bot(), logger)
    await payment_gateway.initialize()
    bot.initialize(payment_gateway)
    dp = Dispatcher()
    register_bot_handlers(dp, bot)
    bot_task = asyncio.create_task(dp.start_polling(bot.get_bot()))
    yield
    bot_task.cancel()
    try:
        await bot_task
    except asyncio.CancelledError:
        pass

app = FastAPI(lifespan=lifespan)

@app.post("https://njui7w-195-128-153-209.ru.tuna.am/payment/yookassa/webhook")
async def yookassa_webhook(request: Request):
    body = await request.body()
    headers = dict(request.headers)
    result = await payment_gateway.handle_yookassa_webhook(
        request_body=body.decode('utf-8'),
        request_headers=headers
    )
    return result

@app.post("https://njui7w-195-128-153-209.ru.tuna.am/payment/cryptomus/webhook")
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
