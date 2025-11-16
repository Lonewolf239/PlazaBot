from aiogram.types import CallbackQuery, Message
from typing import Any
from aiogram.types import BufferedInputFile, InputMediaPhoto

import config


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
    async def register_back(bot, callback_query: CallbackQuery):
        await bot.registration_menu(callback_query.message)

    @staticmethod
    async def check_subscription(bot, chat_id: int, first_name: str) -> bool:
        from ..keyboards import KeyboardManager
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
    async def start_game(bot, chat_id: int, user_data: dict[str, Any], bet: float, message_id: int):
        """Начало игры"""
        user_balance = float(user_data.get("balance", "0.0"))
        if bet > user_balance:
            await bot.edit_message(chat_id, await bot.get_text(chat_id, "INSUFFICIENT_BALANCE", user_data), message_id)
            await bot.main_menu(chat_id)
            return
        total_required = bet
        selected_game = int(user_data.get("selected_game", 0))
        game = await bot.game_manager.get_game(selected_game)
        bet_data = None
        if game.need_bet_data:
            bet_data = bot.bet_data_collector.format_bet_data(chat_id)
            bet_dict = {}
            bet_parts = bet_data.split(";")
            for part in bet_parts:
                key, value = part.split(":", 1)
                bet_dict[key] = value
            bet_values = bet_dict.get("bet_value", "")
            bet_values_list = [v.strip() for v in bet_values.split(",") if v.strip()]
            count_values = len(bet_values_list)
            total_required = bet * count_values
            if total_required > user_balance:
                await bot.edit_message(chat_id, await bot.get_text(chat_id, "INSUFFICIENT_BALANCE", user_data),
                                       message_id)
                await bot.main_menu(chat_id)
                return
            bot.bet_data_collector.reset(chat_id)
        await bot.edit_message(chat_id, await bot.get_text(chat_id, "GAME_STARTING", user_data),
                               message_id, add_delete_keyboard=False)
        await bot.game_manager.start_game(bot, chat_id, message_id,
                                          selected_game, total_required, bet_data, HandlersManager.send_frame)

    @staticmethod
    async def select_bet(bot, chat_id: int, user_data: dict[str, Any], callback_query: CallbackQuery = None):
        """Выбор ставки или начало сбора bet_data"""
        from ..keyboards import KeyboardManager
        if bot.game_manager.is_user_playing(chat_id):
            if callback_query:
                await callback_query.answer(await bot.get_text(chat_id, "USER_ALREADY_PLAYING", user_data), True)
            else:
                await bot.send_message(chat_id, await bot.get_text(chat_id, "USER_ALREADY_PLAYING", user_data))
                await bot.main_menu(chat_id)
            return
        balance = 0.0
        try:
            balance = float(user_data.get("balance", "0") or 0)
        except (ValueError, TypeError):
            pass
        if balance <= 0:
            if callback_query:
                await callback_query.answer(await bot.get_text(chat_id, "EMPTY_BALANCE_FOR_BET", user_data), True)
            else:
                await bot.send_message(chat_id, await bot.get_text(chat_id, "EMPTY_BALANCE_FOR_BET", user_data))
                await bot.main_menu(chat_id)
            return
        game = await bot.game_manager.get_game(int(user_data.get("selected_game", "0")))
        message_id = None
        if callback_query:
            message_id = callback_query.message.message_id
        if game.need_bet_data and game.bet_data_flow:
            bot.bet_data_collector.start_collection(chat_id, game.bet_data_flow)
            await HandlersManager._show_next_bet_parameter(bot, chat_id, user_data, message_id)
        else:
            await bot.edit_message(chat_id, await bot.get_text(chat_id, "SELECT_BET", user_data), message_id,
                                   reply_markup=KeyboardManager.get_bet_keyboard(game, balance,
                                                                                 user_data.get("language", "en")))

    @staticmethod
    async def _show_next_bet_parameter(bot, chat_id: int, user_data: dict[str, Any], message_id: int):
        """Показать следующий параметр для выбора"""
        from ..keyboards import KeyboardManager
        current_param = bot.bet_data_collector.get_current_parameter(chat_id)
        if not current_param:
            await HandlersManager._show_final_bet_selection(bot, chat_id, user_data, message_id)
            return
        language = user_data.get("language", "en")
        progress = bot.bet_data_collector.get_progress_text(chat_id, language)
        param_name = current_param.param_name.get(language, current_param.param_type)
        message_text = f"{progress}\n\n" if progress else ""
        if current_param.multi_select:
            max_select = current_param.multi_select_max
            message_text += f"Выберите до {max_select} вариантов {param_name}:" \
                if language == 'ru' else f"Select up to {max_select} {param_name}:"
        else:
            message_text += f"Выберите {param_name}:" if language == 'ru' else f"Select {param_name}:"
        collected = bot.bet_data_collector.get_collected_data(chat_id) or {}
        bet_type = collected.get('bet_type', '')
        selected_values = []
        if current_param.multi_select:
            selected_values = bot.bet_data_collector.get_multi_select_values(chat_id, current_param.param_type)
        keyboard = KeyboardManager.get_bet_parameter_keyboard(current_param, language,
                                                              bet_type, selected_values, current_param.multi_select)
        try:
            await bot.edit_message(chat_id, message_text, message_id, reply_markup=keyboard)
            return None
        except Exception as e:
            await bot.database_interface.log_error(f"Ошибка при редактировании сообщения: {e}")
            return await bot.send_message(chat_id, message_text, reply_markup=keyboard)

    @staticmethod
    async def _show_final_bet_selection(bot, chat_id: int, user_data: dict[str, Any], message_id: int):
        """Показать финальный выбор ставки после сбора всех параметров"""
        from ..keyboards import KeyboardManager
        language = user_data.get("language", "en")
        game = await bot.game_manager.get_game(int(user_data.get("selected_game", "0")))
        progress = bot.bet_data_collector.get_progress_text(chat_id, language)
        message_text = f"{progress}\n\n"
        message_text += await bot.get_text(chat_id, "SELECT_BET", user_data)
        keyboard = KeyboardManager.get_bet_keyboard(game, float(user_data.get("balance", "0.0")), language)
        if message_id:
            try:
                await bot.edit_message(chat_id, message_text, message_id, reply_markup=keyboard)
            except Exception as e:
                await bot.database_interface.log_error(f"Ошибка при редактировании сообщения: {e}")
                await bot.send_message(chat_id, message_text, reply_markup=keyboard)
        else:
            await bot.send_message(chat_id, message_text, reply_markup=keyboard)

    @staticmethod
    async def select_bet_data(bot, chat_id: int, user_data: dict[str, Any], bet_data_type: str,
                              value: str, message_id: int):
        """Обработка выбора параметра ставки"""
        current_param = bot.bet_data_collector.get_current_parameter(chat_id)
        if not current_param or current_param.param_type != bet_data_type:
            await bot.main_menu(chat_id, message_id)
            return
        if current_param.multi_select:
            if not bot.bet_data_collector.add_value(chat_id, bet_data_type, value):
                return
            await HandlersManager._show_next_bet_parameter(bot, chat_id, user_data, message_id)
        else:
            if not bot.bet_data_collector.add_value(chat_id, bet_data_type, value):
                await bot.main_menu(chat_id, message_id)
                return
            if bot.bet_data_collector.is_complete(chat_id):
                await HandlersManager._show_final_bet_selection(bot, chat_id, user_data, message_id)
            else:
                await HandlersManager._show_next_bet_parameter(bot, chat_id, user_data, message_id)

    @staticmethod
    async def finalize_bet_data(bot, chat_id: int, user_data: dict[str, Any], bet_data_type: str, message_id: int):
        """Завершить multi-select параметр и перейти к следующему"""
        current_param = bot.bet_data_collector.get_current_parameter(chat_id)
        if not current_param or current_param.param_type != bet_data_type:
            await bot.main_menu(chat_id, message_id)
            return
        if not current_param.multi_select:
            return
        if not bot.bet_data_collector.is_multi_select_complete(chat_id, bet_data_type):
            language = user_data.get("language", "en")
            error_msg = "Выберите хотя бы один вариант!" if language == 'ru' else "Select at least one option!"
            await bot.send_message(chat_id, error_msg)
            return
        bot.bet_data_collector.finalize_multi_select(chat_id, bet_data_type)
        if bot.bet_data_collector.is_complete(chat_id):
            await HandlersManager._show_final_bet_selection(bot, chat_id, user_data, message_id)
        else:
            await HandlersManager._show_next_bet_parameter(bot, chat_id, user_data, message_id)

    @staticmethod
    async def send_frame(bot, chat_id: int, message_id: int, frame: dict[str, Any]):
        try:
            image = frame.get("image")
            if image:
                await bot.bot.edit_message_media(
                    chat_id=chat_id,
                    message_id=message_id,
                    media=InputMediaPhoto(
                        media=BufferedInputFile(
                            file=image.getvalue(),
                            filename='frame.png'
                        ),
                        caption=frame.get("text"),
                        parse_mode="HTML"
                    )
                )
            else:
                await bot.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=frame.get("text"),
                    parse_mode="HTML"
                )
        except Exception as e:
            await bot.database_interface.log_error(f"Ошибка при редактировании сообщения: {e}")

    @staticmethod
    async def on_game_started(bot, session):
        user_id = int(session["user_id"])
        game_id = int(session["game_id"])
        bet_amount = float(session["bet_amount"])
        started_at = session["started_at"]
        await bot.referral_manager.process_user_action(user_id, (await bot.bot.get_me()).username, "bet", bet_amount)
        await bot.database_interface.update_balance(user_id, -bet_amount,
                                                    "bet", f"Bet in game: {game_id}, started_at: {started_at}")

    @staticmethod
    async def on_game_finished(bot, result, session):
        from ..keyboards import KeyboardManager
        user_id = int(session["user_id"])
        game_id = int(session["game_id"])
        started_at = session["started_at"]
        user_data = await bot.database_interface.get_user(user_id)
        final_result = result.animations_data["final_result"]
        final_result_image = result.animations_data.get("final_result_image")
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
            await bot.referral_manager.process_user_action(user_id, (await bot.bot.get_me()).username,
                                                           "win", result.win_amount)
            try:
                channel_id = await bot.chat_id()
                if channel_id and result.win_amount > result.bet_amount:
                    if final_result_image:
                        await bot.bot.send_photo(channel_id,
                                                 BufferedInputFile(
                                                     file=final_result_image.getvalue(),
                                                     filename='image.png'
                                                 ),
                                                 caption=await bot.get_text(user_id, "GAME_WIN_ANNOUNCEMENT", user_data,
                                                                            custom_data),
                                                 reply_markup=KeyboardManager.get_channel_announcement_keyboard(
                                                     (await bot.bot.get_me()).username),
                                                 parse_mode="HTML")
                    else:
                        await bot.send_message(channel_id,
                                               await bot.get_text(user_id, "GAME_WIN_ANNOUNCEMENT", user_data,
                                                                  custom_data),
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
    async def change_language(bot, chat_id: int, message_id: int):
        from ..keyboards import KeyboardManager
        await bot.edit_message(chat_id, await bot.get_text(chat_id, "CHANGE_LANGUAGE"), message_id,
                               reply_markup=KeyboardManager.get_language_keyboard())

    @staticmethod
    async def change_game(bot, chat_id: int, user_data: dict[str, Any], message_id: int):
        from ..keyboards import KeyboardManager
        await bot.edit_message(chat_id, await bot.get_text(chat_id, "CHANGE_GAME", user_data), message_id,
                               reply_markup=KeyboardManager.get_change_game_keyboard(
                                   bot.game_manager.get_available_games(),
                                   user_data.get("language", "ru")))

    @staticmethod
    async def set_game(bot, chat_id: int, command: str, message_id: int):
        game_id = int(command[len("set-game:"):])
        await bot.database_interface.update_user(chat_id, selected_game=game_id)
        await bot.main_menu(chat_id, message_id)

    @staticmethod
    async def change_email(bot, callback_query: CallbackQuery):
        await bot.registration_menu(callback_query.message, first_message="CHANGE_EMAIL", ignore_db=True)

    @staticmethod
    async def language(bot, chat_id: int, command: str, message_id: int):
        language_code = command[len("language:"):]
        await bot.database_interface.update_user(chat_id, language=language_code)
        await bot.main_menu(chat_id, message_id)

    # ═══════════════════ Баланс ══════════════════
    @staticmethod
    async def balance(bot, chat_id: int, user_data: dict[str, Any], message_id: int):
        from ..keyboards import KeyboardManager
        await bot.edit_message(chat_id, await bot.get_text(chat_id, "BALANCE", user_data), message_id,
                               reply_markup=KeyboardManager.get_balance_keyboard(user_data.get("language", "en")))

    @staticmethod
    async def get_currency(bot, chat_id: int, user_data: dict[str, Any],
                           operation_type: str, available_currencies: list[str], callback_query: CallbackQuery):
        from ..keyboards import KeyboardManager
        currency_list = []
        if operation_type == "withdraw":
            balance_str = user_data.get("balance", "0").strip()
            try:
                balance_float = float(balance_str) if balance_str else 0.0
                if balance_float <= 0:
                    await callback_query.answer(
                        await bot.get_text(chat_id, "EMPTY_BALANCE_FOR_WITHDRAW", user_data),
                        True)
                    await bot.main_menu(chat_id, callback_query.message.message_id)
                    return
            except (ValueError, TypeError):
                await callback_query.answer(
                    await bot.get_text(chat_id, "EMPTY_BALANCE_FOR_WITHDRAW", user_data),
                    True)
                await bot.main_menu(chat_id, callback_query.message.message_id)
                return
        for asset in bot.crypto_pay.supported_assets:
            if asset.is_fiat:
                continue
            if asset.code not in available_currencies:
                continue
            currency_list.append({"code": asset.code, "name": asset.name})
        await bot.edit_message(
            chat_id,
            await bot.get_text(chat_id, "SELECT_CURRENCY", user_data),
            callback_query.message.message_id,
            reply_markup=KeyboardManager.get_currency_keyboard(
                user_data.get("language", "en"),
                currency_list,
                operation_type
            )
        )

    @staticmethod
    async def get_amount(bot, chat_id: int, user_data: dict[str, Any], currency: str, operation_type: str,
                         message_id: int):
        from ..keyboards import KeyboardManager
        markup = KeyboardManager.get_amount_keyboard(
            user_data.get("language", "en"), currency,
            operation_type, user_data.get("balance", "0.0"))
        await bot.edit_message(chat_id, await bot.get_text(chat_id, "SELECT_AMOUNT", user_data),
                               message_id, reply_markup=markup)

    @staticmethod
    async def do_deposit(bot, chat_id: int, user_data: dict[str, Any], currency: str, amount: float,
                         message_id: int):
        from ..keyboards import KeyboardManager
        deposit = await bot.crypto_pay.initiate_deposit(chat_id, amount, currency)
        if deposit["status"] == "payment_pending":
            await bot.edit_message(chat_id, await bot.get_text(chat_id, "PAYMENT_LINK", user_data), message_id,
                                   reply_markup=KeyboardManager.get_pay_keyboard(
                                       user_data.get("language", "en"), deposit, deposit["internal_tx_id"]))

    @staticmethod
    async def do_withdraw(bot, chat_id: int, user_data: dict[str, Any], currency: str, amount: float,
                          callback_query: CallbackQuery):
        withdraw = await bot.crypto_pay.initiate_withdrawal(chat_id, amount, currency)
        if withdraw:
            custom_data = {"amount": f"{amount:.8f}", "currency": currency}
            await bot.database_interface.update_balance(chat_id, -amount, "withdrawal")
            await callback_query.answer(await bot.get_text(chat_id, "WITHDRAW_SUCCESS", user_data, custom_data), True)
        else:
            await callback_query.answer(await bot.get_text(chat_id, "WITHDRAW_ERROR", user_data), True)
        await bot.main_menu(chat_id, callback_query.message.message_id)

    @staticmethod
    async def check_deposit(bot, chat_id: int, user_data: dict[str, Any], internal_tx_id: str,
                            callback_query: CallbackQuery, just_check: bool = False) -> bool | None:
        invoice = await bot.crypto_pay.get_invoice(internal_tx_id)
        if invoice.status == "paid":
            await callback_query.answer(await bot.get_text(chat_id, "DEPOSIT_SUCCESS", user_data))
            amount = float(invoice.amount) * float(invoice.paid_usd_rate)
            await bot.database_interface.update_balance(chat_id, amount, "deposit")
            await bot.main_menu(chat_id, callback_query.message.message_id)
            if just_check:
                return True
        else:
            if just_check:
                return False
            await callback_query.answer(await bot.get_text(chat_id, "DEPOSIT_FAILED", user_data))

    @staticmethod
    async def cancel_deposit_confirm(bot, chat_id: int, user_data: dict[str, Any],
                                     internal_tx_id: str, message_id: int):
        from ..keyboards import KeyboardManager
        await bot.send_message(chat_id, await bot.get_text(chat_id, "CANCEL_DEPOSIT_CONFIRM", user_data),
                               reply_markup=KeyboardManager.get_confirm_keyboard(
                                   f"cancel-deposit:{internal_tx_id}:{message_id}",
                                   user_data.get("language", "en")))

    @staticmethod
    async def cancel_deposit(bot, chat_id: int, user_data: dict[str, Any],
                             internal_tx_id: str, callback_query: CallbackQuery):
        if await bot.crypto_pay.cancel_deposit(internal_tx_id):
            await callback_query.answer(await bot.get_text(chat_id, "DEPOSIT_CANCELLED", user_data))
        else:
            await callback_query.answer(await bot.get_text(chat_id, "DEPOSIT_CANCEL_FAILED", user_data))
        await bot.main_menu(chat_id, callback_query.message.message_id)

    # ════════════════ Пользователь ═══════════════
    @staticmethod
    async def user(bot, chat_id: int, command: str):
        username = command[len("user:"):]
        user = await bot.database_interface.get_user_by_username(username)
        await HandlersManager.send_userinfo(bot, chat_id, user, profile=True)

    @staticmethod
    async def leaderboard(bot, chat_id: int, user_data: dict[str, Any]):
        """Отправляет таблицу лидеров с топ-10 игроков по выигрышам"""
        top_users = await bot.database_interface.get_top_users(limit=10)
        leaderboard_text = ""
        medals = ["🥇", "🥈", "🥉"]
        for position, user in enumerate(top_users, start=1):
            medal = medals[position - 1] if position <= 3 else f"{position}."
            username = (f"<a href='https://t.me/{(await bot.bot.get_me()).username}?"
                        f"start=user_{user.get("hashed_username")}'>{user.get("username")}</a>")
            custom_data = {"position": medal, "winnings": f"{float(user.get("winnings", 0.0)):.2f}",
                           "registered_at": user.get("registered_at", "None")}
            user_text = await bot.get_text(chat_id, "LEADERBOARD_USERINFO", user_data, custom_data)
            user_text = user_text.replace("username", username)
            user_text += f"\n{await HandlersManager.format_games_statistics(bot, chat_id, user, False)}"
            leaderboard_text += f"{user_text}\n\n"
        text = await bot.get_text(chat_id, "LEADERBOARD", user_data, {"leaderboard_text": leaderboard_text})
        await bot.send_message(chat_id, text)

    @staticmethod
    async def format_games_statistics(bot, chat_id: int, user_data: dict[str, Any], for_admin: bool) -> str:
        """
        Возвращает форматированный текст со статистикой игр пользователя:
        - Любимая игра
        - Всего игр и количество сыгранных раз по каждой
        """
        games_dict = await bot.database_interface.get_games_played(user_data["user_id"])
        if not games_dict:
            return await bot.get_text(chat_id, "USERINFO_NO_GAMES", custom_data=user_data)
        language = (await bot.database_interface.get_user(chat_id)).get("language", "en")
        favorite_game_id = max(games_dict, key=games_dict.get)
        favorite_game = await bot.game_manager.get_game(favorite_game_id)
        favorite_game_name = f"{favorite_game.icon} {favorite_game.name(language)}"
        favorite_play_times = games_dict[favorite_game_id]
        games_list = []
        for game_id, count in games_dict.items():
            game = await bot.game_manager.get_game(game_id)
            game_name = f"{game.icon} {game.name(language)}"
            game_text = await bot.get_text(chat_id, "USERINFO_GAMES_LIST", custom_data=user_data)
            game_text = game_text.replace("game_name", game_name).replace("count", str(count))
            games_list.append(game_text)
        response_text = await bot.get_text(chat_id, "USERINFO_FOFAVORITE_GAME", custom_data=user_data)
        response_text = (response_text.replace("favorite_game_name", favorite_game_name).
                         replace("favorite_play_times", str(favorite_play_times)))
        if for_admin:
            response_text += (f"\n{await bot.get_text(chat_id, "USERINFO_GAMES_LIST_TITLE", custom_data=user_data)}:\n"
                              + "\n".join(games_list))

        return response_text

    @staticmethod
    async def send_userinfo(bot, chat_id: int, user_data: dict[str, Any] = None,
                            for_admin: bool = False, profile: bool = False):
        from ..keyboards import KeyboardManager
        if user_data is None:
            user_data = await bot.database_interface.get_user(chat_id)
        tag = "USERINFO"
        if profile:
            tag = "PROFILE"
        elif for_admin:
            tag = "USERINFO_ADMIN"
        if user_data.get("user_id", chat_id) != chat_id:
            user_data["winnings"] = float(user_data["winnings"]) * 1.15
        user_data["winnings"] = f"{float(user_data["winnings"]):.2f}"
        user_date_recipient = await bot.database_interface.get_user(chat_id)
        userinfo = await bot.get_text(chat_id, tag, user_date_recipient, user_data)
        userinfo = userinfo.replace("username",
                                    f"<a href='https://t.me/{(await bot.bot.get_me()).username}?"
                                    f"start=user_{user_data['hashed_username']}'>{user_data['username']}</a>")
        userinfo += "\n" + await HandlersManager.format_games_statistics(bot, chat_id, user_data, for_admin)
        await bot.send_message(chat_id, userinfo, reply_markup=KeyboardManager.get_delete_keyboard())

    # ════════════════ Админ-панель ═══════════════
    @staticmethod
    async def admin_panel(bot, chat_id: int, user_data: dict[str, Any], message_id: int):
        from ..keyboards import KeyboardManager
        if chat_id not in bot.admin_ids:
            return
        await bot.edit_message(chat_id, await bot.get_text(chat_id, "ADMIN_PANEL", user_data), message_id,
                               reply_markup=KeyboardManager.get_admin_keyboard(user_data.get("language", "en")))

    @staticmethod
    async def admin_summary(bot, chat_id: int, user_data: dict[str, Any], message_id: int):
        from ..keyboards import KeyboardManager
        needed, count, avg_bal, max_bal, min_bal = await bot.database_interface.get_needed(bot.admin_ids)
        text = (
            f"{await bot.get_text(chat_id, "ADMIN_SUMMARY_COUNT", user_data)}: {count}\n"
            f"{await bot.get_text(chat_id, "ADMIN_SUMMARY_NEEDED", user_data)}: {int(needed)} $\n"
            f"{await bot.get_text(chat_id, "ADMIN_SUMMARY_AVG_BALANCE", user_data)}: {int(avg_bal)} $\n"
            f"{await bot.get_text(chat_id, "ADMIN_SUMMARY_MAX_BALANCE", user_data)}: {max_bal}\n"
            f"{await bot.get_text(chat_id, "ADMIN_SUMMARY_MIN_BALANCE", user_data)}: {min_bal}"
        )
        await bot.edit_message(chat_id, text, message_id,
                               reply_markup=KeyboardManager.get_back_keyboard(
                                   user_data.get("language", "en"),
                                   callback_data="admin-panel"))

    @staticmethod
    async def admin_list_players(bot, chat_id: int, command: str, user_data: dict[str, Any], message_id: int):
        from ..keyboards import KeyboardManager
        page = int(command.split(':')[1]) if ':' in command else 1
        text, lines, add_next_page = await bot.get_users_page(page)
        await bot.edit_message(chat_id, text, message_id,
                               reply_markup=KeyboardManager.get_users_keyboard(
                                   user_data.get("language", "en"), lines, page, add_next_page))

    @staticmethod
    async def admin_show_logs(bot, chat_id: int, command: str, user_data: dict[str, Any], message_id: int):
        from ..keyboards import KeyboardManager
        page = int(command.split(':')[1]) if ':' in command else 1
        text, add_next_page = await bot.get_logs_page(page)
        await bot.edit_message(chat_id, text, message_id,
                               reply_markup=KeyboardManager.get_logs_keyboard(
                                   user_data.get("language", "en"), page, add_next_page))

    @staticmethod
    async def admin_show_tables(bot, chat_id: int, user_data: dict[str, Any], message_id: int):
        from ..keyboards import KeyboardManager
        ok, tables = await bot.database_interface.get_tables()
        if not ok:
            await bot.edit_message(chat_id, tables[0], message_id,
                                   reply_markup=KeyboardManager.get_back_keyboard(
                                       user_data.get("language", "en"),
                                       callback_data="admin-panel"))
            return
        await bot.edit_message(chat_id, await bot.get_text(chat_id, "ADMIN_TABLES_LIST", user_data), message_id,
                               reply_markup=KeyboardManager.get_tables_keyboard(
                                   tables, user_data.get("language", "en")))

    @staticmethod
    async def admin_show_table(bot, chat_id: int, table: str, user_data: dict[str, Any], message_id: int):
        bd = await bot.database_interface.display_table(table)
        for row in bd:
            await bot.send_message(chat_id, row)
        await HandlersManager.admin_panel(bot, chat_id, user_data, message_id)

    @staticmethod
    async def admin_issue_balance(bot, chat_id: int, user_data: dict[str, Any], callback_query: CallbackQuery):
        await bot.database_interface.set_balance(chat_id, 1000)
        await callback_query.answer(await bot.get_text(chat_id, "ADMIN_BALANCE_ISSUED", user_data))

    @staticmethod
    async def admin_reset_balance(bot, chat_id: int, user_data: dict[str, Any], callback_query: CallbackQuery):
        await bot.database_interface.reset_balance(chat_id)
        await callback_query.answer(await bot.get_text(chat_id, "ADMIN_BALANCE_RESET", user_data))

    @staticmethod
    async def admin_get_balance(bot, chat_id: int):
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

        total = await bot.crypto_pay.get_total_balance_usd()
        await bot.send_message(chat_id, format_balance(balance_data) + f"\n\n<b>Всего: {total:.2f}$</b>")

    @staticmethod
    async def admin_game_settings_handler(bot, chat_id: int, user_data: dict[str, Any], command, message_id: int):
        command_parts = command.split(':')
        if len(command_parts) > 2:
            game_id = int(command_parts[1])
            game_config = command_parts[2]
            await bot.database_interface.update_config(game_id, game_config)
            await HandlersManager.admin_panel(bot, chat_id, user_data, message_id)
            return
        if len(command_parts) > 1:
            game_id = int(command_parts[1])
            await HandlersManager.admin_game_settings(bot, chat_id, user_data, message_id, game_id)
            return
        await HandlersManager.admin_game_settings(bot, chat_id, user_data, message_id)

    @staticmethod
    async def admin_game_settings(bot, chat_id: int, user_data: dict[str, Any], message_id: int, game_id: int = None):
        from ..keyboards import KeyboardManager
        language_code = user_data.get("language", "en")
        if game_id is None:
            await bot.edit_message(chat_id, await bot.get_text(chat_id, "GAME_SETTINGS", user_data), message_id,
                                   reply_markup=KeyboardManager.get_games_keyboard(
                                       "admin-game-settings", bot.game_manager.get_available_games(), language_code))
            return
        game = await bot.game_manager.get_game(game_id)
        game_configs = bot.GameConfigs[game_id]
        game_name_text = await bot.get_text(chat_id, "GAME_INFO", user_data,
                                            {"game_icon": game.icon, "game_name": game.name(language_code)})
        await bot.edit_message(chat_id, game_name_text, message_id,
                               reply_markup=KeyboardManager.get_game_configs_keyboard(
                                   game_id, game_configs, language_code))

    @staticmethod
    async def admin_game_config_handler(bot, chat_id: int, user_data: dict[str, Any], command, message_id: int):
        command_parts = command.split(':')
        if len(command_parts) > 1:
            game_id = int(command_parts[1])
            await HandlersManager.admin_game_config(bot, chat_id, user_data, message_id, game_id)
            return
        await HandlersManager.admin_game_config(bot, chat_id, user_data, message_id)

    @staticmethod
    async def admin_game_config(bot, chat_id: int, user_data: dict[str, Any], message_id: int, game_id: int = None):
        from ..keyboards import KeyboardManager
        language_code = user_data.get("language", "en")
        if game_id is None:
            await bot.edit_message(chat_id, await bot.get_text(chat_id, "GAME_CONFIG_SELECT", user_data), message_id,
                                   reply_markup=KeyboardManager.get_games_keyboard(
                                       "admin-game-config", bot.game_manager.get_available_games(), language_code))
            return
        game = await bot.game_manager.get_game(game_id)
        await bot.send_message(chat_id, game.get_config_info())
        await HandlersManager.admin_panel(bot, chat_id, user_data, message_id)

    @staticmethod
    async def admin_bot_config(bot, chat_id: int, user_data: dict[str, Any], command: str, message_id: int):
        from ..keyboards import KeyboardManager
        language_code = user_data.get("language", "en")
        command_parts = command.split(':')
        if len(command_parts) > 1:
            if command_parts[1] == "set_channel":
                await bot.database_interface.update_user(chat_id, block_input=True, input_type=20)
                await bot.edit_message(chat_id, await bot.get_text(chat_id, "BOT_CONFIG_ENTER_ID", user_data),
                                       message_id)
            elif command_parts[1] == "set_news":
                await bot.database_interface.update_user(chat_id, block_input=True, input_type=21)
                await bot.edit_message(chat_id, await bot.get_text(chat_id, "BOT_CONFIG_ENTER_ID", user_data),
                                       message_id)
            else:
                await bot.database_interface.clear_bot_config(bot.bot.id)
                await HandlersManager.admin_panel(bot, chat_id, user_data, message_id)
            return
        bot_config = await bot.bot_config()
        if bot_config:
            channel_username = bot_config.get("chat_username", "")
            channel_display = f"@{channel_username}" if channel_username else "❌ Не подключён"
            news_channel_username = bot_config.get("news_channel_username", "")
            news_channel_display = f"@{news_channel_username}" if news_channel_username else "❌ Не подключён"
        else:
            channel_display = "❌ Не подключён"
            news_channel_display = "❌ Не подключён"
        custom_data = {"channel_username": channel_display, "news_channel_username": news_channel_display}
        await bot.edit_message(chat_id, await bot.get_text(chat_id, "BOT_CONFIG", user_data, custom_data), message_id,
                               reply_markup=KeyboardManager.get_bot_config(language_code))

    @staticmethod
    async def update_max_bet(bot, chat_id: int, user_data: dict[str, Any], callback_query: CallbackQuery):
        max_bet = await bot.database_interface.set_max_bet(await bot.crypto_pay.get_total_balance_usd())
        custom_data = {"max_bet": max_bet}
        await callback_query.answer(await bot.get_text(chat_id, "MAX_BET_CONFIG", user_data, custom_data), True)

    @staticmethod
    async def channel_message_menu(bot, chat_id: int, user_data: dict[str, Any], command: str, message_id: int):
        from ..keyboards import KeyboardManager
        command_parts = command.split(':')
        if len(command_parts) > 1:
            if command_parts[1] == "startup":
                await HandlersManager.send_startup_channel_message(bot, chat_id, user_data, message_id)
            else:
                await HandlersManager.get_custom_message(bot, chat_id, user_data, 0)
            return
        await bot.edit_message(chat_id, await bot.get_text(chat_id, "SEND_MESSAGE_TYPE_CHOICE", user_data), message_id,
                               reply_markup=KeyboardManager.get_news_keyboard(user_data.get("language", "en")))

    @staticmethod
    async def create_leaderboard(bot, chat_id: int, user_data: dict[str, Any], callback_query: CallbackQuery):
        await bot.database_interface.create_leaderboard()
        await callback_query.answer(await bot.get_text(chat_id, "LEADERBOARD_CREATED", user_data))

    @staticmethod
    async def profits(bot, chat_id: int, user_data: dict[str, Any], message_id: int):
        from ..utils.plt import PLT
        from ..keyboards import KeyboardManager
        profit_withdrawals = await bot.database_interface.get_profit_withdrawals()
        total = await bot.crypto_pay.get_total_balance_usd()
        profit = total - config.START_BALANCE
        custom_data = {"total": total, "profit": profit}
        await bot.edit_message(chat_id,
                               await bot.get_text(chat_id, "PROFITS", user_data, custom_data),
                               message_id,
                               image=PLT.build_profit_chart(profit_withdrawals),
                               reply_markup=KeyboardManager.get_profit_withdrawal_keyboards(
                                   user_data.get("language", "en")))

    @staticmethod
    async def withdrawal_profits(bot, chat_id: int, user_data: dict[str, Any], message_id: int):
        total = await bot.crypto_pay.get_total_balance_usd()
        profit = total - config.START_BALANCE
        await bot.database_interface.add_profit_withdrawal(str(total), str(profit), str(total - profit))
        await bot.crypto_pay.initiate_withdrawal_profits(config.START_BALANCE)
        await HandlersManager.admin_panel(bot, chat_id, user_data, message_id)

    @staticmethod
    async def send_startup_channel_message(bot, chat_id: int, user_data: dict[str, Any], message_id: int):
        from ..keyboards import KeyboardManager
        russian_message = """
🇷🇺
<b>🎰 Добро пожаловать в Plaza Casino!</b>

<b>💎 ОБ ИГРЕ</b>
Честное казино с прозрачными правилами и равными вероятностями. 
Каждая ставка рассчитывается справедливо и честно.

<b>💰 КАК НАЧАТЬ</b>
1️⃣ Откройте бота
2️⃣ Выберите игру
3️⃣ Пополните баланс
4️⃣ Делайте ставки и выигрывайте!

<b>🛡️ НАДЁЖНОСТЬ</b>
✅ Защищённые платежи
✅ Мгновенные выплаты
✅ Поддержка 24/7

<b>🍀 Удачи в игре!</b>
"""
        english_message = """
🇺🇸
<b>🎰 Welcome to Plaza Casino!</b>

<b>💎 ABOUT THE GAME</b>
Fair casino with transparent rules and equal odds. 
Every bet is calculated fairly and honestly.

<b>💰 HOW TO START</b>
1️⃣ Open the bot
2️⃣ Select a game
3️⃣ Top up your balance
4️⃣ Place bets and win!

<b>🛡️ RELIABILITY</b>
✅ Secure payments
✅ Instant payouts
✅ 24/7 support

<b>🍀 Good luck!</b>
"""
        full_message = f"{russian_message}\n\n{english_message}"
        await HandlersManager.send_news_message(bot,
                                                chat_id,
                                                full_message,
                                                KeyboardManager.get_channel_startup_keyboard(
                                                    (await bot.bot.get_me()).username, config.SUPPORT_BOT),
                                                user_data,
                                                message_id, True)

    @staticmethod
    async def custom_message_cancel(bot, chat_id: int, user_data: dict[str, Any], message_id: int):
        await bot.bot.delete_message(chat_id, message_id)
        if user_data.get("input_type", 0) == 0:
            return
        await bot.database_interface.update_user(chat_id, block_input=False, input_type=0)
        await bot.send_message(chat_id, await bot.get_text(chat_id, "CUSTOM_MESSAGE_CANCELLED", user_data))
        await bot.main_menu(chat_id)

    @staticmethod
    async def get_custom_message(bot, chat_id: int, user_data: dict[str, Any], stage: int,
                                 message: str = None, markup: Any = None):
        from ..keyboards import KeyboardManager
        if stage == 0:
            await bot.database_interface.update_user(chat_id, block_input=True, input_type=30)
            await bot.send_message(chat_id, await bot.get_text(chat_id, "ENTER_MESSAGE_TEXT", user_data),
                                   reply_markup=KeyboardManager.get_custom_message_cancel(
                                       user_data.get("language", "en")))
        elif stage == 1:
            await bot.database_interface.update_user(chat_id, input_type=31)
            await bot.send_message(chat_id, await bot.get_text(chat_id, "ENTER_MESSAGE_BUTTONS", user_data),
                                   reply_markup=KeyboardManager.get_custom_message_cancel(
                                       user_data.get("language", "en")))
        else:
            await bot.database_interface.update_user(chat_id, block_input=False, input_type=0)
            await bot.send_message(chat_id, message, reply_markup=markup)

    @staticmethod
    async def translate_text(ru_message_text: str):
        from googletrans import Translator
        translator = Translator()
        return (await translator.translate(ru_message_text, src='ru', dest='en')).text

    @staticmethod
    async def send_custom_message(bot, chat_id, user_data, message: Message):
        from ..keyboards import KeyboardManager
        ru_message_text = message.html_text if message.text else message.html_caption
        en_message_text = await HandlersManager.translate_text(ru_message_text)
        message_markup = KeyboardManager.remove_control_buttons(message)
        message_text = f"🇷🇺\n{ru_message_text}\n\n\n🇺🇸\n{en_message_text}"
        await HandlersManager.send_news_message(bot, chat_id, message_text,
                                                message_markup, user_data, message.message_id)

    @staticmethod
    async def send_news_message(bot, chat_id: int, text: str, reply_markup: Any,
                                user_data: dict[str, Any], message_id: int, need_pin: bool = False):
        try:
            bot_config = await bot.database_interface.get_bot_config((await bot.bot.get_me()).id)
            if bot_config:
                news_chat_id = bot_config.get("news_chat_id")
                if news_chat_id:
                    sent_message = await bot.send_message(
                        news_chat_id,
                        text,
                        parse_mode="HTML",
                        disable_web_page_preview=True,
                        reply_markup=reply_markup
                    )
                    if need_pin:
                        await bot.bot.pin_chat_message(
                            chat_id=news_chat_id,
                            message_id=sent_message.message_id,
                            disable_notification=True
                        )
                    await bot.send_message(chat_id, await bot.get_text(chat_id, "NEWS_CHANNEL_SEND_SUCCESS",
                                                                       user_data))
                    await bot.database_interface.log_info(f"✅ Сообщение отправлено в канал {news_chat_id}")
                else:
                    await bot.send_message(chat_id, await bot.get_text(chat_id, "NEWS_CHANNEL_NOT_CONNECTED"))
            else:
                await bot.send_message(chat_id, await bot.get_text(chat_id, "NEWS_CHANNEL_NOT_CONNECTED", user_data))
            await HandlersManager.admin_panel(bot, chat_id, user_data, message_id)
        except Exception as e:
            await bot.send_message(chat_id, await bot.get_text(chat_id, "NEWS_CHANNEL_SEND_ERROR", user_data))
            await bot.database_interface.log_error(f"❌ Ошибка при отправке сообщения: {str(e)}")

    @staticmethod
    async def admin_user(bot, chat_id: int, command: str, user_data: dict[str, Any], message_id: int):
        username = command[len("admin-user:"):]
        await HandlersManager.send_userinfo(bot, chat_id,
                                            await bot.database_interface.get_user_by_username(username), True)
        await HandlersManager.admin_panel(bot, chat_id, user_data, message_id)

    @staticmethod
    async def rules(bot, chat_id: int, user_data: dict[str, Any], message_id: int):
        from ..keyboards import KeyboardManager
        game = await bot.game_manager.get_game(int(user_data.get("selected_game", 0)))
        await bot.edit_message(chat_id, game.rules(user_data.get("language", "en")), message_id,
                               reply_markup=KeyboardManager.get_back_keyboard(user_data.get("language", "en")))

    @staticmethod
    async def giveaway(bot, chat_id: int, user_data: dict[str, Any], command: str, message_id: int):
        from aiocryptopay.models.check import Check
        from ..keyboards import KeyboardManager
        bot_config = await bot.database_interface.get_bot_config((await bot.bot.get_me()).id)
        if len(command.split(':')) == 1:
            await bot.edit_message(chat_id, await bot.get_text(chat_id, "CHOICE_OF_DRAW", user_data), message_id,
                                   reply_markup=KeyboardManager.get_giveaway_keyboard(user_data.get("language", "en")))
            return
        if bot_config:
            news_chat_id = bot_config.get("news_chat_id")
            if news_chat_id:
                try:
                    quantity, amount = int(command.split(':')[1]), float(command.split(':')[2])
                    ru_text = f"""
<b>🎁 Розыгрыш</b>

<b>💰 Всего в розыгрыше:</b>
• Количество чеков: {quantity}
• Сумма за чек: {amount} USDT
• Общая сумма: {quantity * amount} USDT

<b>🎉 Как участвовать:</b>
1️⃣ Нажмите на любую кнопку ниже
2️⃣ Каждый чек можно использовать только один раз

<b>⏱️ Поспешите!</b> Призы распределяются быстро. 🔥
"""
                    en_text = f"""
<b>🎁 Giveaway</b>

<b>💰 Total in giveaway:</b>
• Number of checks: {quantity}
• Amount per check: {amount} USDT
• Total amount: {quantity * amount} USDT

<b>🎉 How to participate:</b>
1️⃣ Click on any button below
2️⃣ Each check can only be used once

<b>⏱️ Hurry up!</b> Prizes are distributed quickly. 🔥
"""
                    message_text = f"🇷🇺{ru_text}\n\n\n🇺🇸{en_text}"
                    giveaways: list[Check] = await bot.crypto_pay.create_giveaway(quantity, amount)
                    giveaways_buttons = "|".join(f"{g.amount};{g.bot_check_url}" for g in giveaways) + "|"
                    markup = KeyboardManager.build_giveaways_keyboard(giveaways_buttons)
                    await HandlersManager.send_news_message(bot, chat_id, message_text, markup, user_data, message_id)
                except Exception:
                    await bot.send_message(chat_id, await bot.get_text(chat_id, "ERROR_CREATE_GIVEAWAY", user_data))
            else:
                await bot.send_message(chat_id, await bot.get_text(chat_id, "NEWS_CHANNEL_NOT_CONNECTED"))
