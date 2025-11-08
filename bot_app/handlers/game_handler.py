from typing import Dict, Optional, Type, Callable, Any
from datetime import datetime
import logging

from bot_app.database import DatabaseInterface
from bot_app.games import BaseGame, GameResult


class GameManager:
    """Менеджер для управления играми"""
    def __init__(self, db_interface: DatabaseInterface, logger: logging.Logger):
        self.db_interface = db_interface
        self.logger = logger
        self.games: Dict[int, Type[BaseGame]] = {}
        self.active_sessions: Dict[int, Dict[str, Any]] = {}
        self.game_callbacks: Dict[str, list[Callable[[Any], Any]]] = {
            'on_game_start': [],
            'on_game_end': [],
            'on_game_error': []
        }

    def register_game(self, game_id: int, game_class: Type[BaseGame]) -> None:
        if game_id in self.games:
            self.logger.warning(f"Game {game_id} is already registered")
        self.games[game_id] = game_class
        self.logger.info(f"Registered game {game_id}'")

    def register_games(self, games: Dict[int, Type[BaseGame]]) -> None:
        for game_id, game_class in games.items():
            self.register_game(game_id, game_class)

    async def get_game(self, game_id: int) -> Optional[BaseGame]:
        if game_id not in self.games:
            self.logger.error(f"Game {game_id} not registered")
            return None
        game_class = self.games[game_id]
        config = await self.db_interface.get_config(game_id)
        return game_class(config)

    def get_available_games(self) -> Dict[int, Type[BaseGame]]:
        """Получить все доступные игры"""
        return self.games.copy()

    def on_game_start(self, callback: Callable[[Dict[str, Any]], Any]) -> None:
        """Регистрация callback при начале игры"""
        self.game_callbacks['on_game_start'].append(callback)

    def on_game_end(self, callback: Callable[[GameResult, Dict[str, Any]], Any]) -> None:
        """Регистрация callback при окончании игры"""
        self.game_callbacks['on_game_end'].append(callback)

    def on_game_error(self, callback: Callable[[Exception, Dict[str, Any]], Any]) -> None:
        """Регистрация callback при ошибке"""
        self.game_callbacks['on_game_error'].append(callback)

    async def _call_callbacks(self, callback_type: str, *args) -> None:
        """Вызов всех callback функций"""
        for callback in self.game_callbacks.get(callback_type, []):
            try:
                if hasattr(callback, '__call__'):
                    result = callback(*args)
                    if hasattr(result, '__await__'):
                        await result
            except Exception as e:
                self.logger.error(f"Ошибка при вызове {callback_type}: {e}")

    async def start_game(self, bot, user_id: int, message_id: int, game_id: int, bet: float,
                         bet_date: Optional[str] = None, send_frame: Optional[Callable] = None) -> Optional[GameResult]:
        """
        Запуск игры

        :param bot: Экземпляр бота
        :param user_id: ID пользователя
        :param message_id: ID сообщения
        :param game_id: ID игры
        :param bet: Размер ставки
        :param bet_date: Данные ставки
        :param send_frame: Callback для отправки кадров анимации
        :return: GameResult или None в случае ошибки
        """
        if user_id in self.active_sessions:
            self.logger.warning(f"Пользователь {user_id} уже играет")
            return None

        game = await self.get_game(game_id)
        if not game:
            return None

        if not (game.min_bet <= bet <= game.max_bet):
            self.logger.error(f"Ставка {bet} вне допустимых лимитов [{game.min_bet}, {game.max_bet}]")
            return None

        session = {
            'user_id': user_id,
            'game_id': game_id,
            'bet_amount': bet,
            'started_at': datetime.now()
        }
        self.active_sessions[user_id] = session
        try:
            await self._call_callbacks('on_game_start', session)
            result = await game.play(bot, user_id, message_id, bet, bet_date, send_frame)
            await self._call_callbacks('on_game_end', result, session)
            self.logger.info(f"Пользователь {user_id} завершил игру {game_id}. Выигрыш: {result.win_amount}")
            return result

        except Exception as e:
            self.logger.error(f"Ошибка при запуске игры: {e}", exc_info=True)
            await self._call_callbacks('on_game_error', e, session)
            return None

        finally:
            self.active_sessions.pop(user_id, None)

    def is_user_playing(self, user_id: int) -> bool:
        """Проверить, играет ли пользователь"""
        return user_id in self.active_sessions

    def get_user_session(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получить активную сессию пользователя"""
        return self.active_sessions.get(user_id)
