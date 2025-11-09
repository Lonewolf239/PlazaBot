import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, Any, Optional, Dict, List
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
    user_bet: str
    multiplier: float
    is_win: bool
    game_data: dict[str, Any]
    animations_data: Optional[dict[str, Any]] = None
    bet_data: Optional[str] = None


@dataclass
class BetParameter:
    """Один параметр ставки"""
    param_type: str
    param_name: Dict[str, str]
    options: Dict[str, Any]
    is_required: bool = True
    default_value: Optional[str] = None
    validation_func: Optional[Callable] = None


@dataclass
class BetDataFlow:
    """Конфигурация потока получения bet_data"""
    parameters: List[BetParameter] = field(default_factory=list)

    def add_parameter(self, parameter: BetParameter):
        self.parameters.append(parameter)

    def get_next_parameter(self, current_index: int) -> Optional[BetParameter]:
        if current_index < len(self.parameters) - 1:
            return self.parameters[current_index + 1]
        return None

    def is_complete(self, current_index: int) -> bool:
        return current_index >= len(self.parameters) - 1


class BetDataConfig:
    """Конфигурация получения bet_data для игры"""
    need_bet_data: bool = False
    bet_data_type: str = None
    bet_data_options: dict = None


class BaseGame(ABC):
    """Базовый класс для всех игр"""
    def __init__(self, max_bet: float, config_name: str = "honest"):
        self.icon = ""
        self._name = {"ru": "", "en": ""}
        self._rules = {"ru": "", "en": ""}
        self.config_name = config_name
        self.config = None
        self.max_bet = max_bet
        self.frame_time = 0
        self.bet_data_flow: Optional[BetDataFlow] = None
        self.need_bet_data: bool = False
        self.bet_data_type = ""
        self.bet_data_options = {}
        self.game_over: bool = False
        self.current_status: GameStatus = GameStatus.WAITING
        self._result_handlers: list[Callable[[GameResult], Any]] = []
        self.start_frame_time = 0.03

    def setup_bet_data_flow(self, *parameters: BetParameter):
        """Настройка потока получения bet_data"""
        self.bet_data_flow = BetDataFlow()
        for param in parameters:
            self.bet_data_flow.add_parameter(param)
        self.need_bet_data = len(parameters) > 0

    @abstractmethod
    def load_config(self):
        pass

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
    async def play(self, bot, user_id: int, message_id: int, bet: float,
                   bet_data: Optional[str] = None, send_frame: Optional[Callable] = None) -> GameResult:
        """Запуск игры. Должен быть переопределен в подклассах"""
        pass

    @abstractmethod
    def generate_result(self, bet_data: Optional[str] = None) -> Any:
        """
        Генерирует результат раунда.

        Returns:
            Any: Результат игры (тип зависит от конкретной игры)
        """
        pass

    @abstractmethod
    def evaluate_result(self, result: Any, bet: float, bet_data: Optional[str] = None) -> tuple[float, float]:
        """
        Оценивает результат и возвращает выигрыш и множитель.

        Args:
            result: Результат игры из generate_result()
            bet: Размер ставки
            bet_data: Дополнительные данные ставки

        Returns:
            tuple: (win_amount, multiplier)
        """
        pass

    @abstractmethod
    async def create_animation(self, result: Any, bot, user_id: int,
                               message_id: int, send_frame: Optional[Callable] = None) -> dict[str, Any]:
        """
        Создает анимацию игры.

        Args:
            result: Результат из generate_result()
            bot: Бот объект
            user_id: ID пользователя
            message_id: ID сообщения
            send_frame: Функция для отправки кадров

        Returns:
            dict: Данные анимации
        """
        pass

    @abstractmethod
    def _get_game_data(self, result: Any, bet_data: Optional[str]) -> dict[str, Any]:
        """
        Создает структуру game_data для результата.

        Args:
            result: Результат игры
            bet_data: Данные ставки

        Returns:
            dict: Структурированные данные игры
        """
        pass

    async def _finalize_game(self, result: GameResult) -> GameResult:
        """Финализация игры и вызов обработчиков"""
        self.game_over = True
        self.current_status = GameStatus.FINISHED
        await self._call_result_handlers(result)
        return result
