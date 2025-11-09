import asyncio

from random import random
from typing import Optional, Callable, Any
from . import BaseGame, GameStatus, GameResult, BetParameter
from .config import CoinConfig


class Coin(BaseGame):
    def __init__(self, max_bet: float, config_name: str = "honest"):
        super().__init__(max_bet, config_name)
        self.load_config()
        self.animation_settings = None
        self.icon = "🪙"
        self._name = {"ru": "Монетка", "en": "Coin"}
        self._rules = {
            "ru": (
                "ℹ️ Правила монетки\n"
                "Выберите Орёл или Решку\n"
                "При выпадении выбранной стороны получите ставку ×2"
            ),
            "en": (
                "ℹ️ Coin Rules\n"
                "Choose Heads or Tails\n"
                "If your choice drops you get bet ×2"
            )
        }

        self.need_bet_data = True
        value_param = BetParameter(
            param_type='bet_value',
            param_name={'ru': 'выберите значение', 'en': 'select value'},
            options={
                'values': [
                    {
                        'ru': 'Орёл',
                        'en': 'Heads',
                        'emoji': '🦅',
                        'value': 1,
                        'adjust': 2
                    },
                    {
                        'ru': 'Решка',
                        'en': 'Tails',
                        'emoji': '🪙',
                        'value': 0,
                        'adjust': 2
                    }
                ]
            }
        )
        self.setup_bet_data_flow(value_param)
        self.start_output = "🪙 ..."
        self.load_config()

    def load_config(self) -> None:
        """Загружает конфигурацию в зависимости от выбранного режима"""
        config_type_upper = self.config_name.upper()
        if hasattr(CoinConfig, config_type_upper):
            self.config = getattr(CoinConfig, config_type_upper)
        else:
            self.config = CoinConfig.HONEST
        self.animation_settings = CoinConfig.ANIMATION_SETTINGS

    def get_config_info(self) -> str:
        """Возвращает информацию о текущей конфигурации"""
        config = self.config
        rtp = config.get('rtp', 95)
        house_edge = config.get('house_edge', 5)
        info = (
            f"{config.get('name', 'Монетка')}\n"
            f"{config.get('description', '')}\n\n"
            f"💰 RTP: {rtp}%\n"
            f"🎯 House Edge: {house_edge}%\n"
            f"🎲 Множитель выигрыша: ×2"
        )
        return info

    async def play(self, bot, user_id: int, message_id: int,
                   bet: float, bet_data: Optional[str] = None, send_frame: Optional[Callable] = None) -> GameResult:
        """Запуск игры монетка"""
        self.game_over = False
        self.current_status = GameStatus.RUNNING
        result = self.generate_result(bet_data)
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
        Генерирует результат монетки с правильным расчётом вероятности.
        RTP контролирует вероятность выигрыша игрока прямо.

        Возвращает 1 (Орёл) или 0 (Решка)
        """
        config = self.config
        rtp = config.get('rtp', 95) / 100.0
        win_probability = rtp / 2.0
        win_probability = max(0.0, min(1.0, win_probability))
        random_value = random()
        user_choice = int(bet_data.split(':')[1])
        if random_value < win_probability:
            return user_choice
        else:
            return 0 if user_choice == 1 else 1

    def evaluate_result(self, result: int, bet: float, bet_data: Optional[str] = None) -> tuple[float, float]:
        """Оценивает ставку и возвращает выигрыш и множитель"""
        payout = 0
        multiplier = 0

        if bet_data:
            try:
                bet_value = int(bet_data.split(':')[1])
                if result == bet_value:
                    payout = bet * 2
                    multiplier = 2
                else:
                    payout = 0
                    multiplier = 0
            except (ValueError, IndexError):
                payout = 0
                multiplier = 0

        return payout, multiplier

    async def create_animation(self, result: int, bot, user_id: int,
                               message_id: int, send_frame: Optional[Callable] = None) -> dict[str, Any]:
        """
        Показывает быструю и красивую анимацию кручения монетки.
        """
        total_steps = 8
        frame_time = 0.06
        animation_frames = []
        frame_times = []
        start_frame = self.start_output

        if send_frame:
            await send_frame(bot, user_id, message_id, start_frame)
        animation_frames.append(start_frame)

        spinner_chars = ['◐', '◓', '◑', '◒']
        sides = ["🦅", "🪙"]

        for step in range(total_steps):
            side = sides[step % 2]
            spinner = spinner_chars[step % len(spinner_chars)]
            frame = f"🪙 {spinner} {side}"

            if send_frame:
                await send_frame(bot, user_id, message_id, frame)
            animation_frames.append(frame)
            frame_times.append(frame_time)
            await asyncio.sleep(frame_time)

        result_side = "🦅" if result == 1 else "🪙"
        final_frame = f"✨ {result_side} ✨"

        if send_frame:
            await send_frame(bot, user_id, message_id, final_frame)
        animation_frames.append(final_frame)

        return {
            'total_frames': len(animation_frames),
            'final_result': result_side,
            'animation_duration': sum(frame_times),
            "icon": self.icon
        }

    def _get_game_data(self, result: int, bet_data: Optional[str] = None) -> dict[str, Any]:
        """Создает структуру game_data для монетки"""
        bet_value = None
        if bet_data:
            try:
                bet_value = int(bet_data.split(':')[1])
            except (ValueError, IndexError):
                pass

        result_side = "heads" if result == 1 else "tails"
        return {
            'result': result_side,
            'bet_value': "🦅" if bet_value == 1 else "🪙" if bet_value == 0 else None,
            'result_code': result
        }
