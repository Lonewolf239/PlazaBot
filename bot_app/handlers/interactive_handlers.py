from aiogram import types
from bot_app.keyboards import KeyboardManager
from aiogram.utils.keyboard import InlineKeyboardBuilder


class InteractiveGameHandlers:
    """Обработчики для интерактивных игр"""
    @staticmethod
    async def handle_game_action(bot, callback_query: types.CallbackQuery, action: str):
        """
        Обработать действие в интерактивной игре.

        action: "hi_lo:high", "hi_lo:low", "blackjack:hit", etc.
        """
        chat_id = callback_query.from_user.id
        message_id = callback_query.message.message_id
        parts = action.split(':')
        game_type = parts[0]
        game_action = parts[1] if len(parts) > 1 else None
        user_session = bot.game_manager.get_user_session(chat_id)
        if not user_session:
            await callback_query.answer("❌ Игра не найдена", show_alert=True)
            return
        game_id = user_session.get('game_id')
        game = await bot.game_manager.get_game(game_id)
        if not hasattr(game, 'process_action'):
            await callback_query.answer("❌ Эта игра не интерактивная", show_alert=True)
            return
        try:
            result = await game.process_action(chat_id, game_action)
            if result.get('error'):
                await callback_query.answer(result['error'], show_alert=True)
                return
            round_state = await game.get_round_state(chat_id)
            keyboard = await InteractiveGameHandlers._get_game_keyboard(game, chat_id, game_type)
            await bot.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=round_state,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            if await game.is_game_over(chat_id):
                await InteractiveGameHandlers._finish_game(bot, chat_id, message_id, game)
            await callback_query.answer()
        except Exception as e:
            bot.logger.error(f"Error in game action: {e}")
            await callback_query.answer("❌ Ошибка обработки хода", show_alert=True)

    @staticmethod
    async def _get_game_keyboard(game, user_id: int, game_type: str):
        """Получить клавиатуру для интерактивной игры"""
        kb = InlineKeyboardBuilder()
        if game_type == "hi_lo":
            kb.button(text="📈 Выше", callback_data="game_action:hi_lo:high")
            kb.button(text="📉 Ниже", callback_data="game_action:hi_lo:low")
            kb.button(text="🛑 Завершить", callback_data="game_action:hi_lo:stop")
            kb.adjust(2, 1)
        elif game_type == "blackjack":
            kb.button(text="🎴 Hit", callback_data="game_action:blackjack:hit")
            kb.button(text="⏸️ Stand", callback_data="game_action:blackjack:stand")
            kb.button(text="🛑 Сдаться", callback_data="game_action:blackjack:surrender")
            kb.adjust(2, 1)
        return kb.as_markup()

    @staticmethod
    async def _finish_game(bot, chat_id: int, message_id: int, game):
        """Завершить интерактивную игру"""
        win_amount, multiplier = await game.get_game_result(chat_id)
        user_session = bot.game_manager.get_user_session(chat_id)
        bet_amount = user_session['bet_amount']
        user_data = await bot.database_interface.get_user(chat_id)
        is_win = win_amount > 0
        custom_data = {
            "amount": f"{win_amount:.2f}",
            "bet": str(bet_amount),
            "multiplier": f"{multiplier:.2f}x"
        }
        if is_win:
            await bot.database_interface.update_balance(
                chat_id, win_amount, "win",
                f"Interactive game finished: multiplier {multiplier}x"
            )
            await bot.send_message(
                chat_id,
                await bot.get_text(chat_id, "GAME_WIN", user_data, custom_data),
                reply_markup=KeyboardManager.get_game_again_keyboard(
                    user_data.get("language", "en")
                )
            )
        else:
            await bot.send_message(
                chat_id,
                await bot.get_text(chat_id, "GAME_LOSE", user_data, custom_data),
                reply_markup=KeyboardManager.get_game_again_keyboard(
                    user_data.get("language", "en")
                )
            )
        game.delete_session(chat_id)
