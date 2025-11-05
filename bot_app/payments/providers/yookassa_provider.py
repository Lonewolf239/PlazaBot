import logging
from typing import Dict, Any, TypedDict, Optional

from yookassa import Configuration, Payment
from yookassa.domain.exceptions import ApiError
from yookassa.domain.notification import WebhookNotification

from .base_provider import IProvider
from bot_app.database.db_manager import DatabaseInterface
from bot_app.utils.transaction_statuses import TransactionStatus


class ReceiptCustomer(TypedDict, total=False):
    """Данные покупателя для чека."""
    email: str


class ReceiptItem(TypedDict, total=False):
    """Элемент в чеке."""
    description: str
    quantity: str
    amount: Dict[str, str]
    vat_code: int


class ReceiptData(TypedDict, total=False):
    """Структура данных для чека."""
    customer: ReceiptCustomer
    items: list


class YookassaProvider(IProvider):
    """Провайдер платежей для системы Yookassa."""

    PROVIDER_NAME = "yookassa"

    def __init__(self, logger: logging.Logger, bot, database_interface: DatabaseInterface,
                 yookassa_config: Dict[str, str]):
        """
        Инициализирует YookassaProvider.
        :param logger: Экземпляр логгера.
        :param bot: Экземпляр бота (для отправки сообщений пользователям).
        :param database_interface: Интерфейс для работы с базой данных.
        :param yookassa_config: Словарь с конфигурацией Yookassa (account_id, secret_key, return_url, webhook_url, receipt_vat_code).
        """
        super().__init__()
        self.has_deposit = True
        self.logger = logger
        self.bot = bot
        self.database_interface = database_interface
        self.yookassa_config = yookassa_config

        Configuration.account_id = self.yookassa_config.get("account_id")
        Configuration.secret_key = self.yookassa_config.get("secret_key")
        self.return_url = self.yookassa_config.get("return_url")
        self.webhook_url = self.yookassa_config.get("webhook_url")
        self.receipt_vat_code = self.yookassa_config.get("receipt_vat_code", 1)

        if not Configuration.account_id or not Configuration.secret_key:
            self.logger.error("YookassaProvider: Configuration error. Account ID or Secret Key is missing.")

    def get_provider_name(self) -> str:
        """Возвращает имя провайдера."""
        return self.PROVIDER_NAME

    def _build_receipt_data(self, user_email: Optional[str], amount: float, currency: str) -> Optional[Dict[str, Any]]:
        """
        ИСПРАВЛЕНО: Отдельный метод для построения данных чека с правильной типизацией.

        :param user_email: Email пользователя для чека
        :param amount: Сумма платежа
        :param currency: Валюта платежа
        :return: Словарь с данными чека или None если email не предоставлен
        """
        if not user_email:
            return None

        receipt: Dict[str, Any] = {
            "customer": {
                "email": user_email
            },
            "items": [
                {
                    "description": "Пополнение баланса",
                    "quantity": "1.00",
                    "amount": {
                        "value": f"{amount:.2f}",
                        "currency": currency
                    },
                    "vat_code": self.receipt_vat_code
                }
            ]
        }
        return receipt

    async def deposit(self, user_id: int, amount: float,
                      internal_transaction_id: str, currency: str = "RUB") -> Dict[str, Any]:
        """
        Инициирует платеж в Yookassa для пополнения баланса.
        :param user_id: ID пользователя.
        :param amount: Сумма пополнения.
        :param internal_transaction_id: Наш внутренний UUID транзакции.
        :param currency: Валюта платежа (по умолчанию "RUB").
        :return: Словарь с результатом операции (status, url, provider_transaction_id, transaction_id).
        """
        self.logger.info(
            f"YookassaProvider: Initiating deposit for user {user_id}, amount {amount:.2f} {currency}, TxID: {internal_transaction_id}")

        user_email = await self.database_interface.get_email(user_id)

        receipt_data = self._build_receipt_data(user_email, amount, currency)

        try:
            payment_data: Dict[str, Any] = {
                "amount": {"value": f"{amount:.2f}", "currency": currency},
                "confirmation": {
                    "type": "redirect",
                    "return_url": self.return_url
                },
                "capture": True,
                "description": f"Пополнение баланса пользователя {user_id}",
                "metadata": {"user_id": user_id, "transaction_id": internal_transaction_id},
            }

            if receipt_data is not None:
                payment_data["receipt"] = receipt_data

            payment = Payment.create(payment_data)
            payment_id = payment.id
            confirmation_url = payment.confirmation.confirmation_url

            self.logger.info(
                f"YookassaProvider: Successfully created payment. Yookassa ID: {payment_id}, "
                f"Confirmation URL: {confirmation_url}, UserID: {user_id}, TxID: {internal_transaction_id}")

            return {
                "status": "pending_confirmation",
                "url": confirmation_url,
                "provider_transaction_id": payment_id,
                "transaction_id": internal_transaction_id
            }

        except ApiError as e:
            self.logger.error(f"YookassaProvider API Error creating payment: {e}", exc_info=True)
            await self.database_interface.update_transaction_status(
                transaction_id=internal_transaction_id,
                status=TransactionStatus.DEPOSIT_FAILED,
                message=f"Yookassa API error: {e}"
            )
            return {
                "status": TransactionStatus.DEPOSIT_FAILED,
                "message": f"Yookassa API error: {e}",
                "transaction_id": internal_transaction_id
            }
        except Exception as e:
            self.logger.error(f"YookassaProvider Unexpected error creating payment: {e}", exc_info=True)
            await self.database_interface.update_transaction_status(
                transaction_id=internal_transaction_id,
                status=TransactionStatus.DEPOSIT_FAILED,
                message=f"An internal error occurred: {e}"
            )
            return {
                "status": TransactionStatus.DEPOSIT_FAILED,
                "message": f"An internal error occurred: {e}",
                "transaction_id": internal_transaction_id
            }

    async def handle_deposit_notification(self, notification_data: dict, db_interface: DatabaseInterface, bot,
                                          logger: logging.Logger) -> Dict[str, Any]:
        """
        Обрабатывает входящие уведомления от Yookassa о статусе платежа.
        :param notification_data: Словарь с данными уведомления.
        :param db_interface: Интерфейс базы данных.
        :param bot: Экземпляр бота.
        :param logger: Логгер.
        :return: Словарь с результатом обработки (status, message).
        """
        logger.info(f"YookassaProvider: Received notification: {notification_data}")
        try:
            notification_object = WebhookNotification(notification_data)

            payment = notification_object.object
            payment_id = payment.id

            if not payment.metadata or not payment.metadata.get("transaction_id"):
                logger.error(
                    f"YookassaProvider: Missing 'transaction_id' in metadata for payment {payment_id}. Notification data: {notification_data}")
                return {"status": "failed", "message": "Missing transaction ID in metadata."}

            internal_transaction_id = payment.metadata.get("transaction_id")

            transaction_record = await db_interface.get_provider_transaction(internal_transaction_id)
            if not transaction_record:
                logger.error(
                    f"YookassaProvider: Internal transaction {internal_transaction_id} not found for payment {payment_id}.")
                return {"status": "failed", "message": "Internal transaction not found."}

            user_id = transaction_record.get("user_id")
            amount = float(transaction_record.get("amount"))
            currency = transaction_record.get("currency", "RUB")
            current_status_in_db = transaction_record.get("status")

            if current_status_in_db in [TransactionStatus.PENDING_PAYMENT_CONFIRMATION,
                                        TransactionStatus.DEPOSIT_SUCCEEDED,
                                        TransactionStatus.DEPOSIT_FAILED,
                                        TransactionStatus.PAYMENT_CANCELED]:
                logger.info(
                    f"YookassaProvider: Payment {payment_id} (TxID: {internal_transaction_id}) already processed with status {current_status_in_db}. Skipping notification.")
                return {
                    "status": "already_processed",
                    "message": f"Payment already processed with status: {current_status_in_db}"
                }

            event = notification_object.event

            if event == "payment.succeeded":
                if current_status_in_db == TransactionStatus.PENDING_PAYMENT_INIT or \
                        current_status_in_db == TransactionStatus.PENDING_PAYMENT_CONFIRMATION:
                    success = await db_interface.update_balance(
                        user_id, amount, transaction_type="deposit",
                        description=f"Deposit via {self.PROVIDER_NAME}, Yookassa ID: {payment_id}"
                    )
                    if not success:
                        logger.error(
                            f"YookassaProvider: Failed to update balance for user {user_id} after payment {payment_id}.")
                        await db_interface.update_transaction_status(
                            transaction_id=internal_transaction_id,
                            status=TransactionStatus.INTERNAL_ERROR,
                            message="Balance update failed."
                        )
                        return {"status": "internal_error", "message": "Failed to update user balance."}
                    await db_interface.update_transaction_status(
                        transaction_id=internal_transaction_id,
                        status=TransactionStatus.DEPOSIT_SUCCEEDED
                    )
                    await bot.send_message(user_id, f"Ваш баланс успешно пополнен на {amount:.2f} {currency}.")
                    logger.info(
                        f"YookassaProvider: Payment {payment_id} (TxID: {internal_transaction_id}) succeeded. User {user_id} balance updated by {amount:.2f} {currency}.")
                    return {"status": "succeeded", "message": "Deposit successfully processed."}
                else:
                    logger.warning(
                        f"YookassaProvider: Payment {payment_id} (TxID: {internal_transaction_id}) succeeded, but internal status is '{current_status_in_db}'. Ignoring.")
                    return {"status": "skipped", "message": "Payment succeeded, but internal status did not match."}

            elif event == "payment.canceled":
                if current_status_in_db == TransactionStatus.PENDING_PAYMENT_INIT or \
                        current_status_in_db == TransactionStatus.PENDING_PAYMENT_CONFIRMATION:
                    await db_interface.update_transaction_status(
                        transaction_id=internal_transaction_id,
                        status=TransactionStatus.PAYMENT_CANCELED
                    )
                    await bot.send_message(user_id, "Оплата была отменена.")
                    logger.info(
                        f"YookassaProvider: Payment {payment_id} (TxID: {internal_transaction_id}) canceled by user {user_id}.")
                    return {"status": "canceled", "message": "Deposit canceled."}
                else:
                    logger.warning(
                        f"YookassaProvider: Payment {payment_id} (TxID: {internal_transaction_id}) canceled, but internal status is '{current_status_in_db}'. Ignoring.")
                    return {"status": "skipped", "message": "Payment canceled, but internal status did not match."}

            elif event == "payment.waiting_for_refund":
                logger.warning(
                    f"YookassaProvider: Payment {payment_id} (TxID: {internal_transaction_id}) is waiting for refund. Current status: {current_status_in_db}")
                return {"status": "refund_pending", "message": "Payment is waiting for refund."}

            elif event == "refund.succeeded":
                logger.info(
                    f"YookassaProvider: Refund succeeded for payment {payment_id} (TxID: {internal_transaction_id}). Current status: {current_status_in_db}")

                if current_status_in_db == TransactionStatus.DEPOSIT_SUCCEEDED:
                    success = await db_interface.update_balance(
                        user_id, -amount, transaction_type="deposit_refund",
                        description=f"Refund for deposit, Yookassa ID: {payment_id}"
                    )

                    if not success:
                        logger.error(
                            f"YookassaProvider: Failed to update balance (refund) for user {user_id} after payment {payment_id}.")
                        await db_interface.update_transaction_status(
                            transaction_id=internal_transaction_id,
                            status=TransactionStatus.INTERNAL_ERROR,
                            message="Balance update failed for refund."
                        )
                        return {"status": "internal_error", "message": "Failed to update user balance for refund."}

                    await db_interface.update_transaction_status(
                        transaction_id=internal_transaction_id,
                        status=TransactionStatus.DEPOSIT_REFUNDED
                    )

                    await bot.send_message(user_id, f"Ваш депозит на сумму {amount:.2f} {currency} был возвращен.")
                    return {"status": "refund_succeeded", "message": "Deposit successfully refunded."}
                else:
                    return {
                        "status": "refund_succeeded",
                        "message": "Refund completed, but deposit was not in succeeded state."
                    }

            else:
                logger.warning(
                    f"YookassaProvider: Received unknown notification event: {event} for payment {payment_id} "
                    f"(TxID: {internal_transaction_id}).")
                return {"status": "unknown_event", "message": f"Unknown event: {event}"}

        except ApiError as e:
            logger.error(f"YookassaProvider API Error processing notification: {e}", exc_info=True)
            return {"status": "failed", "message": f"Yookassa API error: {e}"}
        except Exception as e:
            logger.error(f"YookassaProvider Unexpected error processing notification: {e}", exc_info=True)
            return {"status": "failed", "message": f"An internal error occurred: {e}"}

    async def withdraw(self, user_id: int, amount: float, internal_transaction_id: str,
                       currency: str = "RUB") -> Dict[str, Any]:
        """
        Инициирует вывод средств через Yookassa.
        Yookassa API не поддерживает прямые выводы средств пользователям (P2P).
        Этот метод должен быть адаптирован для интеграции с сервисами, которые поддерживают вывод.
        В текущей реализации, метод вернет ошибку.
        :param user_id: ID пользователя.
        :param amount: Сумма вывода.
        :param internal_transaction_id: Наш внутренний UUID транзакции.
        :param currency: Валюта вывода.
        :return: Словарь с результатом операции.
        """
        self.logger.warning(
            f"YookassaProvider: Withdrawal is not directly supported by Yookassa API for P2P. UserID: {user_id}, "
            f"Amount: {amount:.2f} {currency}, TxID: {internal_transaction_id}")

        # TODO: Интегрировать с сервисом, который осуществляет реальные выводы, если Yookassa не используется для этого.
        error_message = "Withdrawal via Yookassa is not directly supported for P2P operations."
        await self.database_interface.update_transaction_status(
            transaction_id=internal_transaction_id,
            status=TransactionStatus.WITHDRAWAL_FAILED,
            message=error_message
        )

        return {
            "status": TransactionStatus.WITHDRAWAL_FAILED,
            "message": error_message,
            "transaction_id": internal_transaction_id
        }

    async def handle_withdrawal_callback(self, transaction_id: str, status: str,
                                         details: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Обрабатывает коллбэк о статусе вывода средств.
        Yookassa не предоставляет прямых уведомлений для статусов вывода средств.
        :param transaction_id: Наш внутренний UUID транзакции.
        :param status: Финальный статус вывода ("succeeded", "failed", "canceled").
        :param details: Дополнительные детали.
        :return: Словарь с результатом обработки.
        """
        self.logger.warning(
            f"YookassaProvider: handle_withdrawal_callback called for TxID {transaction_id}. Status: {status}. Details: {details}")

        message = details.get('message',
                              'Withdrawal status callback received.') if details else 'Withdrawal status callback received.'

        if status == "failed" and details and "reason" in details:
            message = f"Withdrawal failed: {details['reason']}"

        return {
            "status": "processed",
            "message": message
        }
