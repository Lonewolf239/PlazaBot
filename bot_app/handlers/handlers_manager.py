from aiogram import types
from typing import Any

from bot_app.keyboards import KeyboardManager


class HandlersManager:
    # ════════════════ Регистрация ════════════════
    @staticmethod
    async def register_cancel(bot, chat_id: int):
        await bot.database_interface.update_user(chat_id,
                                                 input_type=0,
                                                 email_verified=True,
                                                 block_input=False)
        await bot.main_menu(chat_id)

    @staticmethod
    async def register_back(bot, callback_query: types.CallbackQuery):
        await bot.registration_menu(callback_query.message)

    @staticmethod
    async def check_subscription(bot, chat_id: int, first_name: str) -> bool:
        try:
            user_data = await bot.database_interface.get_user(chat_id)
            if not user_data:
                return True
            if bool(user_data.get("subscribed")):
                return True
            bot_config = await bot.bot_config()
            if not bot_config:
                return True
            channel_id = bot_config.get("chat_id")
            channel_username = bot_config.get("chat_username")
            if not channel_id or not channel_username:
                return True
            member = await bot.bot.get_chat_member(f"@{channel_username}", chat_id)
            if member.status in ("member", "administrator", "creator"):
                await bot.database_interface.update_user(chat_id, subscribed=True)
                await bot.send_message(chat_id, f"👋 Добро пожаловать, {first_name}!\n\n✅ Вы подписаны на наш канал.")
                return True
            await bot.send_message(chat_id,
                                   f"👋 Привет, {first_name}!\n\n❌ Для продолжения работы подпишитесь на наш канал:",
                                   reply_markup=KeyboardManager.get_channel_keyboard(channel_username))
        except Exception:
            await bot.send_message(chat_id, "⚠️ Произошла ошибка при проверке подписки.\nПожалуйста, повторите попытку")
        return False

    # ════════════════════ Игры ═══════════════════
    @staticmethod
    async def start_game(bot, chat_id: int, user_data: dict[str, Any], bet: float):
        """Начало игры"""
        if bet > float(user_data.get("balance", "0.0")):
            await bot.send_message(chat_id, await bot.get_text(chat_id, "INSUFFICIENT_BALANCE", user_data))
            await bot.main_menu(chat_id)
            return

        message = await bot.send_message(chat_id, await bot.get_text(chat_id, "GAME_STARTING", user_data),
                                         add_delete_keyboard=False)
        selected_game = int(user_data.get("selected_game", 0))
        game = await bot.game_manager.get_game(selected_game)
        bet_data = None
        if game.need_bet_data:
            bet_data = bot.bet_data_collector.format_bet_data(chat_id)
            bot.bet_data_collector.reset(chat_id)
        await bot.game_manager.start_game(
            bot, chat_id, message.message_id, selected_game,
            bet, bet_data, HandlersManager.send_frame
        )

    @staticmethod
    async def select_bet(bot, chat_id: int, user_data: dict[str, Any]):
        """Выбор ставки или начало сбора bet_data"""
        if bot.game_manager.is_user_playing(chat_id):
            await bot.send_message(chat_id, await bot.get_text(chat_id, "USER_ALREADY_PLAYING", user_data))
            await bot.main_menu(chat_id)
            return
        balance_str = user_data.get("balance", "0").strip()
        try:
            balance_float = float(balance_str) if balance_str else 0.0
            if balance_float <= 0:
                await bot.send_message(chat_id, await bot.get_text(chat_id, "EMPTY_BALANCE_FOR_BET", user_data))
                await bot.main_menu(chat_id)
                return
        except (ValueError, TypeError):
            await bot.send_message(chat_id, await bot.get_text(chat_id, "EMPTY_BALANCE_FOR_BET", user_data))
            await bot.main_menu(chat_id)
            return
        game = await bot.game_manager.get_game(int(user_data.get("selected_game", "0")))
        if game.need_bet_data and game.bet_data_flow:
            bot.bet_data_collector.start_collection(chat_id, game.bet_data_flow)
            await HandlersManager._show_next_bet_parameter(bot, chat_id, user_data)
        else:
            await bot.send_message(
                chat_id,
                await bot.get_text(chat_id, "SELECT_BET", user_data),
                reply_markup=KeyboardManager.get_bet_keyboard(
                    game,
                    float(user_data.get("balance", "0.0")),
                    user_data.get("language", "en")
                )
            )

    @staticmethod
    async def _show_next_bet_parameter(bot, chat_id: int, user_data: dict[str, Any]):
        """Показать следующий параметр для выбора"""
        current_param = bot.bet_data_collector.get_current_parameter(chat_id)
        if not current_param:
            await HandlersManager._show_final_bet_selection(bot, chat_id, user_data)
            return
        language = user_data.get("language", "en")
        progress = bot.bet_data_collector.get_progress_text(chat_id, language)
        param_name = current_param.param_name.get(language, current_param.param_type)
        message_text = f"{progress}\n\n" if progress else ""
        message_text += f"Выберите {param_name}:" if language == 'ru' else f"Select {param_name}:"
        collected = bot.bet_data_collector.get_collected_data(chat_id) or {}
        bet_type = collected.get('bet_type', '')
        await bot.send_message(chat_id, message_text,
                               reply_markup=KeyboardManager.get_bet_parameter_keyboard(
                                   current_param, language, bet_type))

    @staticmethod
    async def _show_final_bet_selection(bot, chat_id: int, user_data: dict[str, Any]):
        """Показать финальный выбор ставки после сбора всех параметров"""
        language = user_data.get("language", "en")
        game = await bot.game_manager.get_game(int(user_data.get("selected_game", "0")))
        progress = bot.bet_data_collector.get_progress_text(chat_id, language)
        message_text = f"{progress}\n\n"
        message_text += await bot.get_text(chat_id, "SELECT_BET", user_data)
        await bot.send_message(
            chat_id,
            message_text,
            reply_markup=KeyboardManager.get_bet_keyboard(
                game,
                float(user_data.get("balance", "0.0")),
                language
            )
        )

    @staticmethod
    async def select_bet_data(bot, chat_id: int, user_data: dict[str, Any],
                              bet_data_type: str, value: str):
        """Обработка выбора параметра ставки"""
        if not bot.bet_data_collector.add_value(chat_id, bet_data_type, value):
            await bot.main_menu(chat_id)
            return
        if bot.bet_data_collector.is_complete(chat_id):
            await HandlersManager._show_final_bet_selection(bot, chat_id, user_data)
        else:
            await HandlersManager._show_next_bet_parameter(bot, chat_id, user_data)

    @staticmethod
    async def send_frame(bot, chat_id: int, message_id: int, frame: str):
        try:
            await bot.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=frame)
        except Exception as e:
            bot.logger.error(f"Ошибка при редактировании сообщения: {e}")

    @staticmethod
    async def on_game_started(bot, session):
        user_id = int(session["user_id"])
        game_id = int(session["game_id"])
        bet_amount = float(session["bet_amount"])
        started_at = session["started_at"]
        await bot.referral_manager.process_user_action(user_id, (await bot.bot.get_me()).id, "bet", bet_amount)
        await bot.database_interface.update_balance(user_id, -bet_amount,
                                                    "bet", f"Bet in game: {game_id}, started_at: {started_at}")

    @staticmethod
    async def on_game_finished(bot, result, session):
        user_id = int(session["user_id"])
        game_id = int(session["game_id"])
        started_at = session["started_at"]
        user_data = await bot.database_interface.get_user(user_id)
        final_result = result.animations_data["final_result"]
        icon = result.animations_data["icon"]
        user_bet = result.user_bet
        if result.is_win:
            custom_data = {
                "username": f"<a href='https://t.me/"
                            f"{(await bot.bot.get_me()).username}?"
                            f"start=user_{user_data['hashed_username']}'>{user_data['username']}</a>",
                "amount": f"{result.win_amount:.2f}",
                "bet": str(result.bet_amount),
                "user_bet": user_bet,
                "final_result": final_result,
                "icon": icon
            }
            await bot.database_interface.update_balance(
                user_id, result.win_amount, "win",
                f"Game finished: {game_id}, multiplier: {result.multiplier}x, started_at: {started_at}"
            )
            await bot.referral_manager.process_user_action(user_id, (await bot.bot.get_me()).id,
                                                           "win", result.win_amount)
            try:
                channel_id = await bot.chat_id()
                if channel_id:
                    await bot.send_message(channel_id,
                                           await bot.get_text(user_id, "GAME_WIN_ANNOUNCEMENT", user_data, custom_data),
                                           reply_markup=KeyboardManager.get_channel_announcement_keyboard(
                                               (await bot.bot.get_me()).username))
            except Exception:
                pass
            await bot.send_message(user_id, await bot.get_text(user_id, "GAME_WIN", user_data, custom_data),
                                   reply_markup=KeyboardManager.get_game_again_keyboard(
                                       user_data.get("language", "en")))
        else:
            custom_data = {"final_result": final_result, "user_bet": user_bet, "icon": icon}
            await bot.send_message(user_id, await bot.get_text(user_id, "GAME_LOSE", user_data, custom_data),
                                   reply_markup=KeyboardManager.get_game_again_keyboard(
                                       user_data.get("language", "en")))

    # ═════════════════ Настройки ═════════════════
    @staticmethod
    async def settings(bot, chat_id: int, user_data: dict[str, Any]):
        text = await bot.get_text(chat_id, "SETTINGS", user_data)
        text = text.replace("semga05@mail.ru", await bot.get_text(chat_id, "NO_EMAIL"))
        await bot.send_message(chat_id, text,
                               reply_markup=KeyboardManager.get_settings_keyboard(user_data.get("language", "en")))

    @staticmethod
    async def change_language(bot, chat_id: int):
        await bot.send_message(chat_id, await bot.get_text(chat_id, "CHANGE_LANGUAGE"),
                               reply_markup=KeyboardManager.get_language_keyboard())

    @staticmethod
    async def change_game(bot, chat_id: int, user_data: dict[str, Any]):
        await bot.send_message(chat_id, await bot.get_text(chat_id, "CHANGE_GAME", user_data),
                               reply_markup=KeyboardManager.get_change_game_keyboard(
                                   bot.game_manager.get_available_games(),
                                   user_data.get("language", "ru")))

    @staticmethod
    async def set_game(bot, chat_id: int, command: str):
        game_id = int(command[len("set-game:"):])
        await bot.database_interface.update_user(chat_id, selected_game=game_id)
        await bot.main_menu(chat_id)

    @staticmethod
    async def change_email(bot, callback_query: types.CallbackQuery):
        await bot.registration_menu(callback_query.message, first_message="CHANGE_EMAIL", ignore_db=True)

    @staticmethod
    async def language(bot, chat_id: int, command: str):
        language_code = command[len("language:"):]
        await bot.database_interface.update_user(chat_id, language=language_code)
        await bot.main_menu(chat_id)

    # ═══════════════════ Баланс ══════════════════
    @staticmethod
    async def balance(bot, chat_id: int, user_data: dict[str, Any]):
        await bot.send_message(chat_id, await bot.get_text(chat_id, "BALANCE", user_data),
                               reply_markup=KeyboardManager.get_balance_keyboard(user_data.get("language", "en")))

    @staticmethod
    async def get_currency(bot, chat_id: int, user_data: dict[str, Any],
                           operation_type: str, available_currencies: list[str]):
        currency_list = []
        if operation_type == "withdraw":
            balance_str = user_data.get("balance", "0").strip()
            try:
                balance_float = float(balance_str) if balance_str else 0.0
                if balance_float <= 0:
                    await bot.send_message(
                        chat_id,
                        await bot.get_text(chat_id, "EMPTY_BALANCE_FOR_WITHDRAW", user_data)
                    )
                    await bot.main_menu(chat_id)
                    return
            except (ValueError, TypeError):
                await bot.send_message(
                    chat_id,
                    await bot.get_text(chat_id, "EMPTY_BALANCE_FOR_WITHDRAW", user_data)
                )
                await bot.main_menu(chat_id)
                return
        for asset in bot.crypto_pay.supported_assets:
            if asset.is_fiat:
                continue
            if asset.code not in available_currencies:
                continue
            currency_list.append({"code": asset.code, "name": asset.name})
        await bot.send_message(
            chat_id,
            await bot.get_text(chat_id, "SELECT_CURRENCY", user_data),
            reply_markup=KeyboardManager.get_currency_keyboard(
                user_data.get("language", "en"),
                currency_list,
                operation_type
            )
        )

    @staticmethod
    async def get_amount(bot, chat_id: int, user_data: dict[str, Any], currency: str, operation_type: str):
        ok, markup = KeyboardManager.get_amount_keyboard(
            user_data.get("language", "en"), currency,
            operation_type, user_data.get("balance", "0.0"))
        tag = "SELECT_AMOUNT" if ok else "CURRENCY_NOT_AVAILABLE"
        await bot.send_message(chat_id, await bot.get_text(chat_id, tag, user_data), reply_markup=markup)

    @staticmethod
    async def do_deposit(bot, chat_id: int, user_data: dict[str, Any], currency: str, amount: float):
        deposit = await bot.crypto_pay.initiate_deposit(chat_id, amount, currency)
        if deposit["status"] == "payment_pending":
            await bot.send_message(chat_id, await bot.get_text(chat_id, "PAYMENT_LINK", user_data),
                                   reply_markup=KeyboardManager.get_pay_keyboard(
                                       user_data.get("language", "en"), deposit, deposit["internal_tx_id"]))

    @staticmethod
    async def do_withdraw(bot, chat_id: int, user_data: dict[str, Any], currency: str, amount: float):
        withdraw = await bot.crypto_pay.initiate_withdrawal(chat_id, amount, currency)
        if withdraw:
            custom_data = {"amount": f"{amount:.8f}", "currency": currency}
            success_text = await bot.get_text(chat_id, "WITHDRAW_SUCCESS", user_data, custom_data)
            await bot.database_interface.update_balance(chat_id, -amount, "withdrawal")
            await bot.send_message(chat_id, success_text)
        else:
            error_text = await bot.get_text(chat_id, "WITHDRAW_ERROR", user_data)
            await bot.send_message(chat_id, error_text)
        await bot.main_menu(chat_id)

    @staticmethod
    async def check_deposit(bot, chat_id, user_data, internal_tx_id) -> bool:
        invoice = await bot.crypto_pay.get_invoice(internal_tx_id)
        if invoice.status == "paid":
            await bot.send_message(chat_id, await bot.get_text(chat_id, "DEPOSIT_SUCCESS", user_data))
            amount = float(invoice.amount) * float(invoice.paid_usd_rate)
            await bot.database_interface.update_balance(chat_id, amount, "deposit")
            await bot.main_menu(chat_id)
            return True
        else:
            await bot.send_message(chat_id, await bot.get_text(chat_id, "DEPOSIT_FAILED", user_data))
            return False

    @staticmethod
    async def cancel_deposit_confirm(bot, chat_id: int, user_data: dict[str, Any],
                                     internal_tx_id: str, message_id: int):
        await bot.send_message(chat_id, await bot.get_text(chat_id, "CANCEL_DEPOSIT_CONFIRM", user_data),
                               reply_markup=KeyboardManager.get_confirm_keyboard(
                                   f"cancel-deposit:{internal_tx_id}:{message_id}",
                                   user_data.get("language", "en")))

    @staticmethod
    async def cancel_deposit(bot, chat_id: int, user_data: dict[str, Any], internal_tx_id: str):
        if await bot.crypto_pay.cancel_deposit(internal_tx_id):
            await bot.send_message(chat_id, await bot.get_text(chat_id, "DEPOSIT_CANCELLED", user_data))
        else:
            await bot.send_message(chat_id, await bot.get_text(chat_id, "DEPOSIT_CANCEL_FAILED", user_data))
        await bot.main_menu(chat_id)

    # ════════════════ Пользователь ═══════════════
    @staticmethod
    async def user(bot, chat_id: int, command: str):
        username = command[len("user:"):]
        user = await bot.database_interface.get_user_by_username(username)
        await bot.send_userinfo(chat_id, user, profile=True)
        await bot.main_menu(chat_id)

    # ════════════════ Админ-панель ═══════════════
    @staticmethod
    async def admin_panel(bot, chat_id: int, user_data: dict[str, Any]):
        if chat_id not in bot.admin_ids:
            return
        await bot.send_message(chat_id, await bot.get_text(chat_id, "ADMIN_PANEL", user_data),
                               reply_markup=KeyboardManager.get_admin_keyboard(user_data.get("language", "en")))

    @staticmethod
    async def admin_summary(bot, chat_id: int, user_data: dict[str, Any]):
        needed, count, avg_bal, max_bal, min_bal = await bot.database_interface.get_needed(bot.admin_ids)
        text = (
            f"{await bot.get_text(chat_id, "ADMIN_SUMMARY_COUNT", user_data)}: {count}\n"
            f"{await bot.get_text(chat_id, "ADMIN_SUMMARY_NEEDED", user_data)}: {int(needed)} $\n"
            f"{await bot.get_text(chat_id, "ADMIN_SUMMARY_AVG_BALANCE", user_data)}: {int(avg_bal)} $\n"
            f"{await bot.get_text(chat_id, "ADMIN_SUMMARY_MAX_BALANCE", user_data)}: {max_bal}\n"
            f"{await bot.get_text(chat_id, "ADMIN_SUMMARY_MIN_BALANCE", user_data)}: {min_bal}"
        )
        await bot.send_message(chat_id, text,
                               reply_markup=KeyboardManager.get_back_keyboard(
                                   user_data.get("language", "en"),
                                   callback_data="admin-panel"))

    @staticmethod
    async def admin_list_players(bot, chat_id: int, command: str, user_data: dict[str, Any]):
        page = int(command.split(':')[1]) if ':' in command else 1
        text, lines, add_next_page = await bot.get_users_page(page)
        await bot.send_message(chat_id, text,
                               reply_markup=KeyboardManager.get_users_keyboard(
                                   user_data.get("language", "en"), lines, page, add_next_page))

    @staticmethod
    async def admin_show_logs(bot, chat_id: int, command: str, user_data: dict[str, Any]):
        page = int(command.split(':')[1]) if ':' in command else 1
        text, add_next_page = await bot.get_logs_page(page)
        await bot.send_message(chat_id, text,
                               reply_markup=KeyboardManager.get_logs_keyboard(
                                   user_data.get("language", "en"), page, add_next_page))

    @staticmethod
    async def admin_show_tables(bot, chat_id: int, user_data: dict[str, Any]):
        ok, tables = await bot.database_interface.get_tables()
        if not ok:
            await bot.send_message(chat_id, tables[0],
                                   reply_markup=KeyboardManager.get_back_keyboard(
                                       user_data.get("language", "en"),
                                       callback_data="admin-panel"))
            return
        await bot.send_message(chat_id, await bot.get_text(chat_id, "ADMIN_TABLES_LIST", user_data),
                               reply_markup=KeyboardManager.get_tables_keyboard(
                                   tables, user_data.get("language", "en")))

    @staticmethod
    async def admin_show_table(bot, chat_id: int, table: str, user_data: dict[str, Any]):
        bd = await bot.database_interface.display_table(table)
        for row in bd:
            await bot.send_message(chat_id, row)
        await HandlersManager.admin_panel(bot, chat_id, user_data)

    @staticmethod
    async def admin_issue_balance(bot, chat_id: int, user_data: dict[str, Any]):
        await bot.database_interface.set_balance(chat_id, 1000)
        await bot.send_message(chat_id, await bot.get_text(chat_id, "ADMIN_BALANCE_ISSUED", user_data))
        await HandlersManager.admin_panel(bot, chat_id, user_data)

    @staticmethod
    async def admin_reset_balance(bot, chat_id: int, user_data: dict[str, Any]):
        await bot.database_interface.reset_balance(chat_id)
        await bot.send_message(chat_id, await bot.get_text(chat_id, "ADMIN_BALANCE_RESET", user_data))
        await HandlersManager.admin_panel(bot, chat_id, user_data)

    @staticmethod
    async def admin_get_balance(bot, chat_id: int, user_data: dict[str, Any]):
        balance_data = await bot.crypto_pay.get_balance()

        def format_balance(balance: dict) -> str:
            """Форматирует баланс кошелька в красиво оформленный текст."""
            if not balance:
                return "Баланс пуст."
            formatted = ["💰 Баланс кошелька:"]
            for currency, info in balance.items():
                available = info.get("available", 0)
                onhold = info.get("onhold", 0)
                if available == 0 and onhold == 0:
                    continue
                formatted.append(
                    f"\n— {currency}:\n"
                    f"   Доступно: {available:,.8f}\n"
                    f"   Заморожено: {onhold:,.8f}"
                )
            return "\n".join(formatted)

        await bot.send_message(chat_id, format_balance(balance_data))
        await HandlersManager.admin_panel(bot, chat_id, user_data)

    @staticmethod
    async def admin_game_settings_handler(bot, chat_id: int, user_data: dict[str, Any], command):
        command_parts = command.split(':')
        if len(command_parts) > 2:
            game_id = int(command_parts[1])
            game_config = command_parts[2]
            await bot.database_interface.update_config(game_id, game_config)
            await HandlersManager.admin_panel(bot, chat_id, user_data)
            return
        if len(command_parts) > 1:
            game_id = int(command_parts[1])
            await HandlersManager.admin_game_settings(bot, chat_id, user_data, game_id)
            return
        await HandlersManager.admin_game_settings(bot, chat_id, user_data)

    @staticmethod
    async def admin_game_settings(bot, chat_id: int, user_data: dict[str, Any], game_id: int = None):
        language_code = user_data.get("language", "en")
        if game_id is None:
            await bot.send_message(chat_id, await bot.get_text(chat_id, "GAME_SETTINGS", user_data),
                                   reply_markup=KeyboardManager.get_games_keyboard(
                                       "admin-game-settings", bot.game_manager.get_available_games(), language_code))
            return
        game = await bot.game_manager.get_game(game_id)
        game_configs = bot.GameConfigs[game_id]
        game_name_text = await bot.get_text(chat_id, "GAME_INFO", user_data,
                                            {"game_icon": game.icon, "game_name": game.name(language_code)})
        await bot.send_message(chat_id, game_name_text,
                               reply_markup=KeyboardManager.get_game_configs_keyboard(
                                   game_id, game_configs, language_code))

    @staticmethod
    async def admin_game_config_handler(bot, chat_id: int, user_data: dict[str, Any], command):
        command_parts = command.split(':')
        if len(command_parts) > 1:
            game_id = int(command_parts[1])
            await HandlersManager.admin_game_config(bot, chat_id, user_data, game_id)
            return
        await HandlersManager.admin_game_config(bot, chat_id, user_data)

    @staticmethod
    async def admin_game_config(bot, chat_id: int, user_data: dict[str, Any], game_id: int = None):
        language_code = user_data.get("language", "en")
        if game_id is None:
            await bot.send_message(chat_id, await bot.get_text(chat_id, "GAME_CONFIG_SELECT", user_data),
                                   reply_markup=KeyboardManager.get_games_keyboard(
                                       "admin-game-config", bot.game_manager.get_available_games(), language_code))
            return
        game = await bot.game_manager.get_game(game_id)
        await bot.send_message(chat_id, game.get_config_info())
        await HandlersManager.admin_panel(bot, chat_id, user_data)

    @staticmethod
    async def admin_bot_config(bot, chat_id: int, user_data: dict[str, Any], command: str):
        language_code = user_data.get("language", "en")
        command_parts = command.split(':')
        if len(command_parts) > 1:
            if command_parts[1] == "set":
                await bot.database_interface.update_user(chat_id, block_input=True, input_type=20)
                await bot.send_message(chat_id, await bot.get_text(chat_id, "BOT_CONFIG_ENTER_ID", user_data))
                return
            else:
                await bot.database_interface.clear_bot_config(bot.bot.id)
                await HandlersManager.admin_panel(bot, chat_id, user_data)
                return
        bot_config = await bot.bot_config()
        if bot_config:
            channel_username = bot_config.get("chat_username", "")
            channel_display = f"@{channel_username}" if channel_username else "❌ Не подключён"
        else:
            channel_display = "❌ Не подключён"
        custom_data = {"channel_username": channel_display}
        await bot.send_message(chat_id, await bot.get_text(chat_id, "BOT_CONFIG", user_data, custom_data),
                               reply_markup=KeyboardManager.get_bot_config(language_code))

    @staticmethod
    async def admin_user(bot, chat_id: int, command: str, user_data: dict[str, Any]):
        username = command[len("admin-user:"):]
        await bot.send_userinfo(chat_id, await bot.database_interface.get_user_by_username(username), True)
        await HandlersManager.admin_panel(bot, chat_id, user_data)

    @staticmethod
    async def rules(bot, chat_id: int, user_data: dict[str, Any]):
        game = await bot.game_manager.get_game(int(user_data.get("selected_game", 0)))
        await bot.send_message(chat_id, game.rules(user_data.get("language", "en")),
                               reply_markup=KeyboardManager.get_back_keyboard(user_data.get("language", "en")))
