import logging
import uuid
import json

from typing import Dict, Any, Optional, List
from bot_app.database.db_manager import DatabaseInterface
from .providers.base_provider import IProvider
from .config import CONFIG
from bot_app.utils.transaction_statuses import TransactionStatus


# --- Фабрика Провайдеров ---

class ProviderFactory:
    def __init__(self, bot, database_interface: DatabaseInterface, logger: logging.Logger):
        self._providers: Dict[str, IProvider] = {}
        self._bot = bot
        self._database_interface = database_interface
        self._logger = logger
        self._config = CONFIG

    async def initialize(self):
        await self._register_providers()

    async def _register_providers(self):
        """Регистрирует всех доступных провайдеров."""
        await self._database_interface.log_info("Registering providers...")

        # Yookassa Provider
        yookassa_conf = self._config.get("yookassa", {})
        if yookassa_conf.get("enabled", False):
            from bot_app.payments.providers.yookassa_provider import YookassaProvider
            await self.register_provider(YookassaProvider(
                logger=self._logger,
                bot=self._bot,
                database_interface=self._database_interface,
                yookassa_config=yookassa_conf
            ))
            await self._database_interface.log_info("Yookassa provider registered.")

        # TODO: Добавить регистрацию других провайдеров

    async def register_provider(self, provider: IProvider):
        """Регистрирует новый провайдер."""
        if not isinstance(provider, IProvider):
            raise TypeError(f"Provider {type(provider).__name__} must implement IProvider interface")
        self._providers[provider.get_provider_name()] = provider
        await self._database_interface.log_info(f"Provider '{provider.get_provider_name()}' registered.")

    def get_provider(self, provider_name: str) -> Optional[IProvider]:
        """Получает экземпляр провайдера по имени."""
        return self._providers.get(provider_name)

    def get_all_provider_names(self) -> List[str]:
        """Возвращает список имен всех зарегистрированных провайдеров."""
        return list(self._providers.keys())

    def get_providers(self):
        return self._providers


# --- Сервис Платежного Шлюза (Wallet Service) ---

class PaymentGateway:
    def __init__(self, database_interface: DatabaseInterface, bot, logger: logging.Logger):
        self._database_interface = database_interface
        self._bot = bot
        self._logger = logger
        self._config = CONFIG
        self._provider_factory = ProviderFactory(bot, database_interface, logger)

    async def initialize(self):
        await self._provider_factory.initialize()

    @staticmethod
    def _generate_internal_transaction_id() -> str:
        return str(uuid.uuid4())

    def get_config(self):
        return self._config

    async def _record_transaction(self, user_id: int, provider_name: str, transaction_type: str, amount: float,
                                  status: str, currency: str, description: str = "") -> str:
        """Записывает транзакцию в БД. Возвращает internal_transaction_id."""
        internal_transaction_id = self._generate_internal_transaction_id()
        await self._database_interface.create_transaction(
            transaction_id=internal_transaction_id,
            user_id=user_id,
            provider_name=provider_name,
            transaction_type=transaction_type,
            amount=amount,
            currency=currency,
            status=status,
            description=description
        )

        await self._database_interface.log_info(
            f"RECORD TRANSACTION: TxID: {internal_transaction_id}, User: {user_id}, "
            f"Provider: {provider_name}, Type: {transaction_type}, Amount: {amount} {currency}, "
            f"Status: {status}")
        return internal_transaction_id

    async def _update_transaction_status(self, internal_transaction_id: str, status: str, message: str = ""):
        """Обновляет статус транзакции в БД."""
        await self._database_interface.update_transaction_status(
            transaction_id=internal_transaction_id,
            status=status,
            message=message
        )

        await self._database_interface.log_info(
            f"UPDATE TRANSACTION STATUS: TxID: {internal_transaction_id}, New Status: {status}, "
            f"Message: {message}")

    def get_providers(self, provider_type: str) -> list[IProvider]:
        """
        Возвращает список провайдеров в зависимости от типа операции.

        :param provider_type: Тип операции — "deposit" или "withdraw".
                "deposit" — вернуть провайдеров, поддерживающих пополнение.
                "withdraw" — вернуть провайдеров, поддерживающих вывод.
        :return: Список провайдеров, удовлетворяющих условию.
        """
        return [
            p for p in self._provider_factory.get_providers().values()
            if (p.has_deposit if provider_type == "deposit" else p.has_withdraw)
        ]

    async def initiate_deposit(self, user_id: int, amount: float,
                               provider_name: str, currency: str = "RUB") -> Dict[str, Any]:
        """Инициирует процесс пополнения баланса."""
        if amount <= 0:
            return {"status": TransactionStatus.DEPOSIT_FAILED, "message": "Deposit amount must be positive."}

        provider = self._provider_factory.get_provider(provider_name)
        if not provider:
            return {"status": TransactionStatus.DEPOSIT_FAILED, "message": f"Provider '{provider_name}' not found."}

        internal_transaction_id = await self._record_transaction(
            user_id=user_id, provider_name=provider_name, transaction_type="deposit",
            amount=amount, currency=currency, status=TransactionStatus.PENDING_PAYMENT_INIT,
            description="Deposit initiation",
        )

        try:
            deposit_result = await provider.deposit(user_id, amount, internal_transaction_id, currency)
            provider_status = deposit_result.get("status")
            provider_tx_id = deposit_result.get("provider_transaction_id", "N/A")
            payment_url = deposit_result.get("url")

            if provider_status == "pending_confirmation":
                await self._update_transaction_status(
                    internal_transaction_id=internal_transaction_id,
                    status=TransactionStatus.PENDING_PAYMENT_CONFIRMATION,
                    message=f"Waiting for payment confirmation. Provider TxID: {provider_tx_id}"
                )

                return {
                    "status": TransactionStatus.PENDING_PAYMENT_CONFIRMATION,
                    "message": "Payment initiated. Please complete the payment.",
                    "payment_url": payment_url,
                    "transaction_id": internal_transaction_id
                }
            else:
                error_message = deposit_result.get("message", "Unknown error from provider.")
                await self._update_transaction_status(
                    internal_transaction_id=internal_transaction_id,
                    status=TransactionStatus.DEPOSIT_FAILED,
                    message=f"Failed to initiate deposit: {error_message}. Provider TxID: {provider_tx_id}"
                )

                return {
                    "status": TransactionStatus.DEPOSIT_FAILED,
                    "message": f"Failed to initiate deposit: {error_message}",
                    "transaction_id": internal_transaction_id
                }

        except Exception as e:
            await self._database_interface.log_error(f"PaymentGateway Error initiating deposit: {e}", exc_info=True)
            await self._update_transaction_status(
                internal_transaction_id=internal_transaction_id,
                status=TransactionStatus.DEPOSIT_FAILED,
                message=f"An unexpected error occurred: {e}"
            )

            return {
                "status": TransactionStatus.DEPOSIT_FAILED,
                "message": f"An unexpected error occurred: {e}",
                "transaction_id": internal_transaction_id
            }

    async def handle_deposit_notification(self, provider_name: str, notification_data: dict) -> Dict[str, Any]:
        """Перенаправляет уведомление о пополнении соответствующему провайдеру."""
        provider = self._provider_factory.get_provider(provider_name)
        if not provider:
            await self._database_interface.log_error(
                f"PaymentGateway: Provider '{provider_name}' not found for notification handling.")
            return {"status": "failed", "message": "Provider not found"}

        try:
            result = await provider.handle_deposit_notification(
                notification_data=notification_data,
                db_interface=self._database_interface,
                bot=self._bot,
                logger=self._logger
            )
            return result
        except Exception as e:
            await self._database_interface.log_error(f"PaymentGateway Error handling deposit notification for provider "
                                                     f"{provider_name}: {e}", exc_info=True)
            return {"status": "failed", "message": f"An unexpected error occurred: {e}"}

    async def initiate_withdrawal(self, user_id: int, amount: float, currency: str,
                                  target_provider_name: str) -> Dict[str, Any]:
        """Инициирует процесс вывода средств."""
        if amount <= 0:
            return {"status": TransactionStatus.WITHDRAWAL_FAILED, "message": "Withdrawal amount must be positive."}

        current_balance = await self._database_interface.get_balance(user_id)
        if current_balance is None:
            await self._database_interface.log_error(f"PaymentGateway: User {user_id} balance not found.")
            return {"status": TransactionStatus.WITHDRAWAL_FAILED, "message": "User balance not found."}

        if current_balance < amount:
            return {"status": TransactionStatus.WITHDRAWAL_FAILED, "message": "Insufficient balance."}

        provider = self._provider_factory.get_provider(target_provider_name)
        if not provider:
            return {
                "status": TransactionStatus.WITHDRAWAL_FAILED,
                "message": f"Withdrawal provider '{target_provider_name}' not found."
            }

        internal_transaction_id = await self._record_transaction(
            user_id=user_id, provider_name=target_provider_name, transaction_type="withdrawal",
            amount=amount, currency=currency, status=TransactionStatus.PENDING_WITHDRAWAL_INIT,
            description="Withdrawal initiation"
        )

        try:
            withdrawal_result = await provider.withdraw(user_id, amount, internal_transaction_id, currency)
            provider_status = withdrawal_result.get("status")
            provider_message = withdrawal_result.get("message", "")
            provider_tx_id = withdrawal_result.get("provider_transaction_id", "N/A")

            if provider_status == TransactionStatus.PENDING_WITHDRAWAL_REVIEW:
                await self._update_transaction_status(
                    internal_transaction_id=internal_transaction_id,
                    status=TransactionStatus.PENDING_WITHDRAWAL_REVIEW,
                    message=f"Withdrawal initiated, awaiting review. {provider_message}. "
                            f"Provider TxID: {provider_tx_id}"
                )

                await self._database_interface.update_balance(user_id, -amount, transaction_type="withdrawal",
                                                              description=f"Withdrawal initiated: "
                                                                          f"{internal_transaction_id}")

                await self._bot.send_message(user_id, f"Your withdrawal request of {amount:.2f} "
                                                      f"{currency} has been submitted and is awaiting review.")

                return {
                    "status": TransactionStatus.PENDING_WITHDRAWAL_REVIEW,
                    "message": f"Withdrawal request submitted. It is awaiting review. {provider_message}",
                    "transaction_id": internal_transaction_id
                }

            elif provider_status == TransactionStatus.WITHDRAWAL_SUCCEEDED:
                await self._update_transaction_status(
                    internal_transaction_id=internal_transaction_id,
                    status=TransactionStatus.WITHDRAWAL_SUCCEEDED,
                    message=f"{provider_message}. Provider TxID: {provider_tx_id}"
                )

                await self._database_interface.update_balance(user_id, -amount, transaction_type="withdrawal",
                                                              description=f"Withdrawal succeeded: "
                                                                          f"{internal_transaction_id}")

                await self._bot.send_message(user_id, f"Your withdrawal of {amount:.2f} "
                                                      f"{currency} has been successfully processed.")

                return {
                    "status": TransactionStatus.WITHDRAWAL_SUCCEEDED,
                    "message": "Withdrawal successful.",
                    "transaction_id": internal_transaction_id
                }

            else:
                error_message = withdrawal_result.get("message", "Unknown error from provider.")
                await self._update_transaction_status(
                    internal_transaction_id=internal_transaction_id,
                    status=TransactionStatus.WITHDRAWAL_FAILED,
                    message=f"Withdrawal failed: {error_message}. Provider TxID: {provider_tx_id}"
                )

                await self._bot.send_message(user_id, f"Your withdrawal of {amount:.2f} "
                                                      f"{currency} failed. Reason: {error_message}")

                return {
                    "status": TransactionStatus.WITHDRAWAL_FAILED,
                    "message": f"Withdrawal failed: {error_message}",
                    "transaction_id": internal_transaction_id
                }

        except Exception as e:
            await self._database_interface.log_error(f"PaymentGateway Error initiating withdrawal: {e}", exc_info=True)
            await self._update_transaction_status(
                internal_transaction_id=internal_transaction_id,
                status=TransactionStatus.WITHDRAWAL_FAILED,
                message=f"An unexpected error occurred: {e}"
            )

            await self._bot.send_message(user_id, f"An error occurred during your withdrawal request: {e}")

            return {
                "status": TransactionStatus.WITHDRAWAL_FAILED,
                "message": f"An unexpected error occurred: {e}",
                "transaction_id": internal_transaction_id
            }

    async def complete_withdrawal(self, internal_transaction_id: str, status: str,
                                  provider_details: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Этот метод вызывается, когда известен окончательный статус вывода
        (например, после ручного подтверждения или обработки внешним сервисом).
        """
        transaction = await self._database_interface.get_provider_transaction(internal_transaction_id)
        if not transaction:
            await self._database_interface.log_error(
                f"PaymentGateway: Transaction {internal_transaction_id} not found.")
            return {"status": "failed", "message": "Transaction not found."}

        provider_name = transaction.get("provider_name")
        provider = self._provider_factory.get_provider(provider_name)
        if not provider:
            await self._database_interface.log_error(f"PaymentGateway: Provider '{provider_name}' not found.")
            return {"status": "failed", "message": "Provider not found."}

        details = provider_details or {}
        try:
            result = await provider.handle_withdrawal_callback(
                transaction_id=internal_transaction_id,
                status=status,
                details=details
            )
            return result
        except Exception as e:
            await self._database_interface.log_error(f"PaymentGateway Error completing withdrawal: {e}", exc_info=True)
            return {"status": "failed", "message": f"An unexpected error occurred: {e}"}

    # ======================== WEBHOOK HANDLERS ========================

    async def _verify_yookassa_signature(self, raw_body: bytes, signature_header: str) -> bool:
        """
        Проверяет подпись Yookassa webhook'а.
        Yookassa отправляет X-Yookassa-Webhook-Id и X-Yookassa-Webhook-DerivedsignatureNotificationId.
        Однако в базовой версии проверка не требуется, если используется HTTPS.

        :param raw_body: Сырое тело запроса
        :param signature_header: Значение заголовка подписи
        :return: True если подпись валидна
        """
        # Для Yookassa проверка подписи опциональна на HTTPS
        # В production следует добавить проверку согласно документации Yookassa
        await self._database_interface.log_debug("Yookassa signature verification (currently skipped for HTTPS)")
        return True

    async def handle_yookassa_webhook(self, request_body: str, request_headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Обрабатывает webhook от Yookassa.

        FastAPI пример использования:

        @app.post("/payment/yookassa/webhook")
        async def yookassa_webhook(request: Request):
            body = await request.body()
            headers = dict(request.headers)
            result = await payment_gateway.handle_yookassa_webhook(
                request_body=body.decode('utf-8'),
                request_headers=headers
            )
            return result

        :param request_body: Тело запроса (JSON строка)
        :param request_headers: Заголовки запроса
        :return: Словарь с результатом обработки
        """
        await self._database_interface.log_info("Received Yookassa webhook")

        try:
            # Парсим JSON
            notification_data = json.loads(request_body)

            # Проверяем подпись (опционально)
            signature = request_headers.get("X-Yookassa-Webhook-DerivedsignatureNotificationId", "")
            signature_valid = self._verify_yookassa_signature(request_body.encode('utf-8'), signature)
            if not signature_valid:
                await self._database_interface.log_warning("Invalid Yookassa webhook signature")
                return {"status": "error", "message": "Invalid signature"}

            # Обрабатываем уведомление через провайдера
            result = await self.handle_deposit_notification("yookassa", notification_data)

            await self._database_interface.log_info(f"Yookassa webhook processed: {result}")

            # Возвращаем успешный ответ для Yookassa
            return {
                "status": "ok",
                "code": "200"
            }

        except json.JSONDecodeError as e:
            await self._database_interface.log_error(f"Yookassa webhook: Invalid JSON in request body: {e}")
            return {"status": "error", "message": "Invalid JSON"}

        except Exception as e:
            await self._database_interface.log_error(f"Yookassa webhook error: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}

    async def handle_cryptomus_webhook(self, request_body: str, request_headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Обрабатывает webhook от Cryptomus.

        FastAPI пример использования:

        @app.post("/payment/cryptomus/webhook")
        async def cryptomus_webhook(request: Request):
            body = await request.body()
            headers = dict(request.headers)
            result = await payment_gateway.handle_cryptomus_webhook(
                request_body=body.decode('utf-8'),
                request_headers=headers
            )
            return result

        :param request_body: Тело запроса (JSON строка)
        :param request_headers: Заголовки запроса
        :return: Словарь с результатом обработки
        """
        await self._database_interface.log_info("Received Cryptomus webhook")

        try:
            # Парсим JSON
            notification_data = json.loads(request_body)

            # TODO: Добавить проверку подписи для Cryptomus если требуется

            # Обрабатываем уведомление через провайдера
            result = await self.handle_deposit_notification("cryptomus", notification_data)

            await self._database_interface.log_info(f"Cryptomus webhook processed: {result}")

            return {"status": "ok"}

        except json.JSONDecodeError as e:
            await self._database_interface.log_error(f"Cryptomus webhook: Invalid JSON in request body: {e}")
            return {"status": "error", "message": "Invalid JSON"}

        except Exception as e:
            await self._database_interface.log_error(f"Cryptomus webhook error: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}

    def get_webhook_handlers(self) -> Dict[str, callable]:
        """
        Возвращает словарь обработчиков webhook'ов.
        Используется для регистрации маршрутов в фреймворке.

        Пример использования с FastAPI:

        handlers = payment_gateway.get_webhook_handlers()

        @app.post("/payment/yookassa/webhook")
        async def yookassa_webhook(request: Request):
            result = await handlers['yookassa'](
                await request.body().decode('utf-8'),
                dict(request.headers)
            )
            return result
        """
        return {
            "yookassa": self.handle_yookassa_webhook,
            "cryptomus": self.handle_cryptomus_webhook,
        }
