import logging
from aiogram import Bot, types
from typing import Optional, Union, Dict, Any
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardRemove
from bot_app.keyboards import KeyboardManager
from bot_app.games import CasinoSlot
from bot_app.database import DatabaseInterface
from bot_app.payments import PaymentGateway
from bot_app.referral import ReferralManager
from bot_app.handlers import ReferralHandler
from bot_app.utils import Messages
from bot_app.utils import Email, Language
from bot_app.handlers import HandlersManager

PAGE_LIMIT = 16


class BotInterface:
    CasinoGames = [CasinoSlot(),]

    def __init__(self, db_interface: DatabaseInterface, token: str, admins_id: list, logger: logging.Logger):
        self.database_interface = db_interface
        self.token = token
        self.bot = Bot(token)
        self.payment_gateway: Optional[PaymentGateway] = None
        self.admins_id = admins_id
        self.referral_manager: Optional[ReferralManager] = None
        self.logger = logger

    def initialize(self, payment_gateway: PaymentGateway):
        self.payment_gateway = payment_gateway
        self.referral_manager = ReferralManager(
            self.database_interface,
            self.token,
            self.logger
        )

    def get_bot(self):
        return self.bot

    async def get_game(self, chat_id: int):
        return await self.database_interface.get_selected_game(chat_id)

    async def get_text(self, chat_id: int, tag: str, user_data: Dict[str, Any] = None,
                       custom_data: Dict[str, Any] = None) -> str:
        if user_data is None:
            user_data = await self.database_interface.get_user(chat_id)
        language = user_data["language"]
        text_template = Messages.TEXT[tag].get(language, tag)
        text_template = text_template.replace("{selected_game}",
                                              f"{self.CasinoGames[user_data["selected_game"]].icon} "
                                              f"{self.CasinoGames[user_data["selected_game"]].
                                              name(user_data["language"])}")
        if custom_data:
            return text_template.format(**custom_data)
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
            await self.database_interface.update_user(chat_id, in_registration=True,
                                                      email_verified=False, block_input=True, input_type=1)
            await self.send_message(chat_id, await self.get_text(chat_id, first_message),
                                    reply_markup=KeyboardManager.get_register_cancel_keyboard(
                                        user_data.get("language", "en")))
        elif registration_type == 1:
            input_text = message.text.strip()
            if not Email.validate_email_address(input_text):
                await self.send_message(chat_id, await self.get_text(chat_id, "REGISTRATION_ERROR_EMAIL"))
                return
            email_code = Email.generate_verification_code()
            await self.database_interface.update_user(chat_id,
                                                      in_registration=False,
                                                      email=input_text,
                                                      email_code=email_code,
                                                      input_type=2)
            await self.send_message(chat_id, await self.get_text(chat_id, "REGISTRATION_STEP_TWO"),
                                    reply_markup=KeyboardManager.get_back_keyboard(
                                        user_data.get("language", "en"),
                                        callback_data="register_back"))
            Email.send_verification_email(input_text, email_code, Language.RUSSIAN if
            user_data.get("language", "en") == "ru" else Language.ENGLISH)
        else:
            email_code = message.text.strip()
            if await self.database_interface.verify_email(chat_id, email_code):
                await self.database_interface.update_user(chat_id, in_registration=False,
                                                          block_input=False, input_type=0)
                await self.send_message(chat_id, await self.get_text(chat_id, "REGISTRATION_COMPLETED"))
                await self.main_menu(chat_id)
                return
            await self.send_message(chat_id, await self.get_text(chat_id, "REGISTRATION_ERROR_CODE"))

    async def _process_referral_reward(self, user_id: int, amount: float,
                                       action_type: str, bot_username: str = None):
        """
        НОВОЕ: Обрабатывает реферальные начисления
        """
        if not bot_username:
            bot_info = await self.bot.get_me()
            bot_username = bot_info.username
        await self.referral_manager.process_user_action(
            user_id=user_id,
            bot_id=bot_username,
            action_type=action_type,
            amount=abs(amount)
        )

    async def on_start_command(self, message: types.Message):
        command = message.text[1:]
        chat_id = message.chat.id
        bot_info = await self.bot.get_me()
        current_bot_id = bot_info.username
        is_clone = await self.database_interface.is_clone_bot(current_bot_id)
        if is_clone:
            referrer_id = await self.database_interface.get_clone_bot_creator(current_bot_id)
            if referrer_id and referrer_id != chat_id:
                existing = await self.database_interface.fetch_one(
                    """SELECT * FROM referrals
                    WHERE referred_user_id = ? AND referrer_user_id = ?""",
                    (chat_id, referrer_id)
                )
                if not existing:
                    await self.database_interface.execute(
                        """INSERT INTO referrals
                        (referrer_user_id, referred_user_id, referred_bot_id)
                        VALUES (?, ?, ?)""",
                        (referrer_id, chat_id, current_bot_id)
                    )
                    self.logger.info(f"✅ Создана реферальная связь: {referrer_id} -> "
                                     f"{chat_id} (бот: {current_bot_id})")
        await self.registration_menu(message)
        block_input = await self.database_interface.get_block_input(chat_id)
        if block_input:
            return
        parts = command.split(maxsplit=1)
        if len(parts) > 1:
            start_param = parts[1]
            if start_param.startswith("user_"):
                start_param = parts[1][5:] if parts[1].startswith("user_") else parts[1]
                user_data = await self.database_interface.get_user_by_hashed_username(start_param)
                if user_data:
                    await self.send_userinfo(chat_id, user_data, chat_id in self.admins_id)

        await self.main_menu(chat_id)

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

        elif input_type == 10:
            from bot_app.handlers.referral_handler import ReferralHandler
            await ReferralHandler.process_token_input(self, chat_id, input_text)

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
            if not user_data.get("in_registration", False):
                return
            await HandlersManager.register_cancel(self, chat_id)
            return

        if command == "referral-cancel":
            await ReferralHandler.referral_cancel(self, chat_id)
            return

        if block_input:
            return

        if command == "back":
            await self.main_menu(chat_id)

        # ════════════════ Регистрация ════════════════
        elif command == "register_back":
            if not user_data.get("in_registration", False):
                return
            await HandlersManager.register_back(self, callback_query)

        elif command == "games-start":
            await HandlersManager.games_start(self, chat_id)

        # ═════════════════ Настройки ═════════════════
        elif command == "settings":
            await HandlersManager.settings(self, chat_id, user_data)
        elif command == "change-game":
            await HandlersManager.change_game(self, chat_id, user_data)
        elif command.startswith("set-game"):
            await HandlersManager.set_game(self, chat_id, command)
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
        elif command == "profile":
            await HandlersManager.user(self, chat_id, f"user:{chat_id}")
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
            await HandlersManager.admin_user(self, chat_id, command, user_data)
        elif command == "admin-show-tables":
            await HandlersManager.admin_show_tables(self, chat_id, user_data.get("language", "en"))
        elif command.startswith("admin-tables"):
            table = command.split(':')[1]
            await HandlersManager.admin_show_table(self, chat_id, table, user_data)

        # ═════════════════ Рефералка ═════════════════
        elif command == "referral-menu":
            await ReferralHandler.referral_menu(self, chat_id, user_data)
        elif command == "referral-create":
            await ReferralHandler.create_clone_bot(self, chat_id, user_data)
        elif command == "referral-stats":
            await ReferralHandler.my_referrals(self, chat_id, user_data.get("language", "en"))

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

    async def format_games_statistics(self, chat_id: int, user_data: Dict[str, Any], for_admin: bool) -> str:
        """
        Возвращает форматированный текст со статистикой игр пользователя:
        - Любимая игра
        - Всего игр и количество сыгранных раз по каждой
        """
        games_dict = await self.database_interface.get_games_played(chat_id)
        if not games_dict:
            return await self.get_text(chat_id, "USERINFO_NO_GAMES", user_data)
        favorite_game_id = max(games_dict, key=games_dict.get)
        favorite_game_name = (f"{self.CasinoGames[favorite_game_id].icon} "
                              f"{self.CasinoGames[favorite_game_id].name(user_data["language"])}")
        favorite_play_times = games_dict[favorite_game_id]
        games_list = []
        for game_id, count in games_dict.items():
            game_name = (f"{self.CasinoGames[game_id].icon} "
                         f"{self.CasinoGames[game_id].name(user_data["language"])}")
            game_text = await self.get_text(chat_id, "USERINFO_GAMES_LIST", user_data)
            game_text = game_text.replace("game_name", game_name).replace("count", str(count))
            games_list.append(game_text)
        response_text = await self.get_text(chat_id, "USERINFO_FOFAVORITE_GAME", user_data)
        response_text = (response_text.replace("favorite_game_name", favorite_game_name).
                         replace("favorite_play_times", str(favorite_play_times)))
        if for_admin:
            response_text += (f"\n{await self.get_text(chat_id, "USERINFO_GAMES_LIST_TITLE", user_data)}:\n"
                              + "\n".join(games_list))

        return response_text

    async def send_userinfo(self, chat_id: int, user_data: Dict[str, Any] = None,
                            for_admin: bool = False, profile: bool = False):
        if user_data is None:
            user_data = await self.database_interface.get_user(chat_id)
        tag = "USERINFO"
        if profile:
            tag = "PROFILE"
        elif for_admin:
            tag = "USERINFO_ADMIN"
        userinfo = await self.get_text(chat_id, tag, user_data)
        userinfo = userinfo.replace("username",
                                    f"<a href='https://t.me/{(await self.bot.get_me()).username}?start=user_{user_data['hashed_username']}'>"
                                    f"{user_data['username']}</a>")
        userinfo += "\n" + await self.format_games_statistics(chat_id, user_data, for_admin)
        await self.send_message(chat_id, userinfo, reply_markup=KeyboardManager.get_delete_keyboard())

    async def send_message(self, chat_id: int, text: str, parse_mode: str = "HTML",
                           reply_markup: Optional[Union[InlineKeyboardMarkup, ReplyKeyboardRemove]] = None,
                           disable_web_page_preview: Optional[bool] = True):
        """
        Отправляет текстовое сообщение с опциональными параметрами parse_mode,
        клавиатурой и отключением предпросмотра ссылок.
        """
        if reply_markup is None:
            reply_markup = KeyboardManager.get_delete_keyboard()
        return await self.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
            disable_web_page_preview=disable_web_page_preview
        )
