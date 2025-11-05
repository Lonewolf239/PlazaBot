from abc import ABC, abstractmethod
from typing import Dict, Any
import logging


class IProvider(ABC):
    """
    Базовый интерфейс для всех провайдеров платежей.
    Определяет методы, которые должны быть реализованы каждым провайдером.
    """
    def __init__(self):
        self.has_deposit = False
        self.has_withdraw = False

    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Возвращает уникальное имя провайдера.
        :return: Строка с именем провайдера (например, "yookassa", "cryptomus")
        """
        pass

    @abstractmethod
    async def deposit(self, user_id: int, amount: float, internal_transaction_id: str,
                      currency: str = "RUB") -> Dict[str, Any]:
        """
        Инициирует пополнение баланса через провайдера.
        Возвращает словарь с информацией для пользователя (например, URL для оплаты).

        :param user_id: ID пользователя
        :param amount: Сумма пополнения
        :param internal_transaction_id: Наш внутренний UUID транзакции для привязки
        :param currency: Валюта платежа (по умолчанию "RUB")
        :return: Словарь с результатом операции
                {
                    "status": "pending_confirmation",  # или другой статус
                    "url": "https://payment.url",      # URL для переадресации пользователя
                    "provider_transaction_id": "external_id",  # ID платежа от провайдера
                    "transaction_id": internal_transaction_id,
                    "message": "optional message"
                }
        """
        pass

    @abstractmethod
    async def handle_deposit_notification(self, notification_data: dict, db_interface, bot,
                                          logger: logging.Logger) -> Dict[str, Any]:
        """
        Обрабатывает входящие уведомления (webhook) от провайдера о статусе пополнения.
        Должен вернуть результат обработки (например, статус транзакции).

        :param notification_data: Словарь с данными уведомления от провайдера
        :param db_interface: Интерфейс для работы с базой данных
        :param bot: Экземпляр бота для отправки сообщений пользователям
        :param logger: Логгер для записи событий
        :return: Словарь с результатом обработки
                {
                    "status": "succeeded" | "failed" | "already_processed",
                    "message": "описание результата"
                }
        """
        pass

    @abstractmethod
    async def withdraw(self, user_id: int, amount: float, internal_transaction_id: str,
                       currency: str = "RUB") -> Dict[str, Any]:
        """
        Инициирует вывод средств через провайдера.
        Возвращает словарь с информацией о статусе операции.

        :param user_id: ID пользователя
        :param amount: Сумма вывода
        :param internal_transaction_id: Наш внутренний UUID транзакции для привязки
        :param currency: Валюта вывода (по умолчанию "RUB")
        :return: Словарь с результатом операции
                {
                    "status": "pending_review" | "succeeded" | "failed",
                    "message": "описание статуса",
                    "provider_transaction_id": "external_id",  # ID операции от провайдера
                    "transaction_id": internal_transaction_id
                }
        """
        pass

    @abstractmethod
    async def handle_withdrawal_callback(self, transaction_id: str, status: str,
                                         details: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Обрабатывает callback или уведомление о статусе вывода средств.
        Вызывается из payment_gateway.complete_withdrawal() при финализации операции.

        :param transaction_id: Наш внутренний UUID транзакции
        :param status: Финальный статус ("succeeded", "failed", "canceled")
        :param details: Словарь с дополнительными деталями
                       {
                           "user_id": int,
                           "amount": float,
                           "currency": str,
                           "reason": "optional reason for failure"
                       }
        :return: Словарь с результатом обработки
                {
                    "status": "processed" | "failed",
                    "message": "описание результата"
                }
        """
        pass
