import uuid
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from aiocryptopay import AioCryptoPay, Networks
from aiocryptopay.models.currencies import Currency
from aiocryptopay.models.rates import ExchangeRate
from aiocryptopay.models.update import Update
from pycoingecko import CoinGeckoAPI
from bot_app.database import DatabaseInterface


class TransactionStatus:
    """Статусы транзакций"""
    # Пополнения
    PENDING_PAYMENT_INIT = "pending_payment_init"
    PAYMENT_PENDING = "payment_pending"
    PAYMENT_COMPLETED = "payment_completed"
    PAYMENT_EXPIRED = "payment_expired"
    PAYMENT_FAILED = "payment_failed"
    DEPOSIT_CONFIRMED = "deposit_confirmed"
    DEPOSIT_FAILED = "deposit_failed"

    # Выводы
    WITHDRAWAL_PENDING = "withdrawal_pending"
    WITHDRAWAL_PROCESSING = "withdrawal_processing"
    WITHDRAWAL_COMPLETED = "withdrawal_completed"
    WITHDRAWAL_FAILED = "withdrawal_failed"


CRYPTO_CODE_MAP = {
    'USDT': 'tether',
    'USDC': 'usd-coin',
    'BTC': 'bitcoin',
    'ETH': 'ethereum',
    'SOL': 'solana',
    'LTC': 'litecoin',
    'TON': 'ton',
    'TRX': 'tron',
    'GRAM': 'gram',
    'DOGE': 'dogecoin',
    'NOT': 'notcoin',
    'TRUMP': 'official-trump',
    'PEPE': 'pepe',
    'WIF': 'dogwifhat',
    'BONK': 'bonk',
    'MYI': 'mytonwallet',
    'MEMHASH': 'memhash',
    'HMSTR': 'hamster-kombat',
    'CAT': 'catizen',
    'BNB': 'binancecoin',
    'MAJOR': 'major',
    'DOGS': 'dogs',
    'MELANIA': 'melania-meme',
}


class CryptoPay:
    """
    Класс для управления пополнениями и выводами через Crypto Pay API.

    Функционал:
    - Создание счётов (invoices) для пополнений
    - Создание переводов (transfers) для выводов
    - Отслеживание статуса транзакций
    - Обработка вебхуков об оплате
    - Логирование всех операций
    """

    # Минимальное время жизни счёта (в секундах)
    MIN_INVOICE_TTL = 60
    # Максимальное время жизни счёта (в секундах) - 31 день
    MAX_INVOICE_TTL = 2678400

    def __init__(self, token: str, bot, database_interface: DatabaseInterface,
                 network: Networks = Networks.MAIN_NET, logger: Optional[logging.Logger] = None):
        """
        Инициализация CryptoPay.
        :param token: API токен от @CryptoBot
        :param bot: Экземпляр бота для отправки уведомлений
        :param database_interface: Интерфейс для работы с БД
        :param network: Сеть (MAIN_NET или TEST_NET)
        :param logger: Логгер для логирования операций
        """
        self.crypto = AioCryptoPay(token=token, network=network)
        self.supported_assets: list[Currency] = None
        self.supported_codes = []
        self._bot = bot
        self._database = database_interface
        self._logger = logger or logging.getLogger(__name__)
        self._token = token
        self._network = network

    async def initialize(self):
        self.supported_assets = await self.crypto.get_currencies()
        for asset in self.supported_assets:
            self.supported_codes.append(asset.code)

    @staticmethod
    def _generate_transaction_id() -> str:
        """Генерирует уникальный идентификатор транзакции."""
        return str(uuid.uuid4())

    async def _record_transaction(self, user_id: int, transaction_type: str, amount: float, status: str,
                                  currency: str, description: str = "", crypto_id: Optional[int] = None,
                                  payload: str = "") -> str:
        """
        Записывает транзакцию в БД.
        :param user_id: Telegram ID пользователя
        :param transaction_type: Тип транзакции ('deposit' или 'withdrawal')
        :param amount: Размер суммы
        :param status: Статус транзакции
        :param currency: Код валюты (TON, BTC и т.д.)
        :param description: Описание транзакции
        :param crypto_id: ID счёта/перевода в Crypto Pay
        :param payload: Дополнительные данные
        :return: internal_transaction_id: Внутренний ID транзакции
        """
        internal_transaction_id = self._generate_transaction_id()
        try:
            await self._database.create_transaction(
                transaction_id=internal_transaction_id,
                user_id=user_id,
                transaction_type=transaction_type,
                amount=amount,
                currency=currency,
                status=status,
                description=description,
                crypto_id=crypto_id,
                payload=payload,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            self._logger.info(
                f"✓ RECORD TRANSACTION: TxID={internal_transaction_id}, "
                f"User={user_id}, Type={transaction_type}, "
                f"Amount={amount} {currency}, Status={status}"
            )
        except Exception as e:
            self._logger.error(
                f"✗ Failed to record transaction: {e}",
                exc_info=True
            )
            raise
        return internal_transaction_id

    async def _update_transaction_status(self, internal_transaction_id: str, status: str, message: str = "",
                                         crypto_data: Optional[Dict[str, Any]] = None) -> None:
        """
        Обновляет статус транзакции в БД.
        :param internal_transaction_id: Внутренний ID транзакции
        :param status: Новый статус
        :param message: Сообщение/ошибка
        :param crypto_data: Дополнительные данные из Crypto Pay
        """
        try:
            await self._database.update_transaction_status(
                transaction_id=internal_transaction_id,
                status=status,
                message=message,
                updated_at=datetime.now(),
                crypto_data=crypto_data
            )
            self._logger.info(
                f"✓ UPDATE TRANSACTION STATUS: TxID={internal_transaction_id}, "
                f"Status={status}, Message={message}"
            )
        except Exception as e:
            self._logger.error(
                f"✗ Failed to update transaction status: {e}",
                exc_info=True
            )
            raise

    async def get_exchange_rates(self, source: Optional[str] = None,
                                 target: Optional[str] = None) -> list[ExchangeRate]:
        """
        Получает текущие курсы обмена с опциональной фильтрацией.

        :param source: Исходная валюта для фильтрации (опционально)
        :param target: Целевая валюта для фильтрации (опционально)
        :return: Список курсов обмена, отфильтрованный по параметрам
        :raises Exception: Если запрос к API провалился
        """
        try:
            rates = await self.crypto.get_exchange_rates()
            if source is not None:
                rates = [rate for rate in rates if rate.source == source]
            if target is not None:
                rates = [rate for rate in rates if rate.target == target]
            self._logger.debug(
                f"Exchange rates fetched: {len(rates)} pairs "
                f"(source: {source}, target: {target})"
            )
            return rates
        except Exception as e:
            self._logger.error(
                f"Failed to get exchange rates (source: {source}, target: {target}): {e}"
            )
            raise

    @staticmethod
    def get_crypto_rate(currency_code: str) -> float:
        """
        Получает текущий курс криптовалюты к доллару по её коду.
        :param currency_code: код криптовалюты (например, 'BTC', 'ETH')
        :return: float: цена в USD
        """
        try:
            cg = CoinGeckoAPI()
            crypto_id = CRYPTO_CODE_MAP[currency_code]
            price_data = cg.get_price(ids=crypto_id, vs_currencies='usd')
            return price_data[crypto_id]['usd']
        except Exception as e:
            print(f"Ошибка получения курса: {e}")
            return None

    async def get_balance(self) -> Dict[str, Any]:
        """
        Получает баланс кошелька приложения.
        :return: Словарь с балансами по валютам
        """
        try:
            balance = await self.crypto.get_balance()
            self._logger.info(f"Balance fetched: {len(balance)} assets")
            return {b.currency_code: {
                "available": float(b.available),
                "onhold": float(b.onhold)
            } for b in balance}
        except Exception as e:
            self._logger.error(f"Failed to get balance: {e}")
            raise

    async def get_total_balance_usd(self) -> float:
        """Получает общий баланс в долларах (только итоговую сумму)."""
        try:
            balance = await self.crypto.get_balance()
            exchange_rates = await self.crypto.get_exchange_rates()
            rates_map = {}
            for rate in exchange_rates:
                if rate.target == "USD":
                    rates_map[rate.source] = float(rate.rate)
            total_usd = 0.0
            for b in balance:
                available = float(b.available)
                rate_to_usd = rates_map.get(b.currency_code, 0)
                total_usd += available * rate_to_usd
            self._logger.info(f"Total balance: {total_usd} USD")
            return round(total_usd, 2)
        except Exception as e:
            self._logger.error(f"Failed to calculate total balance in USD: {e}")
            raise

    async def get_currencies_with_balance(self) -> list[str]:
        """
        Получает список кодов валют с ненулевым балансом.
        :return: Список кодов валют, где есть доступные средства
        """
        try:
            balance = await self.get_balance()
            currencies = [
                currency_code
                for currency_code, balances in balance.items()
                if balances["available"] > 0
            ]
            self._logger.info(f"Found {len(currencies)} currencies with balance: {currencies}")
            return currencies
        except Exception as e:
            self._logger.error(f"Failed to get currencies with balance: {e}")
            raise

    async def get_app_stats(self, start_at: Optional[str] = None, end_at: Optional[str] = None) -> Dict[str, Any]:
        """
        Получает статистику приложения.
        :param start_at: Начальная дата (ISO 8601)
        :param end_at: Конечная дата (ISO 8601)
        :return: Статистика приложения
        """
        try:
            stats = await self.crypto.get_stats(start_at=start_at, end_at=end_at)
            return {
                "volume": float(stats.volume),
                "conversion": float(stats.conversion),
                "unique_users": stats.unique_users_count,
                "created_invoices": stats.created_invoice_count,
                "paid_invoices": stats.paid_invoice_count,
                "start_at": stats.start_at,
                "end_at": stats.end_at
            }
        except Exception as e:
            self._logger.error(f"Failed to get app stats: {e}")
            raise

    # ==================== ПОПОЛНЕНИЯ (DEPOSITS) ====================

    async def initiate_deposit(self, user_id: int, amount: float, currency: str = "TON",
                               description: str = "", expires_in: int = 3600, allow_comments: bool = True,
                               allow_anonymous: bool = False) -> Dict[str, Any]:
        """
        Инициирует пополнение, создав счёт.
        :param user_id: Telegram ID пользователя
        :param amount: Размер пополнения
        :param currency: Код криптовалюты (TON, BTC, ETH и т.д.)
        :param description: Описание счёта
        :param expires_in: Время жизни счёта в секундах (60-2678400)
        :param allow_comments: Разрешить комментарии
        :param allow_anonymous: Разрешить анонимные платежи
        :return: Словарь с данными о счёте и URL для оплаты
        """
        if amount <= 0:
            self._logger.warning(f"Invalid deposit amount: {amount}")
            return {
                "status": TransactionStatus.DEPOSIT_FAILED,
                "message": "Размер пополнения должен быть положительным"
            }
        if currency not in self.supported_codes:
            self._logger.warning(f"Unsupported currency: {currency}")
            return {
                "status": TransactionStatus.DEPOSIT_FAILED,
                "message": f"Валюта {currency} не поддерживается"
            }
        if not (self.MIN_INVOICE_TTL <= expires_in <= self.MAX_INVOICE_TTL):
            self._logger.warning(f"Invalid expires_in: {expires_in}")
            expires_in = max(self.MIN_INVOICE_TTL, min(expires_in, self.MAX_INVOICE_TTL))
        internal_tx_id = await self._record_transaction(
            user_id=user_id,
            transaction_type="deposit",
            amount=amount,
            currency=currency,
            status=TransactionStatus.PENDING_PAYMENT_INIT,
            description=description or f"Пополнение {amount} {currency}"
        )
        try:
            invoice = await self.crypto.create_invoice(
                asset=currency,
                amount=amount,
                description=description or f"Пополнение",
                payload=internal_tx_id,
                expires_in=expires_in,
                allow_comments=allow_comments,
                allow_anonymous=allow_anonymous
            )
            await self._update_transaction_status(
                internal_tx_id,
                TransactionStatus.PAYMENT_PENDING,
                crypto_data={
                    "invoice_id": invoice.invoice_id,
                    "hash": invoice.hash
                }
            )
            self._logger.info(
                f"✓ Deposit initiated: TxID={internal_tx_id}, "
                f"InvoiceID={invoice.invoice_id}, User={user_id}, "
                f"Amount={amount} {currency}"
            )
            return {
                "status": TransactionStatus.PAYMENT_PENDING,
                "internal_tx_id": internal_tx_id,
                "invoice_id": invoice.invoice_id,
                "amount": amount,
                "currency": currency,
                "payment_url": invoice.bot_invoice_url,
                "mini_app_url": invoice.mini_app_invoice_url,
                "web_app_url": invoice.web_app_invoice_url,
                "expires_at": invoice.expiration_date
            }
        except Exception as e:
            self._logger.error(f"Failed to create invoice: {e}", exc_info=True)
            await self._update_transaction_status(
                internal_tx_id,
                TransactionStatus.DEPOSIT_FAILED,
                message=f"Ошибка создания счёта: {str(e)}"
            )
            raise

    async def get_invoice(self, internal_tx_id: str):
        """
        Получает статус пополнения.
        :param internal_tx_id: Внутренний ID транзакции
        :return: Словарь со статусом пополнения
        """
        try:
            crypto_data = await self._database.get_crypto_data(internal_tx_id)
            if not crypto_data:
                return None
            crypto_id = crypto_data.get("invoice_id")
            invoice = await self.crypto.get_invoices(invoice_ids=[crypto_id])
            return invoice[0]
        except Exception as e:
            self._logger.error(f"Failed to get deposit status: {e}")
            raise

    async def cancel_deposit(self, internal_tx_id: str) -> bool:
        """
        Отменяет активный счёт пополнения.
        :param internal_tx_id: Внутренний ID транзакции
        :return: True если успешно отменено
        """
        try:
            crypto_data = await self._database.get_crypto_data(internal_tx_id)
            if not crypto_data:
                self._logger.warning(f"Transaction not found: {internal_tx_id}")
                return False
            crypto_id = crypto_data.get("invoice_id")
            if not crypto_id:
                self._logger.warning(f"No invoice ID for transaction: {internal_tx_id}")
                return False
            result = await self.crypto.delete_invoice(invoice_id=int(crypto_id))
            if result:
                await self._update_transaction_status(
                    internal_tx_id,
                    TransactionStatus.PAYMENT_EXPIRED,
                    message="Счёт отменён пользователем"
                )
                self._logger.info(f"✓ Deposit cancelled: {internal_tx_id}")
                return True
            else:
                self._logger.warning(f"Failed to delete invoice: {crypto_id}")
                return False
        except Exception as e:
            self._logger.error(f"Failed to cancel deposit: {e}")
            return False

    # ==================== ВЫВОДЫ (WITHDRAWALS) ====================

    async def initiate_withdrawal(self, user_id: int, amount: float,
                                  currency: str = "TON", description: str = "") -> Dict[str, Any]:
        """
        Инициирует вывод средств (создаёт трансфер).
        :param user_id: Telegram ID пользователя
        :param amount: Размер вывода
        :param currency: Код криптовалюты
        :param description: Описание вывода
        :return: Словарь с данными о выводе
        """
        if amount <= 0:
            return {
                "status": TransactionStatus.WITHDRAWAL_FAILED,
                "message": "Размер вывода должен быть положительным"
            }
        if currency not in self.supported_codes:
            return {
                "status": TransactionStatus.WITHDRAWAL_FAILED,
                "message": f"Валюта {currency} не поддерживается"
            }
        internal_tx_id = await self._record_transaction(
            user_id=user_id,
            transaction_type="withdrawal",
            amount=amount,
            currency=currency,
            status=TransactionStatus.WITHDRAWAL_PENDING,
            description=description or f"Вывод {amount} {currency}"
        )
        try:
            spend_id = self._generate_transaction_id()
            transfer = await self.crypto.transfer(
                user_id=user_id,
                asset=currency,
                amount=amount,
                spend_id=spend_id
            )
            if transfer is None:
                return None
            await self._update_transaction_status(
                internal_tx_id,
                TransactionStatus.WITHDRAWAL_PROCESSING,
                crypto_data={
                    "transfer_id": transfer.transfer_id,
                    "spend_id": spend_id
                }
            )
            self._logger.info(
                f"✓ Withdrawal initiated: TxID={internal_tx_id}, "
                f"TransferID={transfer.transfer_id}, User={user_id}, "
                f"Amount={amount} {currency}"
            )
            return transfer
        except Exception as e:
            self._logger.error(f"Failed to create transfer: {e}", exc_info=True)
            await self._update_transaction_status(
                internal_tx_id,
                TransactionStatus.WITHDRAWAL_FAILED,
                message=f"Ошибка создания вывода: {str(e)}"
            )
            return None

    async def get_withdrawal_status(self, internal_tx_id: str) -> Dict[str, Any]:
        """
        Получает статус вывода.
        :param internal_tx_id: Внутренний ID транзакции
        :return: Словарь со статусом вывода
        """
        try:
            tx = await self._database.get_transaction(internal_tx_id)
            if not tx:
                return {"status": "not_found", "message": "Транзакция не найдена"}
            return {
                "internal_tx_id": internal_tx_id,
                "amount": tx.get("amount"),
                "currency": tx.get("currency"),
                "status": tx.get("status"),
                "created_at": tx.get("created_at"),
                "updated_at": tx.get("updated_at")
            }
        except Exception as e:
            self._logger.error(f"Failed to get withdrawal status: {e}")
            raise

    # ==================== WEBHOOKS ====================

    async def invoice_paid(self, update: Update) -> None:
        """
        Обработчик события оплаты счёта (webhook).
        :param update: Объект обновления от Crypto Pay API
        """
        try:
            invoice = update.invoice
            self._logger.info(
                f"✓ Invoice paid webhook received: InvoiceID={invoice.invoice_id}, "
                f"Amount={invoice.amount} {invoice.asset}"
            )
            if not invoice.payload:
                self._logger.warning("Invoice has no payload, skipping")
                return
            internal_tx_id = invoice.payload
            await self._update_transaction_status(
                internal_tx_id,
                TransactionStatus.DEPOSIT_CONFIRMED,
                message=f"Платёж подтверждён. Invoice: {invoice.invoice_id}",
                crypto_data={
                    "invoice_id": invoice.invoice_id,
                    "paid_asset": invoice.paid_asset,
                    "paid_amount": str(invoice.paid_amount),
                    "paid_usd_rate": str(invoice.paid_usd_rate),
                    "fee_amount": str(invoice.fee_amount),
                    "paid_at": str(invoice.paid_at)
                }
            )
            tx = await self._database.get_transaction(internal_tx_id)
            if tx:
                user_id = tx.get("user_id")
                amount = float(invoice.amount) * float(invoice.paid_usd_rate)
                await self._database.update_balance(user_id, amount, "deposit")
                await self._send_deposit_notification(
                    user_id=user_id,
                    amount=invoice.paid_amount,
                    asset=invoice.paid_asset,
                    fee=invoice.fee_amount
                )
        except Exception as e:
            self._logger.error(f"Failed to process invoice_paid webhook: {e}", exc_info=True)

    async def _send_deposit_notification(self, user_id: int, amount: float, asset: str, fee: float = 0) -> None:
        """
        Отправляет уведомление об успешном пополнении.

        :param user_id: Telegram ID пользователя
        :param amount: Размер платежа
        :param asset: Криптовалюта
        :param fee: Комиссия
        """
        try:
            message = (
                f"✅ Пополнение успешно!\n\n"
                f"Сумма: {amount} {asset}\n"
                f"Комиссия: {fee} {asset}\n"
                f"Получено: {amount - fee} {asset}"
            )
            await self._bot.send_message(user_id, message)
        except Exception as e:
            self._logger.error(f"Failed to send notification to {user_id}: {e}")

    # ==================== ПРОВЕРКА СТАТУСОВ ====================

    async def check_pending_deposits(self) -> None:
        """
        Проверяет статус всех активных пополнений.
        Используется для синхронизации с API, если вебхуки недоступны.
        """
        try:
            invoices = await self.crypto.get_invoices(status="active")
            self._logger.info(f"Checking {len(invoices)} active invoices")
            for invoice in invoices:
                if not invoice.payload:
                    continue
                internal_tx_id = invoice.payload
                tx = await self._database.get_transaction(internal_tx_id)
                if tx and tx.get("status") == TransactionStatus.PAYMENT_PENDING:
                    self._logger.debug(f"Invoice {invoice.invoice_id} still pending")
        except Exception as e:
            self._logger.error(f"Failed to check pending deposits: {e}")

    async def check_pending_withdrawals(self) -> None:
        """Проверяет статус всех активных выводов."""
        try:
            transfers = await self.crypto.get_transfers()
            self._logger.info(f"Checking {len(transfers)} transfers")
            for transfer in transfers:
                if not transfer.spend_id:
                    continue
                internal_tx_id = transfer.spend_id
                tx = await self._database.get_transaction(internal_tx_id)
                if tx and tx.get("status") == TransactionStatus.WITHDRAWAL_PROCESSING:
                    await self._update_transaction_status(
                        internal_tx_id,
                        TransactionStatus.WITHDRAWAL_COMPLETED,
                        message=f"Вывод завершён. Transfer: {transfer.transfer_id}",
                        crypto_data={
                            "transfer_id": transfer.transfer_id,
                            "completed_at": str(transfer.completed_at)
                        }
                    )
        except Exception as e:
            self._logger.error(f"Failed to check pending withdrawals: {e}")

    async def get_user_transactions(self, user_id: int, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Получает историю транзакций пользователя.

        :param user_id: Telegram ID пользователя
        :param limit: Максимальное количество записей
        :param offset: Смещение для пагинации

        :return: Список транзакций
        """
        try:
            transactions = await self._database.get_user_transactions(
                user_id=user_id,
                limit=limit,
                offset=offset
            )
            return transactions
        except Exception as e:
            self._logger.error(f"Failed to get user transactions: {e}")
            raise

    # ==================== УТИЛИТЫ ====================

    async def close(self) -> None:
        """Закрывает подключение к Crypto Pay API."""
        try:
            await self.crypto.close()
            self._logger.info("CryptoPay connection closed")
        except Exception as e:
            self._logger.error(f"Failed to close CryptoPay: {e}")

    @staticmethod
    def get_status_display(status: str) -> str:
        """
        Преобразует статус в понятное пользователю описание.
        :param status: Статус транзакции
        :return: Описание статуса на русском
        """
        status_map = {
            TransactionStatus.PENDING_PAYMENT_INIT: "⏳ Инициализация платежа",
            TransactionStatus.PAYMENT_PENDING: "⏳ Ожидание оплаты",
            TransactionStatus.PAYMENT_COMPLETED: "✅ Платёж завершён",
            TransactionStatus.PAYMENT_EXPIRED: "❌ Платёж истёк",
            TransactionStatus.PAYMENT_FAILED: "❌ Платёж не удался",
            TransactionStatus.DEPOSIT_CONFIRMED: "✅ Пополнение подтверждено",
            TransactionStatus.DEPOSIT_FAILED: "❌ Пополнение не удалось",
            TransactionStatus.WITHDRAWAL_PENDING: "⏳ Вывод в ожидании",
            TransactionStatus.WITHDRAWAL_PROCESSING: "⏳ Вывод обрабатывается",
            TransactionStatus.WITHDRAWAL_COMPLETED: "✅ Вывод завершён",
            TransactionStatus.WITHDRAWAL_FAILED: "❌ Вывод не удался",
        }
        return status_map.get(status, status)
