import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Any, Optional
from enum import Enum


class GameStatus(Enum):
    """Статусы игры"""
    WAITING = "waiting"
    RUNNING = "running"
    FINISHED = "finished"


@dataclass
class GameResult:
    """Результат игры"""
    status: GameStatus
    win_amount: int
    bet_amount: int
    multiplier: float
    is_win: bool
    game_data: dict[str, Any]
    animations_data: Optional[dict[str, Any]] = None
    bet_date: Optional[str] = None


class BaseGame(ABC):
    """Базовый класс для всех игр"""
    def __init__(self, config: str = "honest"):
        self.icon = ""
        self._name = {"ru": "", "en": ""}
        self._rules = {"ru": "", "en": ""}
        self.config = config
        self.min_bet = 0.1
        self.max_bet = 5000
        self.frame_time = 0
        self.game_over: bool = False
        self.current_status: GameStatus = GameStatus.WAITING
        self._result_handlers: list[Callable[[GameResult], Any]] = []

    @abstractmethod
    def get_config_info(self) -> str:
        """Получить информацию о конфигурации"""
        return ""

    def name(self, language: str):
        return self._name[language]

    def rules(self, language: str):
        return self._rules[language]

    def register_result_handler(self, handler: Callable[[GameResult], Any]) -> None:
        """Регистрация обработчика результата"""
        self._result_handlers.append(handler)

    async def _call_result_handlers(self, result: GameResult) -> None:
        """Вызов всех зарегистрированных обработчиков"""
        for handler in self._result_handlers:
            if asyncio.iscoroutinefunction(handler):
                await handler(result)
            else:
                handler(result)

    @abstractmethod
    async def play(self, bot, user_id: int, message_id: int,
                   bet: float, bet_date: Optional[str] = None, send_frame: Optional[Callable] = None) -> GameResult:
        """Запуск игры. Должен быть переопределен в подклассах"""
        pass

    async def _finalize_game(self, result: GameResult) -> GameResult:
        """Финализация игры и вызов обработчиков"""
        self.game_over = True
        self.current_status = GameStatus.FINISHED
        await self._call_result_handlers(result)
        return result
