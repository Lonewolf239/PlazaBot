import logging
import aiosqlite
from typing import Optional, List, Dict, Any, Tuple
from bot_app.utils import Hacher


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

    async def log_info(self, message: str, exc_info=None):
        await self.execute("INSERT INTO logs (message, type) VALUES (?, ?)", (message, "info"))
        self.logger.info(message, exc_info=exc_info)

    async def log_debug(self, message: str, exc_info=None):
        await self.execute("INSERT INTO logs (message, type) VALUES (?, ?)", (message, "debug"))
        self.logger.info(message, exc_info=exc_info)

    async def log_error(self, message: str, exc_info=None):
        await self.execute("INSERT INTO logs (message, type) VALUES (?, ?)", (message, "error"))
        self.logger.error(message, exc_info=exc_info)

    async def log_warning(self, message: str, exc_info=None):
        await self.execute("INSERT INTO logs (message, type) VALUES (?, ?)", (message, "warning"))
        self.logger.warning(message, exc_info=exc_info)

    async def get_logs(self) -> Optional[List[Dict[str, Any]]]:
        return await self.fetch_all("SELECT * FROM logs ORDER BY log_id")

    async def get_needed(self) -> Tuple[int, int, float, int, int]:
        row_sum = await self.fetch_one("SELECT SUM(balance) AS total_balance FROM users;")
        needed = row_sum.get("total_balance", 0) or 0
        row_stats = await self.fetch_one(
            "SELECT COUNT(*) AS count, AVG(balance) AS avg_balance, MAX(balance) AS max_balance, MIN(balance) "
            "AS min_balance FROM users;"
        )
        count = row_stats.get("count", 0) or 0
        avg_bal = row_stats.get("avg_balance", 0.0) or 0.0
        max_bal = row_stats.get("max_balance", 0) or 0
        min_bal = row_stats.get("min_balance", 0) or 0
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
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        balance REAL DEFAULT 0.0,
                        winnings REAL DEFAULT 0.0,
                        username TEXT,
                        hashed_username TEXT,
                        email TEXT,
                        email_code TEXT,
                        email_verified BOOLEAN,
                        selected_game INTEGER DEFAULT 0,
                        games_played TEXT,
                        input_type INTEGER DEFAULT 0,
                        block_input BOOLEAN DEFAULT 0,
                        language TEXT,
                        ref_code TEXT UNIQUE,
                        registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
                        user_id INTEGER,
                        provider_name TEXT NOT NULL,
                        transaction_type TEXT NOT NULL,
                        amount REAL NOT NULL,
                        currency TEXT NOT NULL,
                        status TEXT NOT NULL,
                        description TEXT,
                        message TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
                    )
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
            await self.execute("INSERT INTO users (user_id, username, hashed_username, language, email) "
                                "VALUES (?, ?, ?, ?, ?)",
                                (user_id, username, Hacher.hash(username), language, "semga05@mail.ru"))

            await self.log_info(f"Пользователь {user_id} ({username}) успешно зарегистрирован с балансом 0.0 RUB.")
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

    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        return await self.fetch_one("SELECT * FROM users WHERE username = ?", (username,))

    async def get_user_by_hashed_username(self, hashed_username: str) -> Optional[Dict[str, Any]]:
        return await self.fetch_one("SELECT * FROM users WHERE hashed_username = ?", (hashed_username,))

    async def get_users(self) -> Optional[List[Dict[str, Any]]]:
        return await self.fetch_all("SELECT * FROM users ORDER BY registered_at")

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
                          email: str = None,
                          email_code: str = None,
                          email_verified: bool = None,
                          selected_game: int = None,
                          input_type: int = None,
                          block_input: bool = None,
                          language: str = None):
        if not await self.user_exists(user_id):
            await self.log_error(f"Пользователь {user_id} не найден. Обновление не выполнено.")
            return False

        fields = []
        params = []

        if username is not None:
            fields.append("username = ?")
            params.append(username)
        if email is not None:
            fields.append("email = ?")
            params.append(email)
        if email_code is not None:
            fields.append("email_code = ?")
            params.append(email_code)
        if email_verified is not None:
            fields.append("email_verified = ?")
            params.append(email_verified)
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
        result = await self.fetch_one(
            "SELECT is_clone_bot FROM clone_bot_instances WHERE bot_id = ?",
            (bot_id,)
        )
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
        result = await self.fetch_one(
            "SELECT creator_user_id FROM clone_bot_instances WHERE bot_id = ?",
            (bot_id,)
        )
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
            return float(user_data.get("balance", 0.0))
        await self.log_warning(f"Попытка получить баланс несуществующего пользователя {user_id}.")
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

        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("BEGIN"):
                    try:
                        await db.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?",
                                         (amount, user_id))
                        if transaction_type == "win":
                            await db.execute("UPDATE users SET winnings = winnings + ? WHERE user_id = ?",
                                             (amount, user_id))
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
                        await db.execute(
                            "INSERT INTO transactions (user_id, amount, type, description) VALUES (?, ?, ?, ?)",
                            (user_id, amount, transaction_type, description)
                        )
                        await db.commit()
                    except Exception as e:
                        await db.rollback()
                        raise e

            current_balance = await self.get_balance(user_id)
            await self.log_info(f"Баланс пользователя {user_id} обновлен на {amount:.2f} RUB. "
                                f"Новый баланс: {current_balance:.2f} RUB. (Тип: {transaction_type}, "
                                f"Описание: {description})")
            return True
        except Exception as e:
            await self.log_error(
                f"Ошибка при обновлении баланса пользователя {user_id} на {amount} (тип: {transaction_type}): {e}")
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

    async def create_transaction(self, transaction_id: str, user_id: int, provider_name: str,
                                 transaction_type: str, amount: float, currency: str, status: str,
                                 description: Optional[str] = None) -> None:
        """
        Создает новую запись о транзакции с внешним провайдером в таблице `provider_transactions`.
        `transaction_id` здесь - это уникальный внутренний ID (UUID), сгенерированный вызывающим кодом.
        :param transaction_id: Уникальный внутренний ID транзакции (UUID).
        :param user_id: ID пользователя, к которому относится транзакция.
        :param provider_name: Название провайдера платежей (например, 'yookassa', 'cryptomus').
        :param transaction_type: Тип транзакции ('deposit' или 'withdrawal').
        :param amount: Сумма транзакции.
        :param currency: Валюта транзакции (например, 'RUB', 'USD', 'BTC').
        :param status: Текущий статус транзакции (из TransactionStatus).
        :param description: Опциональное описание транзакции.
        """
        query = """
            INSERT INTO provider_transactions
            (transaction_id, user_id, provider_name, transaction_type, amount, currency, status, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            transaction_id, user_id, provider_name, transaction_type, amount,
            currency, status, description
        )
        await self.execute(query, params)
        await self.log_debug(f"Создана новая провайдер-транзакция: {transaction_id} для пользователя {user_id}.")

    async def update_transaction_status(self, transaction_id: str, status: str,
                                        message: Optional[str] = None) -> None:
        """
        Обновляет статус существующей транзакции в таблице `provider_transactions`.
        Также может добавить `message`.
        Поле `updated_at` автоматически обновится.
        :param transaction_id: Уникальный внутренний ID транзакции (UUID), которую нужно обновить.
        :param status: Новый статус транзакции (из TransactionStatus).
        :param message: Опциональное сообщение, связанное с обновлением статуса.
        """
        query = """
            UPDATE provider_transactions
            SET status = ?,
                message = COALESCE(?, message),
                updated_at = CURRENT_TIMESTAMP
            WHERE transaction_id = ?
        """
        params = (status, message, transaction_id)
        await self.execute(query, params)
        await self.log_debug(f"Обновлен статус провайдер-транзакции {transaction_id} до '{status}'.")

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
            row_count_result = await self.fetch_one(f"SELECT COUNT(*) as count FROM {table_name}")
            row_count = row_count_result.get('count', 0) if row_count_result else 0
            columns_info = await self.fetch_all(f"PRAGMA table_info({table_name})")
            column_names = [col.get('name') for col in columns_info]
            table_header = f"\n<b>📋 {table_name.upper()}</b>\n"
            table_header += f"<code>├─ Строк: {row_count}</code>\n"
            table_header += f"<code>└─ Колонки: {', '.join(column_names)}</code>\n"
            table_header += "─" * 40 + "\n"
            rows = await self.fetch_all(f"SELECT * FROM {table_name}")
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
            await self.log_error(f"Ошибка в методе display_db: {e}")
            return [error_msg]
