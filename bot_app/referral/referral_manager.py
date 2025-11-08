import logging
from aiogram import Bot, Dispatcher
from typing import Optional, Dict
import asyncio
from bot_app.database.db_manager import DatabaseInterface

from bot_app.utils import Hacher


class ReferralManager:
    """Управляет созданием и работой клон-ботов"""
    def __init__(self, db: DatabaseInterface, main_bot_token: str, logger: logging.Logger):
        self.db = db
        self.main_bot_token = main_bot_token
        self.logger = logger
        self.active_bots: Dict[str, Bot] = {}
        self.ref_code_mapping: Dict[str, int] = {}
        self.clone_tasks: Dict[str, asyncio.Task] = {}

    async def create_clone_bot(self, creator_user_id: int, token: str) -> Optional[str]:
        """Создает запись о клон-боте и регистрирует его в clone_bot_instances"""
        bot = None
        main_bot = None
        try:
            bot = Bot(token)
            bot_info = await bot.get_me()
            bot_username = bot_info.username

            if not bot_username:
                self.logger.error("Бот не имеет username")
                return None

            existing = await self.db.fetch_one(
                "SELECT * FROM bot_instances WHERE bot_id = ?",
                (bot_username,)
            )

            if existing:
                self.logger.warning(f"Бот {bot_username} уже существует")
                return None

            main_bot = Bot(self.main_bot_token)
            main_bot_info = await main_bot.get_me()
            main_bot_id = main_bot_info.username

            await self.db.execute(
                """INSERT INTO bot_instances
                (bot_id, parent_bot_id, creator_user_id, token)
                VALUES (?, ?, ?, ?)""",
                (bot_username, main_bot_id, creator_user_id, token)
            )

            await self.db.register_clone_bot(bot_username, creator_user_id)

            ref_code = Hacher.hash(str(creator_user_id), False)
            self.ref_code_mapping[ref_code] = creator_user_id
            await self.db.execute(
                "UPDATE users SET ref_code = ? WHERE user_id = ?",
                (ref_code, creator_user_id)
            )

            self.logger.info(f"Создан клон-бот {bot_username} для пользователя {creator_user_id}")
            await self.copy_bot_commands(self.logger, main_bot, bot)
            self.active_bots[bot_username] = bot
            bot = None
            return bot_username

        except Exception as e:
            self.logger.error(f"Ошибка при создании клон-бота: {e}")
            return None
        finally:
            if bot is not None:
                try:
                    await bot.session.close()
                except Exception as e:
                    self.logger.error(f"Ошибка при закрытии сессии тестового бота: {e}")

            if main_bot is not None:
                try:
                    await main_bot.session.close()
                except Exception as e:
                    self.logger.error(f"Ошибка при закрытии сессии главного бота: {e}")

    @staticmethod
    async def copy_bot_commands(logger: logging.Logger, source_bot: Bot, target_bot: Bot):
        """Копирует меню команд с одного бота на другой"""
        try:
            source_commands = await source_bot.get_my_commands()
            if source_commands:
                await target_bot.set_my_commands(source_commands)
                logger.info(f"Команды успешно скопированы на клон-бота. Всего команд: {len(source_commands)}")
            else:
                logger.warning("У оригинального бота не найдено команд")
        except Exception as e:
            logger.error(f"Ошибка при копировании команд: {e}")

    async def start_clone_bot(self, bot_id: str, dispatcher: Dispatcher):
        """
        НОВОЕ: Запускает клон-бота в отдельном таске
        :param bot_id: ID клон-бота
        :param dispatcher: Dispatcher для этого бота
        """
        try:
            if bot_id not in self.active_bots:
                self.logger.error(f"Бот {bot_id} не найден в active_bots")
                return

            bot = self.active_bots[bot_id]
            task = asyncio.create_task(dispatcher.start_polling(bot))
            self.clone_tasks[bot_id] = task
            self.logger.info(f"Запущен клон-бот {bot_id}")

        except Exception as e:
            self.logger.error(f"Ошибка при запуске клон-бота {bot_id}: {e}")

    async def stop_clone_bot(self, bot_id: str):
        """
        НОВОЕ: Останавливает клон-бота
        :param bot_id: ID клон-бота
        """
        if bot_id in self.clone_tasks:
            task = self.clone_tasks[bot_id]
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            del self.clone_tasks[bot_id]
            self.logger.info(f"Остановлен клон-бот {bot_id}")
        if bot_id in self.active_bots:
            try:
                await self.active_bots[bot_id].session.close()
                del self.active_bots[bot_id]
            except Exception as e:
                self.logger.error(f"Ошибка при закрытии сессии {bot_id}: {e}")

    async def get_bot_creator(self, bot_id: str) -> Optional[int]:
        """
        Получает user_id создателя бота
        :param bot_id: username бота
        :return: user_id создателя или None
        """
        bot_record = await self.db.fetch_one(
            "SELECT creator_user_id FROM bot_instances WHERE bot_id = ?",
            (bot_id,)
        )
        return bot_record.get("creator_user_id") if bot_record else None

    async def process_user_action(self, user_id: int, bot_id: str,
                                  action_type: str, amount: float = 0) -> bool:
        """
        Обрабатывает действие пользователя и начисляет процент реферёру
        :param user_id: user_id того, кто совершил действие
        :param bot_id: bot_id через который совершено действие
        :param action_type: тип действия ('bet', 'win')
        :param amount: сумма действия
        :return: True если успешно
        """
        try:
            is_clone = await self.db.is_clone_bot(bot_id)
            if not is_clone:
                return True

            referrer_id = await self.get_bot_creator(bot_id)
            if not referrer_id:
                self.logger.warning(f"Не найден создатель бота {bot_id}")
                return False

            if referrer_id == user_id:
                return True

            existing_referral = await self.db.fetch_one(
                """SELECT * FROM referrals
                WHERE referred_user_id = ? AND referrer_user_id = ?""",
                (user_id, referrer_id)
            )

            if not existing_referral:
                await self.db.execute(
                    """INSERT INTO referrals
                    (referrer_user_id, referred_user_id, referred_bot_id)
                    VALUES (?, ?, ?)""",
                    (referrer_id, user_id, bot_id)
                )
                self.logger.info(f"Создана реферальная связь: {referrer_id} -> {user_id}")

            reward_percent = 0.0
            if action_type == 'bet':
                reward_percent = 0.05
            elif action_type == 'win':
                reward_percent = 0.02

            if reward_percent > 0 and amount > 0:
                reward_amount = amount * reward_percent
                await self.db.update_balance(
                    referrer_id,
                    reward_amount,
                    'referral_reward',
                    f'Реферальная награда от пользователя {user_id} ({action_type})'
                )

                await self.db.execute(
                    """UPDATE referrals
                    SET reward_given = 1, total_earned = total_earned + ?
                    WHERE referrer_user_id = ? AND referred_user_id = ?""",
                    (reward_amount, referrer_id, user_id)
                )

                self.logger.info(f"Начислено {reward_amount} реферёру {referrer_id} от {user_id}")

            return True

        except Exception as e:
            self.logger.error(f"Ошибка при обработке действия пользователя: {e}")
            return False

    async def get_referral_link(self, user_id: int, bot_id: Optional[str] = None) -> str:
        """
        Генерирует реф-ссылку
        :param user_id: user_id реферера
        :param bot_id: bot_id, если None то основной бот
        :return: Реф-ссылка
        """
        if bot_id is None:
            main_bot_info = await Bot(self.main_bot_token).get_me()
            bot_id = main_bot_info.username

        ref_code = Hacher.hash(str(user_id), False)
        return f"https://t.me/{bot_id}?start=ref_{ref_code}"

    async def process_referral(self, referred_user_id: int, referral_code: str,
                               bot_id: str) -> bool:
        """
        Обрабатывает переход по реф-ссылке
        :param referred_user_id: user_id нового пользователя
        :param referral_code: Код из ссылки
        :param bot_id: bot_id через который перешел
        :return: True если успешно
        """
        try:
            referrer_id = self.ref_code_mapping.get(referral_code)
            if not referrer_id:
                user_data = await self.db.fetch_one(
                    "SELECT user_id FROM users WHERE ref_code = ?",
                    (referral_code,)
                )

                if user_data:
                    referrer_id = user_data.get("user_id")
                    self.ref_code_mapping[referral_code] = referrer_id
                else:
                    self.logger.warning(f"Не найден реферер для кода {referral_code}")
                    return False

            if referrer_id == referred_user_id:
                return False

            await self.db.execute(
                """INSERT OR IGNORE INTO referrals
                (referrer_user_id, referred_user_id, referred_bot_id)
                VALUES (?, ?, ?)""",
                (referrer_id, referred_user_id, bot_id)
            )

            self.logger.info(f"Реферальная связь создана: {referrer_id} -> {referred_user_id}")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка при обработке реф-ссылки: {e}")
            return False

    async def get_bot_token(self, bot_id: str) -> Optional[str]:
        """Получает токен бота по его ID"""
        bot = await self.db.fetch_one(
            "SELECT token FROM bot_instances WHERE bot_id = ?",
            (bot_id,)
        )
        return bot.get("token") if bot else None

    async def load_active_bots(self):
        """Загружает все активные боты при старте"""
        bots = await self.db.fetch_all("SELECT bot_id, token FROM bot_instances WHERE is_active = 1")
        for bot_record in bots:
            try:
                self.active_bots[bot_record["bot_id"]] = Bot(bot_record["token"])
            except Exception as e:
                self.logger.error(f"Ошибка при загрузке бота {bot_record['bot_id']}: {e}")

        users = await self.db.fetch_all("SELECT user_id, ref_code FROM users WHERE ref_code IS NOT NULL")
        for user in users:
            self.ref_code_mapping[user["ref_code"]] = user["user_id"]

        self.logger.info(f"Загружено {len(self.active_bots)} активных клон-ботов")

    async def cleanup(self):
        """Закрывает все открытые сессии ботов при завершении"""
        for bot_id, bot in self.active_bots.items():
            try:
                await bot.session.close()
            except Exception as e:
                self.logger.error(f"Ошибка при закрытии сессии {bot_id}: {e}")
        self.active_bots.clear()
