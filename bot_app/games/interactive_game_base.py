from abc import ABC, abstractmethod
from typing import Optional, Any, Dict
from bot_app.games import BaseGame
from enum import Enum


class InteractiveGameStatus(Enum):
    """Статусы интерактивной игры"""
    WAITING_INPUT = "waiting_input"
    PROCESSING = "processing"
    ROUND_ACTIVE = "round_active"
    GAME_OVER = "game_over"


class InteractiveGameBase(BaseGame, ABC):
    """Базовый класс для интерактивных игр"""
    def __init__(self, max_bet: float, config_name: str = "honest"):
        super().__init__(max_bet, config_name)
        self.interactive_status = InteractiveGameStatus.WAITING_INPUT
        self.user_sessions: Dict[int, Dict[str, Any]] = {}

    def create_session(self, user_id: int, bet: float, bet_data: Optional[str] = None):
        """Создать сессию игры для пользователя"""
        self.user_sessions[user_id] = {
            'bet': bet,
            'bet_data': bet_data,
            'balance': bet,
            'current_round': 0,
            'history': [],
            'state': {}
        }

    def get_session(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получить сессию пользователя"""
        return self.user_sessions.get(user_id)

    def update_session(self, user_id: int, **kwargs):
        """Обновить данные сессии"""
        if user_id in self.user_sessions:
            self.user_sessions[user_id].update(kwargs)

    def delete_session(self, user_id: int):
        """Удалить сессию"""
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]

    @abstractmethod
    async def get_round_state(self, user_id: int) -> str:
        """Получить текущее состояние раунда для вывода"""
        pass

    @abstractmethod
    async def process_action(self, user_id: int, action: str) -> Dict[str, Any]:
        """
        Обработать действие пользователя.
        Возвращает результат действия
        """
        pass

    @abstractmethod
    async def is_game_over(self, user_id: int) -> bool:
        """Проверить, завершена ли игра"""
        pass

    @abstractmethod
    async def get_game_result(self, user_id: int) -> tuple[float, float]:
        """Получить выигрыш и множитель при завершении"""
        pass
