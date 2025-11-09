from random import random, choice, shuffle
from typing import Optional, Callable, Any

from . import BaseGame, BetParameter, GameResult, GameStatus
from .config import RouletteV2Config


class RoulerreV2(BaseGame):
    def __init__(self, max_bet: float, config_name: str = "honest"):
        """
        Инициализация рулетки

        :param config_name: 'honest', 'aggressive' или 'generous'
        """
        super().__init__(max_bet, config_name)
        self.load_config()
        self.icon = "🎡"
        self._name = {"ru": "Рулетка V2", "en": "Roulette V2"}
        self._rules = {
            "ru": (
                "ℹ️ Правила рулетки V2\n"
            ),
            "en": (
                "ℹ️ Roulette Rules V2\n"
            )
        }
        self.numbers = list(range(100))
        self.need_bet_data = True
        bet_value_param = BetParameter(
            param_type='bet_value',
            param_name={'ru': 'выберите значение', 'en': 'select value'},
            options={
                'values':
                    {
                        'ru': 'Числа 0-99',
                        'en': 'Numbers 0-36',
                        'emoji': '🔢',
                        'value': list(range(100)),
                        'bet_type': 'number',
                        'adjust': 6
                    }
            }
        )
        self.setup_bet_data_flow(bet_value_param)
        self.start_output = "🎡 ..."
        self.load_config()

    def load_config(self) -> None:
        """Загружает конфигурацию в зависимости от выбранного режима"""
        config_type_upper = self.config_name.upper()
        if hasattr(RouletteV2Config, config_type_upper):
            self.config = getattr(RouletteV2Config, config_type_upper)
        else:
            self.config = "RouletteV2Config.HONEST"

    def get_config_info(self) -> str:
        """Возвращает информацию о текущей конфигурации"""
        config = self.config
        multipliers = config['multipliers']
        probabilities = config['probabilities']
        info = ""
        return info

    async def play(self, bot, user_id: int, message_id: int,
                   bet: float, bet_data: Optional[str] = None, send_frame: Optional[Callable] = None) -> GameResult:
        """Запуск рулетки"""
        self.game_over = False
        self.current_status = GameStatus.RUNNING

        result = self.generate_result()
        win_amount, multiplier = self.evaluate_result(result, bet, bet_data)
        animation_data = await self.create_animation(result, bot, user_id,
                                                     message_id, send_frame)

        game_data = self._get_game_data(result, bet_data)

        game_result = GameResult(
            status=GameStatus.FINISHED,
            win_amount=win_amount,
            bet_amount=bet,
            user_bet=game_data["bet_value"],
            multiplier=multiplier,
            is_win=win_amount > 0,
            game_data=game_data,
            animations_data=animation_data,
            bet_data=bet_data
        )

        return await self._finalize_game(game_result)

    def generate_result(self, bet_data: Optional[str] = None) -> int:
        """
        Симулирует кручение колеса рулетки с учётом конфигурации
        Использует вероятности и смещения цвета из config
        """
        config = self.config
        probabilities = config['probabilities']
        rand = random()
        if rand < probabilities['number_win'] * 1 / 37:
            return 0
        numbers = list(range(100))
        return choice(numbers)

    def evaluate_result(self, result: int, bet: float, bet_data: Optional[str] = None) -> tuple[float, float]:
        """Оценивает ставку и возвращает выигрыш и множитель"""
        payout = 0
        if bet_data:
            try:
                bet_value = bet_data.split(':')[1]
                if result == bet_value:
                    payout = 100
            except (ValueError, IndexError, KeyError):
                payout = 0
        multiplier = payout / bet if bet > 0 else 0
        return payout, multiplier

    async def create_animation(self, result: int, bot, user_id: int,
                               message_id: int, send_frame: Optional[Callable] = None) -> dict[str, Any]:
        """
        Показывает анимацию кручения рулетки с плавным замедлением.

        :param result: Итоговый номер рулетки
        :param bot: Объект бота
        :param user_id: ID пользователя
        :param message_id: ID сообщения для обновления
        :param send_frame: Callback для отправки фреймов
        :return: Словарь с данными анимации
        """
        animation_frames = []
        frame_times = []
        start_frame = self.start_output
        if send_frame:
            await send_frame(bot, user_id, message_id, start_frame)
        animation_frames.append(start_frame)
        wheel = []
        for _ in range(3):
            rotated = self.numbers.copy()
            shuffle(rotated)
            wheel.extend(rotated)
        final_frame = f"🎡 ✓ {result:2d}  "
        if send_frame:
            await send_frame(bot, user_id, message_id, final_frame)

        animation_frames.append(final_frame)

        return {
            'total_frames': len(animation_frames),
            'final_result': f"{result:2d}  ",
            'animation_duration': sum(frame_times),
            "icon": self.icon
        }

    def _get_game_data(self, result: int, bet_data: Optional[str] = None) -> dict[str, Any]:
        """Создает структуру game_data для рулетки"""
        bet_parts = bet_data.split(";")
        bet_type = bet_parts[0].split(':')[1]
        bet_value = bet_parts[1].split(':')[1]
        return {
            'result': result,
            'bet_type': bet_type if bet_data else None,
            'bet_value': bet_value if bet_data else None
        }
