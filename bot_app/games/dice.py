import asyncio

from random import randint

from typing import Optional, Callable, Any

from . import BaseGame, GameStatus, GameResult, BetParameter
from .config import DiceConfig


class Dice(BaseGame):
    def __init__(self, max_bet: float, config_name: str = "honest"):
        super().__init__(max_bet, config_name)
        self.load_config()
        self.animation_settings = None
        self.icon = "🎲"
        self._name = {"ru": "Кости", "en": "Dice"}
        self._rules = {
            "ru": (
                "ℹ️ Правила Костей\n"
                "Бросаются два кубика. Выберите тип ставки и предскажите результат!"
            ),
            "en": (
                "ℹ️ Dice Rules\n"
                "Two dice are rolled. Choose a bet type and predict the result!"
            )
        }
        self.numbers = list(range(2, 13))
        self.need_bet_data = True
        bet_type_param = BetParameter(
            param_type='bet_type',
            param_name={'ru': 'тип ставки', 'en': 'bet type'},
            options={
                'values': [
                    {'ru': 'Сумма', 'en': 'Sum', 'value': 'sum', 'emoji': '➕', 'adjust': 2},
                    {'ru': 'Четность', 'en': 'Parity', 'value': 'parity', 'emoji': '⚖️', 'adjust': 2},
                    {'ru': 'Дубль', 'en': 'Doubles', 'value': 'doubles', 'emoji': '🎲🎲', 'adjust': 2},
                    {'ru': 'Сравнение', 'en': 'Compare', 'value': 'compare', 'emoji': '⚔️', 'adjust': 2},
                    {'ru': 'Диапазон', 'en': 'Range', 'value': 'range', 'emoji': '📊', 'adjust': 2}
                ]
            }
        )
        value_param = BetParameter(
            param_type='bet_value',
            param_name={'ru': 'выберите значение', 'en': 'select value'},
            options={
                'values': [
                    # ===== СУММА ОЧКОВ (от 2 до 12) =====
                    {'ru': 'Сумма = 2', 'en': 'Sum = 2', 'emoji': '2️⃣', 'value': 2, 'bet_type': 'sum', 'adjust': 3},
                    {'ru': 'Сумма = 3', 'en': 'Sum = 3', 'emoji': '3️⃣', 'value': 3, 'bet_type': 'sum', 'adjust': 3},
                    {'ru': 'Сумма = 4', 'en': 'Sum = 4', 'emoji': '4️⃣', 'value': 4, 'bet_type': 'sum', 'adjust': 3},
                    {'ru': 'Сумма = 5', 'en': 'Sum = 5', 'emoji': '5️⃣', 'value': 5, 'bet_type': 'sum', 'adjust': 3},
                    {'ru': 'Сумма = 6', 'en': 'Sum = 6', 'emoji': '6️⃣', 'value': 6, 'bet_type': 'sum', 'adjust': 3},
                    {'ru': 'Сумма = 7', 'en': 'Sum = 7', 'emoji': '7️⃣', 'value': 7, 'bet_type': 'sum', 'adjust': 3},
                    {'ru': 'Сумма = 8', 'en': 'Sum = 8', 'emoji': '8️⃣', 'value': 8, 'bet_type': 'sum', 'adjust': 3},
                    {'ru': 'Сумма = 9', 'en': 'Sum = 9', 'emoji': '9️⃣', 'value': 9, 'bet_type': 'sum', 'adjust': 3},
                    {'ru': 'Сумма = 10', 'en': 'Sum = 10', 'emoji': '🔟', 'value': 10, 'bet_type': 'sum', 'adjust': 3},
                    {'ru': 'Сумма = 11', 'en': 'Sum = 11', 'emoji': '1️⃣1️⃣', 'value': 11, 'bet_type': 'sum',
                     'adjust': 3},
                    {'ru': 'Сумма = 12', 'en': 'Sum = 12', 'emoji': '1️⃣2️⃣', 'value': 12, 'bet_type': 'sum',
                     'adjust': 3},

                    # ===== ЧЕТНОСТЬ =====
                    {'ru': 'Четная сумма', 'en': 'Even sum', 'emoji': '✅', 'value': 'even', 'bet_type': 'parity',
                     'adjust': 2},
                    {'ru': 'Нечетная сумма', 'en': 'Odd sum', 'emoji': '❌', 'value': 'odd', 'bet_type': 'parity',
                     'adjust': 2},

                    # ===== ДУБЛИ (ОДИНАКОВЫЕ ЧИСЛА) =====
                    {'ru': 'Дубль (любой)', 'en': 'Doubles (any)', 'emoji': '🎲🎲', 'value': 'any', 'bet_type': 'doubles',
                     'adjust': 2},
                    {'ru': 'Дубль 1 (1-1)', 'en': 'Doubles 1 (1-1)', 'emoji': '1️⃣', 'value': 1, 'bet_type': 'doubles',
                     'adjust': 2},
                    {'ru': 'Дубль 2 (2-2)', 'en': 'Doubles 2 (2-2)', 'emoji': '2️⃣', 'value': 2, 'bet_type': 'doubles',
                     'adjust': 2},
                    {'ru': 'Дубль 3 (3-3)', 'en': 'Doubles 3 (3-3)', 'emoji': '3️⃣', 'value': 3, 'bet_type': 'doubles',
                     'adjust': 2},
                    {'ru': 'Дубль 4 (4-4)', 'en': 'Doubles 4 (4-4)', 'emoji': '4️⃣', 'value': 4, 'bet_type': 'doubles',
                     'adjust': 2},
                    {'ru': 'Дубль 5 (5-5)', 'en': 'Doubles 5 (5-5)', 'emoji': '5️⃣', 'value': 5, 'bet_type': 'doubles',
                     'adjust': 2},
                    {'ru': 'Дубль 6 (6-6)', 'en': 'Doubles 6 (6-6)', 'emoji': '6️⃣', 'value': 6, 'bet_type': 'doubles',
                     'adjust': 2},

                    # ===== СРАВНЕНИЕ КУБИКОВ =====
                    {'ru': 'Первый > Второй', 'en': 'First > Second', 'emoji': '▶️', 'value': 'first_greater',
                     'bet_type': 'compare', 'adjust': 2},
                    {'ru': 'Второй > Первый', 'en': 'Second > First', 'emoji': '◀️', 'value': 'second_greater',
                     'bet_type': 'compare', 'adjust': 2},
                    {'ru': 'Равны', 'en': 'Equal', 'emoji': '⚖️', 'value': 'equal', 'bet_type': 'compare', 'adjust': 2},

                    # ===== ДИАПАЗОНЫ СУМ =====
                    {'ru': 'Сумма < 7', 'en': 'Sum < 7', 'emoji': '⬇️', 'value': 'less_than_7', 'bet_type': 'range',
                     'adjust': 2},
                    {'ru': 'Сумма > 7', 'en': 'Sum > 7', 'emoji': '⬆️', 'value': 'greater_than_7', 'bet_type': 'range',
                     'adjust': 2},
                    {'ru': 'Сумма = 7', 'en': 'Sum = 7', 'emoji': '7️⃣', 'value': 'equal_7', 'bet_type': 'range',
                     'adjust': 2}
                ]
            },
            validation_func=lambda value, bet_type: value.get('bet_type') == bet_type
        )
        self.setup_bet_data_flow(bet_type_param, value_param)
        self.start_output = "🎲 ..."
        self.load_config()

    def load_config(self) -> None:
        """Загружает конфигурацию в зависимости от выбранного режима"""
        config_type_upper = self.config_name.upper()
        if hasattr(DiceConfig, config_type_upper):
            self.config = getattr(DiceConfig, config_type_upper)
        else:
            self.config = DiceConfig.HONEST
        self.animation_settings = DiceConfig.ANIMATION_SETTINGS

    def get_config_info(self) -> str:
        """Возвращает информацию о текущей конфигурации"""
        config = self.config
        multipliers = config['multipliers']
        probabilities = config['probabilities']
        info = (
            f"📊 Конфигурация: {self.config_name.upper()}\n"
            f"Множители: {multipliers}\n"
            f"Вероятности: {probabilities}"
        )
        return info

    async def play(self, bot, user_id: int, message_id: int,
                   bet: float, bet_data: Optional[str] = None, send_frame: Optional[Callable] = None) -> GameResult:
        """Запуск игры в кости"""
        self.game_over = False
        self.current_status = GameStatus.RUNNING

        # Генерируем результат двух кубиков
        dice1, dice2 = self.generate_result(bet_data)

        # Проверяем выигрыш/проигрыш
        win_amount, multiplier = self.evaluate_result((dice1, dice2), bet, bet_data)

        # Показываем анимацию с реальным результатом
        animation_data = await self.create_animation((dice1, dice2), bot, user_id, message_id, send_frame)

        # Получаем игровые данные
        game_data = self._get_game_data((dice1, dice2), bet_data)

        game_result = GameResult(
            status=GameStatus.FINISHED,
            win_amount=win_amount,
            bet_amount=bet,
            user_bet=f"{game_data['bet_type']} {game_data['bet_value']}",
            multiplier=multiplier,
            is_win=win_amount > 0,
            game_data=game_data,
            animations_data=animation_data,
            bet_data=bet_data
        )

        return await self._finalize_game(game_result)

    def generate_result(self, bet_data: Optional[str] = None) -> tuple[int, int]:
        """
        Генерирует результат броска двух костей (значения от 1 до 6 для каждого).
        Возвращает кортеж (dice1, dice2)
        """
        dice1 = randint(1, 6)
        dice2 = randint(1, 6)
        return dice1, dice2

    def evaluate_result(self, result: tuple[int, int], bet: float,
                        bet_data: Optional[str] = None) -> tuple[float, float]:
        """
        Проверяет выигрыш/проигрыш на основе результата двух кубиков.
        result - кортеж (dice1, dice2)
        Возвращает (выигрыш, множитель)
        """
        if not bet_data:
            return 0, 0

        dice1, dice2 = result
        actual_sum = dice1 + dice2

        bet_parts = bet_data.split(";")
        bet_type = bet_parts[0].split(':')[1]
        bet_value = bet_parts[1].split(':')[1]

        multiplier = 0
        is_win = False

        if bet_type == 'sum':
            is_win = actual_sum == int(bet_value)
            multiplier = self.config['multipliers'].get(f'sum_{bet_value}', 0)

        elif bet_type == 'parity':
            is_even = actual_sum % 2 == 0
            is_win = (bet_value == 'even' and is_even) or (bet_value == 'odd' and not is_even)
            multiplier = self.config['multipliers'].get('parity', 0)

        elif bet_type == 'doubles':
            is_double = dice1 == dice2
            if bet_value == 'any':
                is_win = is_double
            else:
                is_win = is_double and dice1 == int(bet_value)
            multiplier = self.config['multipliers'].get('doubles', 0)

        elif bet_type == 'compare':
            if bet_value == 'first_greater':
                is_win = dice1 > dice2
            elif bet_value == 'second_greater':
                is_win = dice2 > dice1
            elif bet_value == 'equal':
                is_win = dice1 == dice2
            multiplier = self.config['multipliers'].get('compare', 0)

        elif bet_type == 'range':
            if bet_value == 'less_than_7':
                is_win = actual_sum < 7
            elif bet_value == 'greater_than_7':
                is_win = actual_sum > 7
            elif bet_value == 'equal_7':
                is_win = actual_sum == 7
            multiplier = self.config['multipliers'].get('range', 0)

        payout = bet * multiplier if is_win else 0
        return payout, multiplier

    async def create_animation(self, result: tuple[int, int], bot, user_id: int, message_id: int,
                               send_frame: Optional[Callable] = None) -> dict[str, Any]:
        """
        Показывает анимацию кручения костей, заканчивающуюся реальным результатом.

        :param result: Кортеж (dice1, dice2) - реальный результат
        :param bot: Объект бота
        :param user_id: ID пользователя
        :param message_id: ID сообщения для обновления
        :param send_frame: Callback для отправки фреймов
        :return: Словарь с данными анимации
        """
        if not send_frame:
            dice1, dice2 = result
            return {
                'total_frames': 0,
                'final_result': (dice1, dice2),
                'animation_duration': 0,
                'icon': self.icon
            }

        animation_frames = self.animation_settings.get('frames', 20)
        frame_delay = self.animation_settings.get('delay', 0.1)

        # Генерируем случайные значения для анимации
        dice1_values = [randint(1, 6) for _ in range(animation_frames)]
        dice2_values = [randint(1, 6) for _ in range(animation_frames)]

        # Показываем анимацию
        for i in range(animation_frames):
            frame_sum = dice1_values[i] + dice2_values[i]
            frame_text = f"{self.icon} [{dice1_values[i]}] [{dice2_values[i]}] = {frame_sum}"

            if send_frame:
                await send_frame(bot, user_id, message_id, frame_text)

            if frame_delay > 0:
                await asyncio.sleep(frame_delay)

        # Финальный результат - СОВПАДАЕТ С РЕАЛЬНЫМ РЕЗУЛЬТАТОМ
        dice1_final, dice2_final = result
        final_sum = dice1_final + dice2_final

        final_text = f"{self.icon} [{dice1_final}] [{dice2_final}] = {final_sum}"
        if send_frame:
            await send_frame(bot, user_id, message_id, final_text)

        return {
            'total_frames': animation_frames,
            'final_result': result,
            'animation_duration': animation_frames * frame_delay,
            'icon': self.icon
        }

    def _get_game_data(self, result: tuple[int, int], bet_data: Optional[str] = None) -> dict[str, Any]:
        """Создает структуру game_data для костей"""
        if not bet_data:
            return {
                'result': result,
                'bet_type': None,
                'bet_value': None
            }
        bet_parts = bet_data.split(";")
        bet_type = bet_parts[0].split(':')[1]
        bet_value = bet_parts[1].split(':')[1]
        dice1, dice2 = result
        return {
            'result': result,
            'sum': dice1 + dice2,
            'dice1': dice1,
            'dice2': dice2,
            'bet_type': bet_type,
            'bet_value': bet_value
        }
