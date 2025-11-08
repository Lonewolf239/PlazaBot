import asyncio
from random import random, shuffle, choice
from typing import Optional, Callable, Any
from . import BaseGame, GameStatus, GameResult, BetParameter
from .config import RouletteConfig


class Roulette(BaseGame):
    """
    Игра рулетка с поддержкой конфигурации.

    Типы ставок:
    - number|0-36: на конкретный номер (выплата ×35)
    - color|🔴 или color|⚫️: на цвет (выплата ×1)
    - range|1-18 или range|19-36: на диапазон (выплата ×1)
    - dozen|1, dozen|2 или dozen|3: на дюжину (выплата ×2)
    - column|1, column|2 или column|3: на колонну (выплата ×2)
    """
    def __init__(self, config_name: str = "honest"):
        """
        Инициализация рулетки

        :param config_name: 'honest', 'aggressive' или 'generous'
        """
        super().__init__(config_name)
        self.load_config()
        self.animation_settings = None
        self.icon = "🎡"
        self._name = {"ru": "Рулетка", "en": "Roulette"}
        self._rules = {
            "ru": (
                "ℹ️ Правила рулетки\n"
                "🎯 Номер (0–36) — выплата ×35\n"
                "🟴 Цвет (красное/чёрное) — выплата ×1\n"
                "📊 Диапазон (1–18/19–36) — выплата ×1\n"
                "🔢 Дюжина (1–12, 13–24, 25–36) — выплата ×2\n"
                "📈 Колонна (1, 2, 3) — выплата ×2"
            ),
            "en": (
                "ℹ️ Roulette Rules\n"
                "🎯 Number (0–36) — payout ×35\n"
                "🟴 Color (red/black) — payout ×1\n"
                "📊 Range (1–18/19–36) — payout ×1\n"
                "🔢 Dozen (1–12, 13–24, 25–36) — payout ×2\n"
                "📈 Column (1, 2, 3) — payout ×2"
            )
        }
        self.numbers = list(range(37))
        self.colors = {
            0: "🟢",
            **{n: "🔴" if n in (
                1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36
            ) else "⚫️" for n in range(1, 37)}
        }
        self.dozens = {
            1: set(range(1, 13)),
            2: set(range(13, 25)),
            3: set(range(25, 37))
        }
        self.ranges = {
            "1-18": set(range(1, 19)),
            "19-36": set(range(19, 37))
        }
        self.columns = {
            1: {1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34},
            2: {2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35},
            3: {3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36}
        }
        self.need_bet_data = True
        bet_type_param = BetParameter(
            param_type='bet_type',
            param_name={'ru': 'тип ставки', 'en': 'bet type'},
            options={
                'values': [
                    {'ru': 'Число', 'en': 'Number', 'value': 'number', 'emoji': '🎯'},
                    {'ru': 'Цвет', 'en': 'Color', 'value': 'color', 'emoji': '🎨'},
                    {'ru': 'Чет/Нечет', 'en': 'Even/Odd', 'value': 'parity', 'emoji': '⚖️'},
                    {'ru': 'Дюжина', 'en': 'Dozen', 'value': 'dozen', 'emoji': '📊'},
                    {'ru': '1-18 / 19-36', 'en': 'Low/High', 'value': 'half', 'emoji': '⬆️'}
                ]
            }
        )
        value_param = BetParameter(
            param_type='bet_value',
            param_name={'ru': 'выберите значение', 'en': 'select value'},
            options={
                'values': [
                    {
                        'ru': 'Числа 0-36',
                        'en': 'Numbers 0-36',
                        'emoji': '🔢',
                        'value': list(range(0, 37)),
                        'bet_type': 'number',
                        'adjust': 6
                    },
                    {
                        'ru': 'Красное',
                        'en': 'Red',
                        'emoji': '🔴',
                        'value': '🔴',
                        'bet_type': 'color',
                        'adjust': 2
                    },
                    {
                        'ru': 'Чёрное',
                        'en': 'Black',
                        'emoji': '⚫️',
                        'value': '⚫️',
                        'bet_type': 'color',
                        'adjust': 2
                    },
                    {
                        'ru': 'Чётное',
                        'en': 'Even',
                        'emoji': '2️⃣',
                        'value': 'even',
                        'bet_type': 'parity',
                        'adjust': 2
                    },
                    {
                        'ru': 'Нечётное',
                        'en': 'Odd',
                        'emoji': '1️⃣',
                        'value': 'odd',
                        'bet_type': 'parity',
                        'adjust': 2
                    },
                    {
                        'ru': '1-12',
                        'en': '1-12',
                        'emoji': '🥇',
                        'value': 1,
                        'bet_type': 'dozen',
                        'adjust': 3
                    },
                    {
                        'ru': '13-24',
                        'en': '13-24',
                        'emoji': '🥈',
                        'value': 2,
                        'bet_type': 'dozen',
                        'adjust': 3
                    },
                    {
                        'ru': '25-36',
                        'en': '25-36',
                        'emoji': '🥉',
                        'value': 3,
                        'bet_type': 'dozen',
                        'adjust': 3
                    },
                    {
                        'ru': '1-18',
                        'en': '1-18',
                        'emoji': '◀️',
                        'value': '1-18',
                        'bet_type': 'half',
                        'adjust': 2
                    },
                    {
                        'ru': '19-36',
                        'en': '19-36',
                        'emoji': '▶️',
                        'value': '19-36',
                        'bet_type': 'half',
                        'adjust': 2
                    },
                ]
            },
            validation_func=lambda value, bet_type: value.get('bet_type') == bet_type
        )
        self.setup_bet_data_flow(bet_type_param, value_param)
        self.start_output = "🎡 ..."
        self.load_config()

    def load_config(self) -> None:
        """Загружает конфигурацию в зависимости от выбранного режима"""
        config_type_upper = self.config_name.upper()
        if hasattr(RouletteConfig, config_type_upper):
            self.config = getattr(RouletteConfig, config_type_upper)
        else:
            self.config = RouletteConfig.HONEST

        self.animation_settings = RouletteConfig.ANIMATION_SETTINGS

    def get_config_info(self) -> str:
        """Возвращает информацию о текущей конфигурации"""
        config = self.config
        multipliers = config['multipliers']
        probabilities = config['probabilities']
        info = (
            f"<b>{config['name']}</b>\n"
            f"{config['description']}\n\n"
            f"<b>🎲 Вероятности выигрыша:</b>\n"
            f"• Номер: {probabilities['number_win'] * 100:.1f}%\n"
            f"• Цвет: {probabilities['color_win'] * 100:.1f}%\n"
            f"• Диапазон: {probabilities['range_win'] * 100:.1f}%\n"
            f"• Дюжина: {probabilities['dozen_win'] * 100:.1f}%\n"
            f"• Колонна: {probabilities['column_win'] * 100:.1f}%\n\n"
            f"<b>💰 Выплаты:</b>\n"
            f"• Номер: ×{multipliers['number']}\n"
            f"• Цвет/Диапазон: ×{multipliers['color']}\n"
            f"• Дюжина/Колонна: ×{multipliers['dozen']}\n"
        )
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
            user_bet=f"{game_data["bet_type"]} {game_data["bet_value"]}",
            multiplier=multiplier,
            is_win=win_amount > 0,
            game_data=game_data,
            animations_data=animation_data,
            bet_data=bet_data
        )

        return await self._finalize_game(game_result)

    def generate_result(self) -> int:
        """
        Симулирует кручение колеса рулетки с учётом конфигурации
        Использует вероятности и смещения цвета из config
        """
        config = self.config
        probabilities = config['probabilities']
        color_bias = config.get('color_bias', 0.0)
        rand = random()
        if rand < probabilities['number_win'] * 1 / 37:
            return 0
        red_numbers = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
        black_numbers = {2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35}
        color_threshold = 0.5 + color_bias
        if rand < color_threshold:
            return choice(list(red_numbers))
        else:
            return choice(list(black_numbers))

    def evaluate_result(self, result: int, bet: float, bet_data: Optional[str] = None) -> tuple[float, float]:
        """Оценивает ставку и возвращает выигрыш и множитель"""
        payout = 0
        if bet_data:
            try:
                bet_parts = bet_data.split(";")
                bet_type = bet_parts[0].split(':')[1]
                bet_value = bet_parts[1].split(':')[1]
                print(bet_type)
                print(bet_value)
                multipliers = self.config['multipliers']
                if bet_type == "number":
                    if result == int(bet_value):
                        payout = bet * multipliers['number']
                elif bet_type == "color":
                    if self.colors[result] == bet_value:
                        payout = bet * multipliers['color']
                elif bet_type == "range":
                    if result in self.ranges.get(bet_value, set()):
                        payout = bet * multipliers['range']
                elif bet_type == "dozen":
                    if result in self.dozens.get(int(bet_value), set()):
                        payout = bet * multipliers['dozen']
                elif bet_type == "column":
                    if result in self.columns.get(int(bet_value), set()):
                        payout = bet * multipliers['column']
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
        settings = self.animation_settings
        total_steps = settings['total_steps']
        frame_time = settings['start_frame_time']
        frame_acceleration = settings['frame_acceleration']

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

        for step in range(total_steps):
            num = wheel[step % len(wheel)]
            color = self.colors[num]

            spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
            spinner = spinner_chars[step % len(spinner_chars)]

            frame = f"🎡 {spinner} {num:2d}  {color}"

            if send_frame:
                await send_frame(bot, user_id, message_id, frame)

            animation_frames.append(frame)
            frame_times.append(frame_time)

            await asyncio.sleep(frame_time)
            frame_time += frame_acceleration

        result_color = self.colors[result]
        final_frame = f"🎡 ✓ {result:2d}  {result_color}"

        if send_frame:
            await send_frame(bot, user_id, message_id, final_frame)

        animation_frames.append(final_frame)

        return {
            'total_frames': len(animation_frames),
            'final_result': f"{result:2d}  {result_color}",
            'animation_duration': sum(frame_times),
            "icon": self.icon
        }

    def _get_game_data(self, result: int, bet_data: Optional[str] = None) -> dict[str, Any]:
        """Создает структуру game_data для рулетки"""
        return {
            'result': result,
            'result_color': self.colors[result],
            'bet_type': bet_data.split(';')[0] if bet_data else None,
            'bet_value': bet_data.split(';')[1] if bet_data else None
        }
