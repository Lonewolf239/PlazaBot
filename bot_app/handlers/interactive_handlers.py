from aiogram import types
from aiogram.types import InlineKeyboardMarkup, BufferedInputFile
from bot_app.keyboards import KeyboardManager
from bot_app.games.base_game import GameResult, GameStatus
from bot_app.handlers import HandlersManager


class InteractiveGameHandlers:
    """Обработчики для интерактивных игр"""
    @staticmethod
    async def handle_game_action(bot, callback_query: types.CallbackQuery, action: str):
        """Обработать действие в интерактивной игре"""
        chat_id = callback_query.from_user.id
        message_id = callback_query.message.message_id
        user_data = await bot.database_interface.get_user(chat_id)
        parts = action.split(':')
        game_type = parts[0]
        game_action = parts[1] if len(parts) > 1 else None
        user_session = bot.game_manager.get_user_session(chat_id)
        if not user_session:
            await callback_query.answer(
                await bot.get_text(chat_id, "INTERACTIVE_GAME_NOT_FOUND", user_data), show_alert=True)
            await bot.bot.delete_message(chat_id, message_id)
            return
        game_id = user_session.get('game_id')
        game = await bot.game_manager.get_game(game_id)
        game.set_game_id(game_id)
        try:
            result = await game.process_action(bot, chat_id, game_action)
            if result.get('error'):
                await callback_query.answer(result['error'], show_alert=True)
                return
            is_game_over = result.get('game_over') or await game.is_game_over(bot, chat_id)
            if is_game_over:
                game_result = await InteractiveGameHandlers._create_game_result(bot, chat_id, game, user_session)
                final_message = await game.get_final_result_message(bot, chat_id)
                try:
                    image = final_message.get("image")
                    if image:
                        await bot.bot.delete_message(chat_id, message_id)
                        await bot.bot.send_photo(chat_id,
                                                 BufferedInputFile(
                                                     file=image.getvalue(),
                                                     filename='image.png'
                                                 ),
                                                 caption=final_message["text"],
                                                 reply_markup=InlineKeyboardMarkup(inline_keyboard=[]),
                                                 parse_mode="HTML")
                    else:
                        await bot.bot.edit_message_text(
                            chat_id=chat_id,
                            message_id=message_id,
                            text=final_message["text"],
                            reply_markup=InlineKeyboardMarkup(inline_keyboard=[]),
                            parse_mode="HTML")
                except Exception as e:
                    bot.logger.error(f"Ошибка при финальном редактировании: {e}")
                await HandlersManager.on_game_finished(bot, game_result, user_session)
                bot.game_manager.delete_interactive_session(chat_id, game_id)
                bot.game_manager.active_sessions.pop(chat_id, None)
                await callback_query.answer()
                return
            round_state = await game.get_round_state(bot, chat_id)
            game_session = game.get_session(bot, chat_id)
            keyboard = await KeyboardManager.get_interactive_game_keyboard(game_type,
                                                                           user_data.get("language", "en"),
                                                                           game_session)
            try:
                await bot.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=round_state,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
            except Exception as e:
                bot.logger.error(f"Ошибка при редактировании: {e}")
            await callback_query.answer()
        except Exception as e:
            bot.logger.error(f"Ошибка в игре: {e}", exc_info=True)
            await callback_query.answer(
                await bot.get_text(chat_id, "ERROR_IN_MOVE", user_data), show_alert=True)
            await bot.bot.delete_message(chat_id, message_id)

    @staticmethod
    async def _create_game_result(bot, chat_id: int, game, user_session) -> GameResult:
        """Создать финальный результат игры"""
        win_amount, multiplier = await game.get_game_result(bot, chat_id)
        bet_amount = user_session['bet_amount']
        is_win = win_amount > bet_amount
        game_final_result = await game.get_final_result_message(bot, chat_id)
        game_icon = game.icon
        animations_data = {
            "final_result": game_final_result["text"],
            "final_result_image": game_final_result.get("image"),
            "icon": game_icon,
            "multiplier": multiplier
        }
        user_bet = user_session.get('bet_data', None)
        game_data = await game.get_game_data(None, user_session.get('bet_data'))
        result = GameResult(
            status=GameStatus.FINISHED,
            win_amount=win_amount,
            bet_amount=bet_amount,
            user_bet=user_bet,
            multiplier=multiplier,
            is_win=is_win,
            game_data=game_data,
            animations_data=animations_data,
            bet_data=user_session.get('bet_data')
        )
        return result
