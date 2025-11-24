import asyncio
import logging
import random
import math
from io import BytesIO
from aiogram import Bot, types
from typing import Optional, Union, Dict, Any
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardRemove, InputMediaPhoto, BufferedInputFile
import config
from .keyboards import KeyboardManager
from .games import CasinoSlot, Roulette, Lottery, BetDataFlow, BetParameter, Coin, Dice, HiLo, Mines, Blackjack, \
    CasinoSlotV2
from .database import DatabaseInterface
from .payments import CryptoPay
from .referral import ReferralManager
from .handlers import ReferralHandler, GameManager
from .utils import Messages
# from .utils import Email, Language
from .handlers import HandlersManager, InteractiveGameHandlers

PAGE_LIMIT = 16


class BetDataCollector:
    """Управляет процессом сбора bet_data от пользователя"""

    def __init__(self):
        self._user_states: Dict[int, Dict[str, Any]] = {}

    def start_collection(self, chat_id: int, bet_data_flow: BetDataFlow):
        """Начать сбор данных"""
        self._user_states[chat_id] = {
            'parameters': bet_data_flow.parameters,
            'current_step': 0,
            'collected_data': {},
            'multi_select_data': {},
            "message_id": None
        }

    def add_value(self, chat_id: int, param_type: str, value: str) -> bool:
        """Добавить или переключить значение параметра"""
        if chat_id not in self._user_states:
            return False
        state = self._user_states[chat_id]
        param = next((p for p in state['parameters'] if p.param_type == param_type), None)
        if not param:
            return False
        if param.multi_select:
            if param_type not in state['multi_select_data']:
                state['multi_select_data'][param_type] = []
            selected = state['multi_select_data'][param_type]
            if value in selected:
                selected.remove(value)
            else:
                if len(selected) < param.multi_select_max:
                    selected.append(value)
                else:
                    return False
            return True
        else:
            state['collected_data'][param_type] = value
            state['current_step'] += 1
            return True

    def is_multi_select_complete(self, chat_id: int, param_type: str) -> bool:
        """Проверить, что выбрано хотя бы одно значение в multi-select параметре"""
        if chat_id not in self._user_states:
            return False
        state = self._user_states[chat_id]
        return len(state['multi_select_data'].get(param_type, [])) > 0

    def finalize_multi_select(self, chat_id: int, param_type: str) -> bool:
        """Завершить multi-select параметр и перейти к следующему"""
        if chat_id not in self._user_states:
            return False
        state = self._user_states[chat_id]
        param = next((p for p in state['parameters'] if p.param_type == param_type), None)
        if not param or not param.multi_select:
            return False
        selected = state['multi_select_data'].get(param_type, [])
        if not selected:
            return False
        state['collected_data'][param_type] = ','.join(selected)
        state['current_step'] += 1
        if param_type in state['multi_select_data']:
            del state['multi_select_data'][param_type]
        return True

    def get_multi_select_values(self, chat_id: int, param_type: str) -> list:
        """Получить текущие выбранные значения для multi-select параметра"""
        if chat_id not in self._user_states:
            return []
        state = self._user_states[chat_id]
        return state['multi_select_data'].get(param_type, [])

    def get_current_parameter(self, chat_id: int) -> Optional[BetParameter]:
        """Получить текущий параметр"""
        if chat_id not in self._user_states:
            return None
        state = self._user_states[chat_id]
        current_step = state['current_step']
        if current_step < len(state['parameters']):
            return state['parameters'][current_step]
        return None

    def is_complete(self, chat_id: int) -> bool:
        """Проверить, все ли параметры собраны"""
        if chat_id not in self._user_states:
            return False
        state = self._user_states[chat_id]
        return state['current_step'] >= len(state['parameters'])

    def get_collected_data(self, chat_id: int) -> Optional[Dict[str, str]]:
        """Получить собранные данные"""
        if chat_id not in self._user_states:
            return None
        return self._user_states[chat_id]['collected_data'].copy()

    def format_bet_data(self, chat_id: int) -> Optional[str]:
        """Форматировать собранные данные в строку"""
        data = self.get_collected_data(chat_id)
        if not data:
            return None
        return ';'.join([f"{k}:{v}" for k, v in data.items()])

    def get_progress_text(self, chat_id: int, language: str = 'en') -> str:
        """Получить текст прогресса"""
        if chat_id not in self._user_states:
            return ""
        state = self._user_states[chat_id]
        collected = state['collected_data']
        if not collected:
            return ""
        lines = []
        for param_type, value in collected.items():
            param = next((p for p in state['parameters'] if p.param_type == param_type), None)
            if param:
                param_name = param.param_name.get(language, param_type)
                lines.append(f"✅ {param_name}: {value}")
        return "\n".join(lines)

    def reset(self, chat_id: int):
        """Сбросить состояние пользователя"""
        if chat_id in self._user_states:
            del self._user_states[chat_id]

    def cancel_collection(self, chat_id: int):
        """Отменить сбор данных"""
        self.reset(chat_id)


class BotInterface:
    CasinoGames = {
        0: CasinoSlot,
        1: CasinoSlotV2,
        2: Roulette,
        3: Lottery,
        4: Coin,
        5: Dice,
        6: HiLo,
        7: Mines,
        8: Blackjack
        # 200: Crash
    }
    GameWeights = {0: 25, 1: 20, 2: 18, 8: 15, 7: 10, 5: 6, 6: 3, 4: 2, 3: 1}
    GameConfigs = {
        0: ["honest", "aggressive", "generous"],
        1: ["honest", "aggressive", "generous"],
        2: ["honest", "aggressive", "generous"],
        3: ["honest", "aggressive", "generous"],
        4: ["honest", "aggressive", "generous"],
        5: ["honest"],
        6: ["honest"],
        7: ["honest", "aggressive", "generous"],
        8: ["honest"],
        # 200: ["honest"],
    }

    def __init__(self, db_interface: DatabaseInterface, token: str, admin_ids: list, logger: logging.Logger):
        self.database_interface = db_interface
        self.token = token
        self.bot = Bot(token)
        self.crypto_pay: Optional[CryptoPay] = None
        self.admin_ids = admin_ids
        self.referral_manager: Optional[ReferralManager] = None
        self.logger = logger
        self.game_manager = GameManager(db_interface)
        self.game_manager.on_game_start(self.on_game_started)
        self.game_manager.on_game_end(self.on_game_finished)
        self.game_manager.on_game_error(self.on_game_error)
        self.bet_data_collector = BetDataCollector()

    async def initialize(self, crypto_pay: CryptoPay):
        self.crypto_pay = crypto_pay
        self.referral_manager = ReferralManager(
            self.database_interface,
            self.token,
            self.logger
        )
        await self.game_manager.register_games(self.CasinoGames)

    async def on_game_started(self, session):
        await HandlersManager.on_game_started(self, session)

    async def on_game_finished(self, result, session):
        await HandlersManager.on_game_finished(self, result, session)

    async def on_game_error(self, error, session):
        await self.database_interface.log_error(str(error) + str(session))

    def get_bot(self):
        return self.bot

    async def get_game(self, chat_id: int):
        return await self.database_interface.get_selected_game(chat_id)

    @staticmethod
    def _remove_none_blocks(text: str, data: Dict[str, Any]) -> str:
        """Удаляет блоки между ## если содержащиеся в них параметры равны None"""
        import re
        pattern = r'#([^#]*?)#'

        def replace_block(match):
            block_content = match.group(1)
            params = re.findall(r'\{(\w+)}', block_content)
            for param in params:
                if data.get(param) is None:
                    return ""
            return block_content

        return re.sub(pattern, replace_block, text)

    async def get_text(self, chat_id: int, tag: str, user_data: Dict[str, Any] = None,
                       custom_data: Dict[str, Any] = None) -> str:
        if user_data is None:
            user_data = await self.database_interface.get_user(chat_id)
        language = user_data["language"]
        text_template = Messages.TEXT[tag].get(language, tag)
        game = await self.game_manager.get_game(int(user_data.get("selected_game", 0)))
        text_template = text_template.replace("{selected_game}",
                                              f"{game.icon} {game.name(user_data.get("language", "en"))}")
        format_data = custom_data if custom_data else user_data
        text_template = self._remove_none_blocks(text_template, format_data)
        return text_template.format(**format_data)

    @staticmethod
    def get_user_language(message: types.Message) -> str:
        user_lang = message.from_user.language_code
        if user_lang is None:
            return "en"
        if user_lang.startswith("ru"):
            return "ru"
        else:
            return "en"

    async def bot_config(self):
        bot_id = (await self.bot.get_me()).id
        bot_config = await self.database_interface.get_bot_config(bot_id)
        return bot_config

    async def chat_id(self):
        return (await self.bot_config()).get("chat_id", None)

    async def get_channel_username(self, channel_id: int):
        try:
            chat = await self.bot.get_chat(channel_id)
            return chat.username
        except Exception:
            return None

    async def main_menu(self, chat_id: int, message_id: int = None):
        selected_game = await self.get_game(chat_id)
        game = await self.game_manager.get_game(selected_game)
        news_channel_username = await self.database_interface.get_news_channel_username((await self.bot.get_me()).id)
        await self.edit_message(
            chat_id,
            await self.get_text(chat_id, "MAIN_MENU"),
            message_id=message_id,
            reply_markup=KeyboardManager.get_main_keyboard(game.icon,
                                                           chat_id in self.admin_ids,
                                                           await self.database_interface.get_language(chat_id),
                                                           config.SUPPORT_BOT, news_channel_username)
        )

    async def registration_menu(self, message: types.Message,  # registration_type=0, first_message="REGISTRATION",
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
        return
        # if registration_type == 0:
        #     await self.database_interface.update_user(chat_id, in_registration=True,
        #                                               email_verified=False, block_input=True, input_type=1)
        #     await self.send_message(chat_id, await self.get_text(chat_id, first_message),
        #                             reply_markup=KeyboardManager.get_register_cancel_keyboard(
        #                                 user_data.get("language", "en")))
        # elif registration_type == 1:
        #     input_text = message.text.strip()
        #     if not Email.validate_email_address(input_text):
        #         await self.send_message(chat_id, await self.get_text(chat_id, "REGISTRATION_ERROR_EMAIL"))
        #         return
        #     email_code = Email.generate_verification_code()
        #     await self.database_interface.update_user(chat_id,
        #                                               in_registration=False,
        #                                               email=input_text,
        #                                               email_code=email_code,
        #                                               input_type=2)
        #     await self.send_message(chat_id, await self.get_text(chat_id, "REGISTRATION_STEP_TWO"),
        #                             reply_markup=KeyboardManager.get_back_keyboard(
        #                                 user_data.get("language", "en"),
        #                                 callback_data="register_back"))
        #     Email.send_verification_email(input_text, email_code, Language.RUSSIAN if user_data.get(
        #         "language", "en") == "ru" else Language.ENGLISH)
        # else:
        #     email_code = message.text.strip()
        #     if await self.database_interface.verify_email(chat_id, email_code):
        #         await self.database_interface.update_user(chat_id, in_registration=False,
        #                                                   block_input=False, input_type=0)
        #         await self.send_message(chat_id, await self.get_text(chat_id, "REGISTRATION_COMPLETED"))
        #         await self.main_menu(chat_id)
        #         return
        #     await self.send_message(chat_id, await self.get_text(chat_id, "REGISTRATION_ERROR_CODE"))

    async def on_start_command(self, message: types.Message):
        command = message.text[1:]
        chat_id = message.chat.id
        if str(chat_id).startswith('-'):
            await message.reply(
                text=Messages.TEXT["BOT_START_IN_CHAT"].get("en"),
                reply_markup=await KeyboardManager.get_bot_open_keyboard(self.bot)
            )
            return
        bot_info = await self.bot.get_me()
        current_bot_id = bot_info.username
        is_clone = await self.database_interface.is_clone_bot(current_bot_id)
        await self.create_and_launch_phantoms()
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
                    await self.database_interface.log_info(f"✅ Создана реферальная связь: {referrer_id} -> "
                                                           f"{chat_id} (бот: {current_bot_id})")
        await self.registration_menu(message)
        user_data = await self.database_interface.get_user(chat_id)
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
                    await HandlersManager.send_userinfo(self, chat_id, user_data, chat_id in self.admin_ids)
            elif start_param == "deb":
                await self.database_interface.update_user(chat_id, new_bet=True)
                await HandlersManager.select_bet(self, chat_id, user_data)
                return
        if not await HandlersManager.check_subscription(self, chat_id, message.from_user.first_name):
            return
        await self.main_menu(chat_id)

    async def on_text(self, message: types.Message):
        chat_id = message.chat.id
        if str(chat_id).startswith('-'):
            return
        input_type = await self.database_interface.get_input_type(chat_id)
        message_id = message.message_id
        input_text = message.text.strip()

        await self.bot.delete_message(chat_id, message_id)
        if input_type == 0:
            return

        elif input_type == 1:
            await self.registration_menu(message, 1)
        elif input_type == 2:
            await self.registration_menu(message, 2)

        elif input_type == 10:
            from .handlers.referral_handler import ReferralHandler
            await ReferralHandler.process_token_input(self, chat_id, input_text)

        elif input_type == 20 or input_type == 21:
            if not input_text.startswith('-'):
                input_text = '-' + input_text
            channel_username = await self.get_channel_username(input_text)
            if channel_username is None:
                await self.send_message(chat_id, await self.get_text(chat_id, "CHANNEL_CONFIG_ERROR"))
                return
            await self.database_interface.update_user(chat_id, block_input=False, input_type=0)
            if input_type == 20:
                await self.database_interface.set_bot_config((await self.bot.get_me()).id, chat_id=input_text,
                                                             chat_username=channel_username)
            else:
                await self.database_interface.set_bot_config((await self.bot.get_me()).id, news_chat_id=input_text,
                                                             news_channel_username=channel_username)
            await self.send_message(input_text, await self.get_text(chat_id, "CHANNEL_TEST_MESSAGE"))
            await self.send_message(chat_id, await self.get_text(chat_id, "CHANNEL_CONFIG_SUCCESS"))
            await self.main_menu(chat_id)
        elif input_type == 30 or input_type == 31:
            user_data = await self.database_interface.get_user(chat_id)
            if input_type == 30:
                await self.database_interface.add_custom_message(chat_id, input_text)
                await HandlersManager.get_custom_message(self, chat_id, user_data, 1)
            elif input_type == 31:
                custom_markup = KeyboardManager.get_markup_from_text(user_data.get("language", "en"), input_text)
                custom_message = await self.database_interface.get_custom_messages(chat_id)
                await HandlersManager.get_custom_message(self, chat_id, user_data, 2, custom_message, custom_markup)

    async def on_inline_button(self, callback_query: types.CallbackQuery):
        command = callback_query.data
        if not command:
            return
        chat_id = callback_query.message.chat.id
        if command == "delete":
            await self.bot.delete_message(chat_id, callback_query.message.message_id)
            await callback_query.answer()
            return
        if str(chat_id).startswith('-'):
            return
        user_data = await self.database_interface.get_user(chat_id)
        block_input = user_data.get("block_input", False)
        if command == "register_cancel":
            if not user_data.get("in_registration", False):
                return
            await HandlersManager.register_cancel(self, chat_id)
            return
        elif command == "referral-cancel":
            await ReferralHandler.referral_cancel(self, chat_id,
                                                  callback_query.message.message_id)
            return
        elif command == "custom-message-cancel":
            await HandlersManager.custom_message_cancel(self, chat_id, user_data,
                                                        callback_query.message.message_id)
            return
        if block_input:
            return
        if command == "back":
            await self.main_menu(chat_id, callback_query.message.message_id)

        # ════════════════ Регистрация ════════════════
        elif command == "register_back":
            if not user_data.get("in_registration", False):
                return
            await HandlersManager.register_back(self, callback_query)
        elif command == "check-subscription":
            if await HandlersManager.check_subscription(self, chat_id, user_data["username"]):
                await self.main_menu(chat_id,
                                     callback_query.message.message_id)
            await self.bot.delete_message(chat_id,
                                          callback_query.message.message_id)
            return

        # ════════════════════ Игры ═══════════════════
        if command.startswith("select-bet-data"):
            parts = command.split(':')
            if len(parts) == 3:
                bet_data_type = parts[1]
                value = parts[2]
                await HandlersManager.select_bet_data(self, chat_id, user_data, bet_data_type, value,
                                                      callback_query.message.message_id)
            await callback_query.answer()
        elif command.startswith("finalize-bet-data"):
            parts = command.split(':')
            if len(parts) == 2:
                bet_data_type = parts[1]
                await HandlersManager.finalize_bet_data(self, chat_id, user_data, bet_data_type,
                                                        callback_query.message.message_id)
            await callback_query.answer()
        elif command.startswith("select-bet"):
            await self.database_interface.update_user(chat_id, new_bet="new_bet" in command)
            user_data['new_bet'] = "new_bet" in command
            await HandlersManager.select_bet(self, chat_id, user_data, callback_query)
        elif command.startswith("start-game"):
            bet = float(command.split(':')[1])
            await HandlersManager.start_game(self, chat_id, user_data, bet,
                                             callback_query.message.message_id)
        elif command.startswith("game_action:"):
            action = callback_query.data[len("game_action:"):]
            await InteractiveGameHandlers.handle_game_action(self, callback_query, action)

        # ═════════════════ Настройки ═════════════════
        elif command == "change-game":
            await HandlersManager.change_game(self, chat_id, user_data,
                                              callback_query.message.message_id)
        elif command.startswith("set-game"):
            await HandlersManager.set_game(self, chat_id, command,
                                           callback_query.message.message_id)
        elif command == "change-language":
            await HandlersManager.change_language(self, chat_id,
                                                  callback_query.message.message_id)
        elif command == "change-email":
            await HandlersManager.change_email(self, callback_query)
        elif command.startswith("language"):
            await HandlersManager.language(self, chat_id, command,
                                           callback_query.message.message_id)

        # ═══════════════════ Баланс ══════════════════
        elif command == "balance":
            await HandlersManager.balance(self, chat_id, user_data,
                                          callback_query.message.message_id)
        elif command == "balance-deposit":
            await HandlersManager.get_currency(self, chat_id, user_data, "deposit", self.crypto_pay.supported_codes,
                                               callback_query)
        elif command == "balance-withdraw":
            await HandlersManager.get_currency(self, chat_id, user_data, "withdraw",
                                               await self.crypto_pay.get_currencies_with_balance(), callback_query)
        elif command.startswith("deposit-select-currency"):
            currency = command.split(':')[1]
            await HandlersManager.get_amount(self, chat_id, user_data, currency, "deposit",
                                             callback_query.message.message_id)
        elif command.startswith("withdraw-select-currency"):
            currency = command.split(':')[1]
            await HandlersManager.get_amount(self, chat_id, user_data, currency, "withdraw",
                                             callback_query.message.message_id)
        elif command.startswith("do-deposit"):
            currency = command.split(':')[1]
            amount = float(command.split(':')[2])
            await HandlersManager.do_deposit(self, chat_id, user_data, currency, amount,
                                             callback_query.message.message_id)

        # TODO: удалить после реализации вебхуков
        elif command.startswith("check-deposit"):
            internal_tx_id = command.split(':')[1]
            await HandlersManager.check_deposit(self, chat_id, user_data, internal_tx_id, callback_query)
            await callback_query.answer()

        elif command.startswith("cancel-deposit"):
            parts = command.split(':')
            tx_id = parts[1]
            message_id = parts[2] if len(parts) > 2 else ""
            confirm = parts[3] if len(parts) > 3 else ""
            if await HandlersManager.check_deposit(self, chat_id, user_data, tx_id, callback_query, True):
                await callback_query.answer()
                return
            if not confirm:
                await HandlersManager.cancel_deposit_confirm(self, chat_id, user_data,
                                                             tx_id, callback_query.message.message_id)
                await callback_query.answer()
                return
            if confirm == "yes":
                await HandlersManager.cancel_deposit(self, chat_id, user_data, tx_id, callback_query)
                await self.bot.delete_message(chat_id, message_id)
            else:
                await self.bot.delete_message(chat_id, callback_query.message.message_id)
        elif command.startswith("do-withdraw"):
            currency = command.split(':')[1]
            amount = float(command.split(':')[2])
            await HandlersManager.do_withdraw(self, chat_id, user_data, currency, amount, callback_query)

        # ════════════════ Пользователь ═══════════════
        elif command == "profile":
            await HandlersManager.user(self, chat_id, f"user:{chat_id}")
        elif command.startswith("user"):
            await HandlersManager.user(self, chat_id, command)
        elif command == "leaderboard":
            await HandlersManager.leaderboard(self, chat_id, user_data)

        # ════════════════ Админ-панель ═══════════════
        elif command == "admin-panel":
            await HandlersManager.admin_panel(self, chat_id, user_data,
                                              callback_query.message.message_id)
        elif command == "admin-summary":
            await HandlersManager.admin_summary(self, chat_id, user_data,
                                                callback_query.message.message_id)
        elif command.startswith("admin-list-players"):
            await HandlersManager.admin_list_players(self, chat_id, command, user_data,
                                                     callback_query.message.message_id)
        elif command.startswith("admin-show-logs"):
            await HandlersManager.admin_show_logs(self, chat_id, command, user_data,
                                                  callback_query.message.message_id)
        elif command.startswith("admin-user"):
            await HandlersManager.admin_user(self, chat_id, command, user_data,
                                             callback_query.message.message_id)
        elif command == "admin-show-tables":
            await HandlersManager.admin_show_tables(self, chat_id, user_data,
                                                    callback_query.message.message_id)
        elif command.startswith("admin-tables"):
            table = command.split(':')[1]
            await HandlersManager.admin_show_table(self, chat_id, table, user_data,
                                                   callback_query.message.message_id)
        elif command == "admin-issue-balance":
            await HandlersManager.admin_issue_balance(self, chat_id, user_data, callback_query)
        elif command == "admin-reset-balance":
            await HandlersManager.admin_reset_balance(self, chat_id, user_data, callback_query)
        elif command == "admin-get-balance":
            await HandlersManager.admin_get_balance(self, chat_id)
        elif command.startswith("admin-game-settings"):
            await HandlersManager.admin_game_settings_handler(self, chat_id, user_data, command,
                                                              callback_query.message.message_id)
        elif command.startswith("admin-game-config"):
            await HandlersManager.admin_game_config_handler(self, chat_id, user_data, command,
                                                            callback_query.message.message_id)
        elif command.startswith("admin-bot-config"):
            await HandlersManager.admin_bot_config(self, chat_id, user_data, command,
                                                   callback_query.message.message_id)
        elif command == "update-max-bet":
            await HandlersManager.update_max_bet(self, chat_id, user_data, callback_query)
        elif command.startswith("channel-message"):
            await HandlersManager.channel_message_menu(self, chat_id, user_data, command,
                                                       callback_query.message.message_id)
        elif command == "custom-message-send":
            await HandlersManager.send_custom_message(self, chat_id, user_data,
                                                      callback_query.message)
        elif command == "create-leaderboard":
            await HandlersManager.create_leaderboard(self, chat_id, user_data, callback_query)
        elif command.startswith("giveaway"):
            await HandlersManager.giveaway(self, chat_id, user_data, command,
                                           callback_query.message.message_id)
        elif command == "profits":
            await HandlersManager.profits(self, chat_id, user_data,
                                          callback_query.message.message_id)
        elif command == "withdrawal-profits":
            await HandlersManager.withdrawal_profits(self, chat_id, user_data, callback_query)

        # ═════════════════ Рефералка ═════════════════
        elif command == "referral-menu":
            await ReferralHandler.referral_menu(self, chat_id, user_data,
                                                callback_query.message.message_id)
        elif command == "referral-create":
            await ReferralHandler.create_clone_bot(self, chat_id, user_data)
        elif command == "referral-stats":
            await ReferralHandler.my_referrals(self, chat_id, user_data,
                                               callback_query.message.message_id)

        # ═══════════════════ Прочее ══════════════════
        elif command == "rules":
            await HandlersManager.rules(self, chat_id, user_data,
                                        callback_query.message.message_id)
        await callback_query.answer()

    async def encrypt_user_data(self, chat_id: int):
        from Crypto.Cipher import AES
        from Crypto.Random import get_random_bytes
        from Crypto.Util.Padding import pad
        import base64
        import json
        import hashlib
        SECRET_KEY = hashlib.sha256(config.SECRET_KEY_STR.encode()).digest()
        user_data = await self.database_interface.get_user(chat_id)
        iv = get_random_bytes(16)
        cipher = AES.new(SECRET_KEY, AES.MODE_CBC, iv)
        json_data = json.dumps(user_data).encode('utf-8')
        padded_data = pad(json_data, AES.block_size)
        ciphertext = cipher.encrypt(padded_data)
        json_size = len(json_data).to_bytes(4, byteorder='big')
        encrypted = base64.b64encode(json_size + iv + ciphertext).decode('utf-8')
        from urllib.parse import quote
        encrypted_safe = quote(encrypted)
        return f"{config.WEBAPP_URL}/index.html?data={encrypted_safe}"

    async def on_web_app(self, chat_id: int, data):
        await self.send_message(chat_id, str(data))

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

    @staticmethod
    def get_phantom_bet(max_bet: float):
        max_bet = max_bet
        min_bet = 0.01
        bet_values = []
        if max_bet <= 10:
            n_points = 12
            step = (max_bet - min_bet) / (n_points - 1) if max_bet > min_bet else 0
            bet_values = [round(min_bet + i * step, 2) for i in range(n_points)]
            bet_values = [v for v in bet_values if v <= max_bet]
        else:
            log_min = math.log10(min_bet)
            log_max = math.log10(max_bet)
            step = (log_max - log_min) / 18
            for i in range(19):
                log_val = log_min + step * i
                val = 10 ** log_val
                if val < 1:
                    bet_values.append(round(val, 2))
                elif val < 100:
                    bet_values.append(round(val, 1))
                else:
                    bet_values.append(int(val))
            bet_values = sorted(set(bet_values))
        bet_values = sorted(set(bet_values))
        n = len(bet_values)
        middle_idx = (n - 1) / 2
        sigma = n / 4
        weights = []
        for i in range(n):
            distance = abs(i - middle_idx)
            weight = math.exp(-(distance ** 2) / (2 * sigma ** 2))
            weights.append(weight)
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]
        return random.choices(bet_values, weights=weights, k=1)[0]

    @staticmethod
    def get_phantom_pause() -> int:
        import datetime
        current_hour = datetime.datetime.now().hour
        if current_hour in [12, 13, 14, 19, 20, 21, 22, 23]:
            pause_minutes = random.choices(
                [5, 7, 10, 12, 15],
                weights=[20, 25, 30, 20, 5],
                k=1
            )[0]
        elif current_hour in [10, 11, 15, 16, 17, 18]:
            pause_minutes = random.choices(
                [10, 15, 20, 25],
                weights=[15, 30, 35, 20],
                k=1
            )[0]
        else:
            pause_minutes = random.choices(
                [20, 30, 40, 50],
                weights=[10, 20, 40, 30],
                k=1
            )[0]
        variance = pause_minutes * 0.2
        pause_minutes += random.uniform(-variance, variance)
        return pause_minutes * 60

    async def broadcast_phantom_wins(self):
        while True:
            max_bet = await self.database_interface.get_max_bet()
            bet = self.get_phantom_bet(max_bet)
            user_id = random.randrange(0, 50)
            game_id = random.choices(
                list(self.CasinoGames.keys()),
                weights=[self.GameWeights[game_id] for game_id in self.CasinoGames.keys()],
                k=1
            )[0]
            game = await self.game_manager.get_game(game_id)
            result = await game.get_phantom_win(user_id, bet, self)
            if result is None:
                continue
            if result.win_amount <= 0:
                continue
            await self.database_interface.update_balance(user_id, result.win_amount, 'win', 'Phantom win')
            channel_id = await self.chat_id()
            if channel_id:
                user_data = await self.database_interface.get_user(user_id)
                final_result = result.animations_data["final_result"]
                final_result_image = result.animations_data.get("final_result_image")
                icon = result.animations_data["icon"]
                user_bet = result.user_bet
                custom_data = {
                    "username": f"<a href='https://t.me/"
                                f"{(await self.bot.get_me()).username}?"
                                f"start=user_{user_data['hashed_username']}'>{user_data['username']}</a>",
                    "amount": f"{result.win_amount:.2f}",
                    "bet": str(result.bet_amount),
                    "user_bet": user_bet,
                    "final_result": final_result,
                    "icon": icon
                }
                if final_result_image:
                    await self.bot.send_photo(channel_id,
                                              BufferedInputFile(
                                                  file=final_result_image.getvalue(),
                                                  filename='image.png'
                                              ),
                                              caption=await self.get_text(user_id, "GAME_WIN_ANNOUNCEMENT", user_data,
                                                                          custom_data),
                                              reply_markup=KeyboardManager.get_channel_announcement_keyboard(
                                                  (await self.bot.get_me()).username),
                                              parse_mode="HTML")
                else:
                    await self.send_message(channel_id,
                                            await self.get_text(user_id, "GAME_WIN_ANNOUNCEMENT", user_data,
                                                                custom_data),
                                            reply_markup=KeyboardManager.get_channel_announcement_keyboard(
                                                (await self.bot.get_me()).username))
            await asyncio.sleep(self.get_phantom_pause())

    async def create_and_launch_phantoms(self):
        usernames = [
            "Димогорган",
            "TyLEnKa568",
            "._.",
            "MotyaNeloh",
            "ал",
            "Name?",
            "~Vilka~",
            "Achoch",
            ">///<",
            "JL",
            "H2",
            "Баракуда",
            "*",
            "Т-Банк",
            ">.<",
            "Кремлёв",
            "кiт",
            "Dmitri228",
            "8=======*",
            "Олег",
            "Gravis",
            "Kakish",
            "Саня",
            "чортов",
            "Vova",
            "Святослав",
            "$$$",
            ".",
            "MotoWay",
            "Kuro",
            "Саншко",
            "When",
            "Hinner1",
            "Сева",
            "Л1гхт",
            "миша",
            "Мьоп",
            "NIKTO",
            "Елисейка",
            "Вадим",
        ]
        for i in range(len(usernames)):
            await self.database_interface.create_user(i + 10, usernames[i], random.choice(["en", "ru"]))
        # noinspection PyAsyncCall
        asyncio.create_task(self.broadcast_phantom_wins())

    async def send_message(self, chat_id: int, text: str, parse_mode: str = "HTML", image: BytesIO = None,
                           reply_markup: Optional[Union[InlineKeyboardMarkup, ReplyKeyboardRemove]] = None,
                           disable_web_page_preview: Optional[bool] = True, add_delete_keyboard=True):
        """
        Отправляет текстовое сообщение с опциональными параметрами parse_mode,
        клавиатурой и отключением предпросмотра ссылок.
        """
        if reply_markup is None and add_delete_keyboard:
            reply_markup = KeyboardManager.get_delete_keyboard()
        if image:
            return await self.bot.send_photo(
                chat_id,
                photo=BufferedInputFile(file=image.getvalue(), filename='frame.png'),
                parse_mode=parse_mode,
                reply_markup=reply_markup)
        return await self.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
            disable_web_page_preview=disable_web_page_preview)

    async def edit_message(self, chat_id: int, text: str, message_id: Optional[int] = None,
                           image: Optional[BytesIO] = None,
                           reply_markup: Optional[Union[InlineKeyboardMarkup, ReplyKeyboardRemove]] = None,
                           add_delete_keyboard: Optional[bool] = True):
        if reply_markup is None and add_delete_keyboard:
            reply_markup = KeyboardManager.get_delete_keyboard()
        try:
            if message_id:
                if image:
                    return await self.bot.edit_message_media(
                        chat_id=chat_id,
                        message_id=message_id,
                        media=InputMediaPhoto(
                            media=BufferedInputFile(
                                file=image.getvalue(),
                                filename='frame.png'
                            ),
                            caption=text,
                            parse_mode="HTML"
                        ),
                        reply_markup=reply_markup
                    )
                else:
                    try:
                        return await self.bot.edit_message_text(
                            chat_id=chat_id,
                            message_id=message_id,
                            text=text,
                            parse_mode="HTML",
                            reply_markup=reply_markup
                        )
                    except Exception:
                        await self.bot.delete_message(chat_id, message_id)
                        await self.send_message(chat_id, text, reply_markup=reply_markup,
                                                add_delete_keyboard=add_delete_keyboard)
            else:
                return await self.send_message(chat_id, text, image=image,
                                               reply_markup=reply_markup, add_delete_keyboard=add_delete_keyboard)
        except Exception:
            pass
