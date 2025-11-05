from aiogram import Bot, types
from typing import Optional, Union, Dict, Any
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardRemove
from bot_app.keyboards.keyboards_manager import KeyboardManager
from bot_app.games import CasinoSlot
from bot_app.database.db_manager import DatabaseInterface
from bot_app.payments import PaymentGateway
from bot_app.utils.messages import Messages
from bot_app.utils.smtp import Email, Language

CasinoGames = [CasinoSlot(),]
PAGE_LIMIT = 16

class BotInterface:
    def __init__(self, db_interface: DatabaseInterface, token: str, admins_id: list):
        self.database_interface = db_interface
        self.bot = Bot(token)
        self.payment_gateway: Optional[PaymentGateway] = None
        self.admins_id = admins_id

    def initialize(self, payment_gateway: PaymentGateway):
        self.payment_gateway = payment_gateway

    def get_bot(self):
        return self.bot

    async def get_game(self, chat_id: int):
        return await self.database_interface.get_selected_game(chat_id)

    async def get_text(self, chat_id: int, tag: str, user_data: Dict[str, Any] = None) -> str:
        if user_data is None:
            user_data = await self.database_interface.get_user(chat_id)
        language = user_data["language"]
        text_template = Messages.TEXT[tag].get(language, tag)
        text_template = text_template.replace("{selected_game}",
                                              f"{CasinoGames[user_data["selected_game"]].icon} "
                                              f"{CasinoGames[user_data["selected_game"]].name[user_data["language"]]}")
        return text_template.format(**user_data)

    @staticmethod
    def get_user_language(message: types.Message) -> str:
        user_lang = message.from_user.language_code
        if user_lang is None:
            return "en"
        if user_lang.startswith("ru"):
            return "ru"
        else:
            return "en"

    async def main_menu(self, chat_id: int):
        selected_game = await self.get_game(chat_id)
        await self.send_message(
            chat_id,
            await self.get_text(chat_id, "MAIN_MENU"),
            parse_mode="HTML",
            reply_markup=KeyboardManager.get_main_keyboard(CasinoGames[selected_game].icon,
                                                           chat_id in self.admins_id,
                                                           await self.database_interface.get_language(chat_id))
        )

    async def registration_menu(self, message: types.Message, registration_type = 0, first_message = "REGISTRATION",
                                ignore_db = False):
        chat_id = message.chat.id
        user_data = await self.database_interface.get_user(chat_id)
        if not user_data:
            await self.database_interface.create_user(chat_id, message.from_user.first_name,
                                                      self.get_user_language(message))
            user_data = await self.database_interface.get_user(chat_id)
        if not ignore_db:
            if bool(user_data.get("email_verified", False)):
                return
        if registration_type == 0:
            await self.database_interface.update_user(chat_id, email_verified=False, block_input=True, input_type=1)
            await self.send_message(chat_id, await self.get_text(chat_id, first_message),
                                    reply_markup=KeyboardManager.get_register_cancel_keyboard(user_data.get("language", "en")))
        elif registration_type == 1:
            input_text = message.text.strip()
            if not Email.is_valid_email(input_text):
                await self.send_message(chat_id, await self.get_text(chat_id, "REGISTRATION_ERROR_EMAIL"))
                return
            email_code = Email.get_email_code()
            await self.database_interface.update_user(chat_id,
                                                      email=input_text,
                                                      email_code=email_code,
                                                      input_type=2)
            await self.send_message(chat_id, await self.get_text(chat_id, "REGISTRATION_STEP_TWO"),
                                    reply_markup=KeyboardManager.get_register_back_keyboard(user_data.get("language", "en")))
            Email.send_email(input_text, email_code, Language.RUSSIAN if
            user_data.get("language", "en") == "ru" else Language.ENGLISH)
        else:
            email_code = message.text.strip()
            if await self.database_interface.verify_email(chat_id, email_code):
                await self.database_interface.update_user(chat_id, block_input=False, input_type=0)
                await self.send_message(chat_id, await self.get_text(chat_id, "REGISTRATION_COMPLETED"))
                await self.main_menu(chat_id)
                return
            await self.send_message(chat_id, await self.get_text(chat_id, "REGISTRATION_ERROR_CODE"))

    async def on_command(self, message: types.Message):
        command = message.text[1:]
        chat_id = message.chat.id
        await self.registration_menu(message)

        block_input = await self.database_interface.get_block_input(chat_id)
        if block_input:
            return

        if command == "start":
            await self.main_menu(chat_id)
        elif command == "help":
            await self.send_message(
                chat_id,
                "Список доступных команд:\n/start - начать\n/help - помощь\n/other_command - другая команда"
            )
        elif command == "other_command":
            await self.send_message(
                chat_id,
                "Вы вызвали другую команду."
            )
        else:
            await self.send_message(
                chat_id,
                f"Неизвестная команда: /{command}. Введите /help для списка команд."
            )

    async def on_text(self, message: types.Message):
        chat_id = message.chat.id
        input_type = await self.database_interface.get_input_type(chat_id)
        input_text = message.text.strip()

        await self.bot.delete_message(chat_id, message.message_id)
        if input_type == 0:
            return

        # Register
        elif input_type == 1:
            await self.registration_menu(message, 1)
        elif input_type == 2:
            await self.registration_menu(message, 2)

    async def on_inline_button(self, callback_query: types.CallbackQuery):
        command = callback_query.data

        if not command:
            return

        chat_id = callback_query.message.chat.id
        await self.bot.delete_message(chat_id, callback_query.message.message_id)

        if command == "delete":
            return

        user_data = await self.database_interface.get_user(chat_id)
        block_input = user_data.get("block_input", False)

        if command == "register_cancel":
            await self.database_interface.update_user(chat_id,
                                                      input_type=0,
                                                      email_verified=True,
                                                      block_input=False)
            await self.main_menu(chat_id)

        if block_input:
            return
        if command == "back":
            await self.main_menu(chat_id)

        # ════════════════ Регистрация ════════════════
        elif command == "register_back":
            await self.registration_menu(callback_query.message)

        # ═════════════════ Настройки ═════════════════
        elif command == "settings":
            text = str(await self.get_text(chat_id, "SETTINGS"))
            text = text.replace("semga05@mail.ru", "None")
            await self.send_message(chat_id, text,
                                    reply_markup=KeyboardManager.get_settings_keyboard(user_data.get("language", "en")))
        elif command == "change-game":
            pass
        elif command == "change-language":
            await self.send_message(chat_id, await self.get_text(chat_id, "CHANGE_LANGUAGE"),
                                    reply_markup=KeyboardManager.get_language_keyboard())
        elif command == "change-email":
            await self.registration_menu(callback_query.message, first_message="CHANGE_EMAIL", ignore_db=True)
        elif command.startswith("language"):
            language_code = command[len("language:"):]
            await self.database_interface.update_user(chat_id, language=language_code)
            await self.main_menu(chat_id)

        # ═══════════════════ Баланс ══════════════════
        elif command == "balance":
            await self.send_message(chat_id, await self.get_text(chat_id, "BALANCE"),
                                    reply_markup=KeyboardManager.get_balance_keyboard(user_data.get("language", "en")))
        elif command == "balance-deposit":
            providers = self.payment_gateway.get_providers("deposit")
            text = "\n".join([p.get_provider_name() for p in providers])
            await self.send_message(chat_id, text)
            deposit = await self.payment_gateway.initiate_deposit(chat_id, 100, providers[0].get_provider_name(), "RUB")
            await self.send_message(chat_id, deposit.get("payment_url"))
        elif command == "balance-withdraw":
            providers = self.payment_gateway.get_providers("withdraw")


        # ════════════════ Пользователь ═══════════════
        elif command.startswith("user"):
            username = command[len("user:"):]
            user = await self.database_interface.get_user_by_username(username)
            await self.send_userinfo(chat_id, user)
            await self.main_menu(chat_id)

        # ════════════════ Админ-панель ═══════════════
        elif command == "admin-panel":
            if chat_id not in self.admins_id:
                return
            await self.send_message(chat_id, await self.get_text(chat_id, "ADMIN_PANEL"),
                                    reply_markup=KeyboardManager.get_admin_keyboard(user_data.get("language", "en")))
        elif command == "admin-summary":
            needed, count, avg_bal, max_bal, min_bal = await self.database_interface.get_needed()
            text = (
                f"👥 {await self.get_text(chat_id, "ADMIN_SUMMARY_COUNT")}: {count}\n"
                f"💰 {await self.get_text(chat_id, "ADMIN_SUMMARY_NEEDED")}: {int(needed)} руб\n"
                f"📈 {await self.get_text(chat_id, "ADMIN_SUMMARY_AVG_BALANCE")}: {int(avg_bal)} руб\n"
                f"🔼 {await self.get_text(chat_id, "ADMIN_SUMMARY_MAX_BALANCE")}: {max_bal}\n"
                f"🔽 {await self.get_text(chat_id, "ADMIN_SUMMARY_MIN_BALANCE")}: {min_bal}"
            )
            await self.send_message(chat_id, text,
                                    reply_markup=KeyboardManager.get_admin_keyboard(user_data.get("language", "en")))
        elif command.startswith("admin-list-players"):
            page = int(command.split(':')[1]) if ':' in command else 1
            text, lines, add_next_page = await self.get_users_page(page)
            await self.send_message(chat_id, text,
                                    reply_markup=KeyboardManager.get_users_keyboard(
                                        user_data.get("language", "en"), lines, page, add_next_page))
            pass
        elif command.startswith("admin-show-logs"):
            page = int(command.split(':')[1]) if ':' in command else 1
            text, add_next_page = await self.get_logs_page(page)
            await self.send_message(chat_id, text,
                                    reply_markup=KeyboardManager.get_logs_keyboard(
                                        user_data.get("language", "en"), page, add_next_page))
        elif command.startswith("admin-user"):
            username = command[len("admin-user:"):]
            await self.send_userinfo(chat_id, await self.database_interface.get_user_by_username(username), True)
            await self.main_menu(chat_id)

        # ═══════════════════ Прочее ══════════════════
        elif command == "rules":
            await self.send_message(chat_id,
                                    CasinoGames[user_data.get("selected_game", 0)].rules(user_data.get("language", "en")),
                                    reply_markup=KeyboardManager.get_back_keyboard(user_data.get("language", "en")))
        else:
            await self.send_message(chat_id, command)

    @staticmethod
    def get_page(rows, page: int):
        total_rows = len(rows)
        last_page = (total_rows + PAGE_LIMIT - 1) // PAGE_LIMIT
        add_next_page = (page < last_page)
        start = (page - 1) * PAGE_LIMIT
        end = start + PAGE_LIMIT
        page_rows = rows[start:end]
        return last_page, page_rows, add_next_page

    async def get_users_page(self, page: int):
        rows = await self.database_interface.get_users()
        last_page, page_rows, add_next_page = self.get_page(rows, page)
        lines = [r['username'] for r in page_rows]
        text = f"Пользователи [{page}/{last_page}]:\n\n"
        return text, lines, add_next_page

    async def get_logs_page(self, page: int):
        rows = await self.database_interface.get_logs()
        last_page, page_rows, add_next_page = self.get_page(rows, page)
        lines = [f"[{r['timestamp']}] {r['type']} — {r['message']}" for r in page_rows]
        text = f"Логи [{page}/{last_page}]:\n\n" + "\n\n".join(lines)
        return text, add_next_page

    async def send_userinfo(self, chat_id: int, user_data: Dict[str, Any], for_admin: bool = False):
        await self.send_message(chat_id, await self.get_text(chat_id, "USERINFO_ADMIN" if for_admin else "USERINFO", user_data),
                                reply_markup=KeyboardManager.get_delete_keyboard())

    async def send_message(self, chat_id: int, text: str, parse_mode: str = None,
                           reply_markup: Optional[Union[InlineKeyboardMarkup, ReplyKeyboardRemove]] = None,
                           disable_web_page_preview: Optional[bool] = None):
        """
        Отправляет текстовое сообщение с опциональными параметрами parse_mode,
        клавиатурой и отключением предпросмотра ссылок.
        """
        return await self.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
            disable_web_page_preview=disable_web_page_preview
        )
