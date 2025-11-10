from abc import ABC, abstractmethod
from typing import Optional, Any, Dict, Callable
from . import BaseGame
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
        self._game_id: Optional[int] = None

    def set_game_id(self, game_id: int):
        """Установить game_id для управления сессиями"""
        self._game_id = game_id

    @property
    def game_id(self) -> int:
        """Получить game_id"""
        if self._game_id is None:
            raise RuntimeError("game_id не установлен. Убедитесь, что вызван set_game_id()")
        return self._game_id

    @staticmethod
    async def send_initial_message(bot, user_id: int, message_id: int, text: str, game_type: str):
        """Отправить начальное сообщение с клавиатурой"""
        from bot_app.keyboards import KeyboardManager
        user_data = await bot.database_interface.get_user(user_id)
        language = user_data.get("language", "en")
        keyboard = await KeyboardManager.get_interactive_game_keyboard(game_type, language)
        try:
            await bot.bot.edit_message_text(
                chat_id=user_id,
                message_id=message_id,
                text=text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        except Exception as e:
            bot.logger.error(f"Ошибка при отправке первого сообщения: {e}")

    def get_session(self, bot, user_id: int) -> Optional[Dict[str, Any]]:
        """Получить сессию игрока из game_manager"""
        return bot.game_manager.get_interactive_session(user_id, self.game_id)

    def create_session_in_manager(self, bot, user_id: int, bet: float, bet_data: Optional[str] = None):
        """Создать сессию в game_manager"""
        session = {
            'bet': bet,
            'bet_data': bet_data,
            'balance': bet,
            'current_round': 0,
            'history': [],
            'state': {}
        }
        bot.game_manager.create_interactive_session(user_id, self.game_id, session)
        return session

    def update_session(self, bot, user_id: int, **kwargs):
        """Обновить сессию в game_manager"""
        bot.game_manager.update_interactive_session(user_id, self.game_id, **kwargs)

    @abstractmethod
    async def get_final_result_message(self, bot, user_id: int) -> Dict[str, Any]:
        """
        Получить финальный текст результата при завершении игры.
        Например:
        return "🏁 Финальная серия: 5 🔥\n💰 Выигрыш: ×32.0"
        """
        pass

    @abstractmethod
    async def get_round_state(self, bot, user_id: int) -> str:
        """Получить текущее состояние раунда для вывода"""
        pass

    @abstractmethod
    async def process_action(self, bot, user_id: int, action: str) -> Dict[str, Any]:
        """
        Обработать действие пользователя.
        Возвращает результат действия
        """
        pass

    @abstractmethod
    async def is_game_over(self, bot, user_id: int) -> bool:
        """Проверить, завершена ли игра"""
        pass

    @abstractmethod
    async def get_game_result(self, bot, user_id: int) -> tuple[float, float]:
        """Получить выигрыш и множитель при завершении"""
        pass

    def generate_result(self, bet_data: Optional[str] = None) -> Any:
        """Не используется в интерактивной игре"""
        pass

    def evaluate_result(self, result: Any, bet: float, bet_data: Optional[str] = None) -> tuple[float, float]:
        """Не используется в интерактивной игре"""
        pass

    async def create_animation(self, result: Any, bot, user_id: int, message_id: int,
                               send_frame: Optional[Callable] = None, bet_data: Optional[str] = None) -> dict[str, Any]:
        """Не используется в интерактивной игре"""
        pass
