from typing import Any

from bot_app.keyboards import KeyboardManager


class ReferralHandler:
    """Обработчик команд рефералки"""
    @staticmethod
    async def referral_menu(bot, chat_id: int, user_data: dict):
        """Главное меню рефералки"""
        language = user_data.get("language", "en")
        text = await bot.get_text(chat_id, "REFERRAL_MENU", user_data)
        await bot.send_message(
            chat_id,
            text,
            reply_markup=KeyboardManager.get_referral_keyboard(language)
        )

    @staticmethod
    async def referral_cancel(bot, chat_id: int):
        await bot.database_interface.update_user(chat_id, block_input=False, input_type=0)
        await bot.main_menu(chat_id)

    @staticmethod
    async def create_clone_bot(bot, chat_id: int, user_data: dict[str, Any]):
        """Начинает процесс создания клон-бота"""
        text = await bot.get_text(chat_id, "REFERRAL_CLONE_BOT_STEP1", user_data)
        await bot.database_interface.update_user(chat_id, block_input=True, input_type=10)
        await bot.send_message(chat_id, text,
                               reply_markup=KeyboardManager.get_referral_cancel_keyboard(
                                   user_data.get("language", "en")))

    @staticmethod
    async def process_token_input(bot, chat_id: int, token: str):
        """
        Обрабатывает введенный токен
        :param bot: BotInterface
        :param chat_id: ID пользователя
        :param token: Токен бота
        """
        test_bot = None
        try:
            from aiogram import Bot
            user_data = await bot.database_interface.get_user(chat_id)
            test_bot = Bot(token)
            try:
                bot_info = await test_bot.get_me()
                if not bot_info:
                    text = await bot.get_text(chat_id, "REFERRAL_INVALID_TOKEN", user_data)
                    await bot.send_message(chat_id, text)
                    return False
                bot_id = await bot.referral_manager.create_clone_bot(chat_id, token)
                if not bot_id:
                    text = await bot.get_text(chat_id, "REFERRAL_BOT_CREATION_ERROR", user_data)
                    await bot.send_message(chat_id, text)
                    return False
                ref_link = await bot.referral_manager.get_referral_link(chat_id, bot_id)
                text = await bot.get_text(chat_id, "REFERRAL_CLONE_BOT_SUCCESS",
                                          custom_data={'bot_name': f'@{bot_info.username}', 'ref_link': ref_link})
                await bot.database_interface.update_user(chat_id, block_input=False, input_type=0)
                await bot.send_message(chat_id, text)
                from aiogram import Dispatcher
                from main import register_bot_handlers
                clone_dp = Dispatcher()
                clone_bot_interface = type(bot)(
                    bot.database_interface,
                    token,
                    bot.admin_ids,
                    bot.logger
                )
                clone_bot_interface.initialize(bot.crypto_pay)
                clone_bot_interface.referral_manager = bot.referral_manager
                register_bot_handlers(clone_dp, clone_bot_interface)
                await bot.referral_manager.start_clone_bot(bot_id, clone_dp)
                bot.logger.info(f"Клон-бот {bot_id} запущен немедленно")
                await bot.main_menu(chat_id)
                return True
            finally:
                if test_bot is not None:
                    try:
                        await test_bot.session.close()
                    except Exception as e:
                        bot.logger.error(f"Ошибка при закрытии сессии test_bot: {e}")
        except Exception as e:
            user_data = await bot.database_interface.get_user(chat_id)
            bot.logger.error(f"Ошибка при обработке токена: {e}")
            text = await bot.get_text(chat_id, "REFERRAL_BOT_CREATION_ERROR", user_data)
            await bot.send_message(chat_id, text)
            return False
        finally:
            if test_bot is not None:
                try:
                    await test_bot.session.close()
                except Exception as e:
                    bot.logger.error(f"Ошибка при закрытии test_bot в finally: {e}")

    @staticmethod
    async def my_referrals(bot, chat_id: int, user_data: dict[str, Any]):
        """Показывает статистику рефералов"""
        stats = await bot.database_interface.fetch_one(
            """SELECT
            COUNT(*) as total_refs,
            SUM(CASE WHEN reward_given = 1 THEN 1 ELSE 0 END) as rewarded
            FROM referrals
            WHERE referrer_user_id = ?""",
            (chat_id,)
        )
        text = await bot.get_text(chat_id, "REFERRAL_MY_REFERRALS", user_data, custom_data=stats)
        await bot.send_message(chat_id, text)
        await bot.main_menu(chat_id)
