import asyncio
from secrets import choice
from typing import Optional, Callable, Any
from . import BaseGame, GameStatus, GameResult, BetParameter
from .config import RouletteConfig


class Roulette(BaseGame):
    """
    Игра рулетка с поддержкой конфигурации.

    Типы ставок:
    - number|0-36: на конкретный номер (выплата ×35)
    - color|🔴 или color|⚫️: на цвет (выплата ×1.25)
    - range|1-18 или range|19-36: на диапазон (выплата ×1.25)
    - dozen|1, dozen|2 или dozen|3: на дюжину (выплата ×2)
    - column|1, column|2 или column|3: на колонну (выплата ×2)
    """
    def __init__(self, max_bet: float, config_name: str = "honest"):
        """
        Инициализация рулетки

        :param config_name: 'honest', 'aggressive' или 'generous'
        """
        super().__init__(max_bet, config_name)
        self.animation_settings = None
        self.load_config()
        self.icon = "🎡"
        self._name = {"ru": "Рулетка", "en": "Roulette"}
        self._rules = self.generate_rules()
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
                    {'ru': 'Число', 'en': 'Number', 'value': 'number', 'emoji': '🎯',
                        'adjust': 2},
                    {'ru': 'Цвет', 'en': 'Color', 'value': 'color', 'emoji': '🎨',
                        'adjust': 2},
                    {'ru': 'Чет/Нечет', 'en': 'Even/Odd', 'value': 'parity', 'emoji': '⚖️',
                        'adjust': 2},
                    {'ru': 'Дюжина', 'en': 'Dozen', 'value': 'dozen', 'emoji': '📊',
                        'adjust': 2},
                    {'ru': '1-18 / 19-36', 'en': 'Low/High', 'value': 'half', 'emoji': '⬆️',
                        'adjust': 2},
                    {'ru': 'Колонна', 'en': 'Column', 'value': 'column', 'emoji': '🏛️',
                        'adjust': 2}
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
                    {
                        'ru': '1 Колонна (1,4,7,...)',
                        'en': '1 Column (1,4,7,...)',
                        'emoji': '🥇',
                        'value': '1',
                        'bet_type': 'column',
                        'adjust': 2
                    },
                    {
                        'ru': '2 Колонна (2,5,8,...)',
                        'en': '2 Column (2,5,8,...)',
                        'emoji': '🥈',
                        'value': '2',
                        'bet_type': 'column',
                        'adjust': 2
                    },
                    {
                        'ru': '3 Колонна (3,6,9,...)',
                        'en': '3 Column (3,6,9,...)',
                        'emoji': '🥉',
                        'value': '3',
                        'bet_type': 'column',
                        'adjust': 2
                    },
                ]
            },
            validation_func=lambda value, bet_type: value.get('bet_type') == bet_type
        )
        self.setup_bet_data_flow(bet_type_param, value_param)
        self.start_output = "🎡 ..."

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
            f"• Чет/Нечет: {probabilities['parity_win'] * 100:.1f}%\n"
            f"• Диапазон: {probabilities['half_win'] * 100:.1f}%\n"
            f"• Дюжина: {probabilities['dozen_win'] * 100:.1f}%\n"
            f"• Колонна: {probabilities['column_win'] * 100:.1f}%\n\n"
            f"<b>💰 Выплаты:</b>\n"
            f"• Номер: ×{multipliers['number']}\n"
            f"• Цвет/Половина/Диапазон: ×{multipliers['color']}\n"
            f"• Дюжина/Колонна: ×{multipliers['dozen']}\n"
        )
        return info

    def generate_rules(self) -> dict:
        """Генерирует HTML-версию правил с множителями из конфига"""
        multipliers = self.config['multipliers']
        rules_ru = f"""
<b>{self.icon} Правила Рулетки</b>

<b>🎯 КАК ИГРАТЬ</b>
Выбери один из шести типов ставок.
Предсказание должно совпасть с результатом!

<b>📋 ТИПЫ СТАВОК</b>

<b>🎯 Число (0–36)</b>
Ставь на конкретный номер.
• Множитель → {multipliers['number']}x

<b>🎨 Цвет (красное/чёрное)</b>
Выбери цвет выпавшего номера.
• Множитель → {multipliers['color']}x

<b>⚖️ Чётное/Нечётное</b>
Предскажи чётность номера.
• Множитель → {multipliers['color']}x

<b>📊 Дюжина (1–12, 13–24, 25–36)</b>
Ставь на одну из трёх групп по 12 номеров.
• Множитель → {multipliers['dozen']}x

<b>⬆️ Половина (1–18, 19–36)</b>
Ставь на нижнюю или верхнюю половину номеров.
• Множитель → {multipliers['color']}x

<b>🏛️ Колонна (вертикальные ряды)</b>
Выбери одну из трёх колонн чисел.
• Множитель → {multipliers['dozen']}x

<b>🎲 ОСОБЕННОСТИ</b>
Зеро (0) - банк берёт при любой ставке, кроме самой на 0
"""
        rules_en = f"""
<b>{self.icon} Roulette Rules</b>

<b>🎯 HOW TO PLAY</b>
Choose one of six bet types.
Your prediction must match the result!

<b>📋 BET TYPES</b>

<b>🎯 Number (0–36)</b>
Bet on a specific number.
• Multiplier → {multipliers['number']}x

<b>🎨 Color (Red/Black)</b>
Choose the color of the winning number.
• Multiplier → {multipliers['color']}x

<b>⚖️ Even/Odd</b>
Predict the parity of the number.
• Multiplier → {multipliers['color']}x

<b>📊 Dozen (1–12, 13–24, 25–36)</b>
Bet on one of three groups of 12 numbers.
• Multiplier → {multipliers['dozen']}x

<b>⬆️ Half (1–18, 19–36)</b>
Bet on the lower or upper half of numbers.
• Multiplier → {multipliers['color']}x

<b>🏛️ Column (vertical rows)</b>
Choose one of three columns of numbers.
• Multiplier → {multipliers['dozen']}x

<b>🎲 FEATURES</b>
Zero (0) - bank wins on any bet except betting directly on 0
"""
        return {
            "ru": rules_ru,
            "en": rules_en
        }

    async def play(self, bot, user_id: int, message_id: int,
                   bet: float, bet_data: Optional[str] = None, send_frame: Optional[Callable] = None) -> GameResult:
        """Запуск рулетки"""
        self.game_over = False
        self.current_status = GameStatus.RUNNING

        result = self.generate_result()
        win_amount, multiplier = self.evaluate_result(result, bet, bet_data)
        animation_data = await self.create_animation(result, bot, user_id,
                                                     message_id, send_frame)
        game_data = self.get_game_data(result, bet_data)
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

    def generate_result(self, bet_data: Optional[str] = None) -> int:
        """
        Симулирует кручение колеса рулетки с учётом конфигурации
        Использует вероятности и смещения цвета из config
        """
        return choice(self.numbers)

    def evaluate_result(self, result: int, bet: float, bet_data: Optional[str] = None) -> tuple[float, float]:
        """Оценивает ставку и возвращает выигрыш и множитель"""
        payout = 0
        if bet_data:
            try:
                bet_parts = bet_data.split(";")
                bet_type = bet_parts[0].split(':')[1]
                bet_value = bet_parts[1].split(':')[1]
                multipliers = self.config['multipliers']
                if bet_type == "number":
                    if result == int(bet_value):
                        payout = bet * multipliers['number']
                elif bet_type == "color":
                    if self.colors[result] == bet_value:
                        payout = bet * multipliers['color']
                elif bet_type == "parity":
                    if result == 0:
                        payout = 0
                    elif (bet_value == "even" and result % 2 == 0) or (bet_value == "odd" and result % 2 != 0):
                        payout = bet * multipliers['parity']
                elif bet_type == "dozen":
                    if result in self.dozens.get(int(bet_value), set()):
                        payout = bet * multipliers['dozen']
                elif bet_type == "column":
                    if result in self.columns.get(int(bet_value), set()):
                        payout = bet * multipliers['column']
                elif bet_type == "half":
                    if bet_value == "1-18" and 1 <= result <= 18:
                        payout = bet * multipliers['half']
                    elif bet_value == "19-36" and 19 <= result <= 36:
                        payout = bet * multipliers['half']
            except (ValueError, IndexError, KeyError):
                payout = 0
        multiplier = payout / bet if bet > 0 else 0
        return payout, multiplier

    async def create_animation(self, result: int, bot, user_id: int, message_id: int,
                               send_frame: Optional[Callable] = None,
                               bet_data: Optional[str] = None) -> dict[str, Any]:
        """
        Показывает анимацию кручения рулетки как реально вращающееся колесо.
        :return: Словарь с данными анимации
        """
        settings = self.animation_settings
        total_steps = settings['total_steps']
        start_frame_time = settings['start_frame_time']
        animation_frames = []
        frame_times = []
        start_frame = self.start_output
        if send_frame:
            await send_frame(bot, user_id, message_id, {"text": start_frame})
        animation_frames.append(start_frame)
        wheel = self.numbers * 8
        target_indices = [i for i, num in enumerate(wheel) if num == result]
        final_index = target_indices[-2]
        start_offset = max(0, final_index - total_steps)
        wheel_display = {
            'top_1': None,
            'top_2': None,
            'center': None,
            'bottom_1': None,
            'bottom_2': None
        }
        total_animation_time = 0
        for step in range(total_steps):
            progress = step / total_steps
            if progress < 0.75:
                current_time = start_frame_time + progress * 0.1
            else:
                adjusted_progress = (progress - 0.75) / 0.75
                current_time = start_frame_time + 0.1 + (adjusted_progress ** 2) * 0.1
            wheel_index = start_offset + step
            positions = [
                wheel[(wheel_index - 2) % len(wheel)],
                wheel[(wheel_index - 1) % len(wheel)],
                wheel[wheel_index % len(wheel)],
                wheel[(wheel_index + 1) % len(wheel)],
                wheel[(wheel_index + 2) % len(wheel)]
            ]
            wheel_display['top_2'] = positions[0]
            wheel_display['top_1'] = positions[1]
            wheel_display['center'] = positions[2]
            wheel_display['bottom_1'] = positions[3]
            wheel_display['bottom_2'] = positions[4]
            frame = self._build_roulette_frame(wheel_display)
            if send_frame:
                await send_frame(bot, user_id, message_id, {"text": frame})
            animation_frames.append(frame)
            frame_times.append(current_time)
            total_animation_time += current_time
            await asyncio.sleep(current_time)
        positions = [
            wheel[(final_index - 2) % len(wheel)],
            wheel[(final_index - 1) % len(wheel)],
            wheel[final_index % len(wheel)],
            wheel[(final_index + 1) % len(wheel)],
            wheel[(final_index + 2) % len(wheel)]
        ]
        wheel_display['top_2'] = positions[0]
        wheel_display['top_1'] = positions[1]
        wheel_display['center'] = positions[2]
        wheel_display['bottom_1'] = positions[3]
        wheel_display['bottom_2'] = positions[4]
        final_frame = self._build_roulette_frame(wheel_display, highlight_result=True)
        if send_frame:
            await send_frame(bot, user_id, message_id, {"text": final_frame})
        animation_frames.append(final_frame)
        return {
            'total_frames': len(animation_frames),
            'final_result': f"{wheel_display['center']:2d} {self.colors[wheel_display['center']]}",
            'animation_duration': total_animation_time,
            'icon': self.icon
        }

    def _build_roulette_frame(self, wheel_display: dict, highlight_result: bool = False) -> str:
        """
        Строит визуализацию вращающейся рулетки.

        :param wheel_display: Словарь с позициями на колесе
        :param highlight_result: Выделять ли результат (используется для финального кадра)
        :return: Строка визуализации рулетки
        """
        top_2 = wheel_display['top_2']
        top_1 = wheel_display['top_1']
        center = wheel_display['center']
        bottom_1 = wheel_display['bottom_1']
        bottom_2 = wheel_display['bottom_2']
        colors = {
            top_2: self.colors[top_2],
            top_1: self.colors[top_1],
            center: self.colors[center],
            bottom_1: self.colors[bottom_1],
            bottom_2: self.colors[bottom_2]
        }
        if highlight_result:
            frame = f"""
🎡
◀ {top_2:2d} {colors[top_2]} ▶
◀ {top_1:2d} {colors[top_1]} ▶
▲
◀ {center:2d} {colors[center]} ▶ ✓
▼
◀ {bottom_1:2d} {colors[bottom_1]} ▶
◀ {bottom_2:2d} {colors[bottom_2]} ▶
            """
        else:
            frame = f"""
🎡
◀ {top_2:2d} {colors[top_2]} ▶
◀ {top_1:2d} {colors[top_1]} ▶
▲
◀ {center:2d} {colors[center]} ▶
▼
◀ {bottom_1:2d} {colors[bottom_1]} ▶
◀ {bottom_2:2d} {colors[bottom_2]} ▶
            """
        return frame

    def get_game_data(self, result: int, bet_data: Optional[str] = None) -> dict[str, Any]:
        """Создает структуру game_data для рулетки"""
        bet_parts = bet_data.split(";")
        bet_type = bet_parts[0].split(':')[1]
        bet_value = bet_parts[1].split(':')[1]
        return {
            'result': result,
            'result_color': self.colors[result],
            'bet_type': bet_type if bet_data else None,
            'bet_value': bet_value if bet_data else None
        }
