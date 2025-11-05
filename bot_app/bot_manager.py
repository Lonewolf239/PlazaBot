from aiogram import Bot, types
from typing import Optional, Union, Dict, Any
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardRemove
from bot_app.keyboards import KeyboardManager
from bot_app.games import CasinoSlot
from bot_app.database import DatabaseInterface
from bot_app.payments import PaymentGateway
from bot_app.utils import Messages
from bot_app.utils import Email, Language
from bot_app.handlers import HandlersManager

PAGE_LIMIT = 16


class BotInterface:
    CasinoGames = [CasinoSlot(), ]

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
                                              f"{self.CasinoGames[user_data["selected_game"]].icon} "
                                              f"{self.CasinoGames[user_data["selected_game"]].name[user_data["language"]]}")
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
            reply_markup=KeyboardManager.get_main_keyboard(self.CasinoGames[selected_game].icon,
                                                           chat_id in self.admins_id,
                                                           await self.database_interface.get_language(chat_id))
        )

    async def registration_menu(self, message: types.Message, registration_type=0, first_message="REGISTRATION",
                                ignore_db=False):
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
                                    reply_markup=KeyboardManager.get_register_cancel_keyboard(
                                        user_data.get("language", "en")))
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
                                    reply_markup=KeyboardManager.get_register_back_keyboard(
                                        user_data.get("language", "en")))
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
            await HandlersManager.register_cancel(self, chat_id)

        if block_input:
            return

        if command == "back":
            await self.main_menu(chat_id)

        # ════════════════ Регистрация ════════════════
        elif command == "register_back":
            await HandlerManager.register_back(self, callback_query)

        # ═════════════════ Настройки ═════════════════
        elif command == "settings":
            await HandlersManager.settings(self, chat_id, user_data)
        elif command == "change-game":
            pass
        elif command == "change-language":
            await HandlersManager.change_language(self, chat_id)
        elif command == "change-email":
            await HandlersManager.change_email(self, callback_query)
        elif command.startswith("language"):
            await HandlersManager.language(self, chat_id, command)

        # ═══════════════════ Баланс ══════════════════
        elif command == "balance":
            await HandlersManager.balance(self, chat_id, user_data)
        elif command == "balance-deposit":
            await HandlersManager.balance_deposit(self, chat_id)
        elif command == "balance-withdraw":
            await HandlersManager.balance_withdraw(self, chat_id)

        # ════════════════ Пользователь ═══════════════
        elif command.startswith("user"):
            await HandlersManager.user(self, chat_id, command)

        # ════════════════ Админ-панель ═══════════════
        elif command == "admin-panel":
            await HandlersManager.admin_panel(self, chat_id, user_data)
        elif command == "admin-summary":
            await HandlersManager.admin_summary(self, chat_id, user_data)
        elif command.startswith("admin-list-players"):
            await HandlersManager.admin_list_players(self, chat_id, command, user_data)
        elif command.startswith("admin-show-logs"):
            await HandlersManager.admin_show_logs(self, chat_id, command, user_data)
        elif command.startswith("admin-user"):
            await HandlersManager.admin_user(self, chat_id, command)

        # ═══════════════════ Прочее ══════════════════
        elif command == "rules":
            await HandlersManager.rules(self, chat_id, user_data)
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
        await self.send_message(chat_id,
                                await self.get_text(chat_id, "USERINFO_ADMIN" if for_admin else "USERINFO", user_data),
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
