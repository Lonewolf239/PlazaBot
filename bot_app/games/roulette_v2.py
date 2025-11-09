import asyncio
from secrets import choice
from random import shuffle
from typing import Optional, Callable, Any

from . import BaseGame, BetParameter, GameResult, GameStatus
from .config import RouletteV2Config


class RouletteV2(BaseGame):
    def __init__(self, max_bet: float, config_name: str = "honest"):
        """
        Инициализация рулетки

        :param config_name: 'honest', 'aggressive' или 'generous'
        """
        super().__init__(max_bet, config_name)
        self.load_config()
        self.icon = "🎯"
        self._name = {"ru": "Рулетка V2", "en": "Roulette V2"}
        self._rules = {
            "ru": (
                "ℹ️ Правила Рулетки V2\n\n"
                "🎯 <b>КАК ИГРАТЬ</b>\n"
                "Выбери от 1 до 6 чисел от 0 до 89.\n"
                "Каждое число стоит одну ставку.\n\n"
                "💰 <b>МНОЖИТЕЛИ ВЫИГРЫША</b>\n"
                "1 число → 15x\n"
                "2 числа → 14x\n"
                "3 числа → 13x\n"
                "4 числа → 12x\n"
                "5 чисел → 11x\n"
                "6 чисел → 10x\n\n"
                "✅ <b>ВЫИГРЫШ</b>\n"
                "Если хотя бы одно число совпадает,\n"
                "вся ставка умножается на множитель!\n\n"
                "🍀 <b>Удачи!</b>"
            ),
            "en": (
                "ℹ️ Roulette V2 Rules\n\n"
                "🎯 <b>HOW TO PLAY</b>\n"
                "Select 1 to 6 numbers from 0 to 89.\n"
                "Each number costs one bet.\n\n"
                "💰 <b>MULTIPLIERS</b>\n"
                "1 number → 15x\n"
                "2 numbers → 14x\n"
                "3 numbers → 13x\n"
                "4 numbers → 12x\n"
                "5 numbers → 11x\n"
                "6 numbers → 10x\n\n"
                "✅ <b>WIN</b>\n"
                "If any selected number matches,\n"
                "your entire bet is multiplied!\n\n"
                "🍀 <b>Good luck!</b>"
            )
        }
        self.numbers = list(range(90))
        self.need_bet_data = True
        bet_value_param = BetParameter(
            param_type='bet_value',
            param_name={'ru': 'выберите значение', 'en': 'select value'},
            options={
                'values': [
                    {
                        'ru': 'Числа 0-89',
                        'en': 'Numbers 0-89',
                        'emoji': '🔢',
                        'value': self.numbers,
                        'bet_type': 'number',
                        'adjust': 5
                    }
                ]
            },
            multi_select=True,
            multi_select_max=6
        )
        self.setup_bet_data_flow(bet_value_param)
        self.start_output = "🎯 ..."

    def load_config(self) -> None:
        """Загружает конфигурацию в зависимости от выбранного режима"""
        config_type_upper = self.config_name.upper()
        if hasattr(RouletteV2Config, config_type_upper):
            self.config = getattr(RouletteV2Config, config_type_upper)
        else:
            self.config = RouletteV2Config.HONEST

    def get_config_info(self) -> str:
        """Возвращает информацию о текущей конфигурации"""
        config = self.config
        name = config.get('name', 'Unknown')
        description = config.get('description', '')
        house_edge = config.get('house_edge', 0)
        rtp = config.get('rtp', 0)
        info = (
            f"🎯 {name}\n"
            f"{description}\n\n"
            f"📊 Характеристики:\n"
            f"Дом-преимущество: {house_edge:.2f}%\n"
            f"RTP для игроков: {rtp:.2f}%\n"
        )
        return info

    def generate_rules(self) -> dict:
        """Генерирует HTML-версию правил"""
        rules_ru = f"""
<b>{self.icon} Правила Рулетки V2</b>

<b>🎯 КАК ИГРАТЬ</b>
Выбери от 1 до 6 чисел от 0 до 89.
Каждое число стоит одну ставку.

<b>💰 <b>МНОЖИТЕЛИ ВЫИГРЫША</b>
• 1 число → 15x
• 2 числа → 14x
• 3 числа → 13x
• 4 числа → 12x
• 5 чисел → 11x
• 6 чисел → 10x

<b>✅ ВЫИГРЫШ</b>
Если хотя бы одно число совпадает,
вся ставка умножается на множитель!

<b>🍀 Удачи!</b>
"""
        rules_en = f"""
<b>{self.icon} Roulette V2 Rules</b>

<b>🎯 HOW TO PLAY</b>
Select 1 to 6 numbers from 0 to 89.
Each number costs one bet.

<b>💰 MULTIPLIERS</b>
• 1 number → 15x
• 2 numbers → 14x
• 3 numbers → 13x
• 4 numbers → 12x
• 5 numbers → 11x
• 6 numbers → 10x

<b>✅ WIN</b>
If any selected number matches,
your entire bet is multiplied!

<b>🍀 Good luck!</b>
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
        animation_data = await self.create_animation(result, bot, user_id, message_id, send_frame, bet_data)
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
        return choice(self.numbers)

    def evaluate_result(self, result: int, bet: float, bet_data: Optional[str] = None) -> tuple[float, float]:
        """Оценивает ставку и возвращает выигрыш и множитель"""
        multiplier = 0
        if bet_data:
            try:
                bet_value = bet_data.split(':')[1]
                selected_numbers = bet_value.split(',')
                if str(result) in selected_numbers:
                    multiplier = 16 - len(selected_numbers)
            except (ValueError, IndexError, KeyError):
                multiplier = 0
        payout = bet * multiplier
        return payout, multiplier

    async def create_animation(self, result: int, bot, user_id: int,
                               message_id: int, send_frame: Optional[Callable] = None,
                               bet_data: Optional[str] = None) -> dict[str, Any]:
        """
        Показывает анимацию кручения рулетки с таблицей.
        :return: Словарь с данными анимации
        """
        selected_numbers = set()
        if bet_data:
            try:
                bet_value = bet_data.split(':')[1]
                selected_numbers = set(int(x.strip()) for x in bet_value.split(','))
            except (ValueError, IndexError, KeyError):
                selected_numbers = set()
        animation_frames = []
        frame_times = []
        start_frame = "🎯 ...\n"
        start_frame += self._generate_table(list(range(90)), selected_numbers=selected_numbers)
        if send_frame:
            await send_frame(bot, user_id, message_id, start_frame)
        frame_times.append(0.5)
        animation_frames.append(start_frame)
        animation_stages = [
            (15, 0.25),
            (11, 0.25),
            (9, 0.3),
            (8, 0.3),
            (8, 0.35),
            (7, 0.35),
            (6, 0.4),
            (6, 0.4),
            (6, 0.5),
            (5, 0.5),
            (4, 0.6),
            (3, 0.6),
            (1, 0.7)
        ]
        animation_numbers = [number for number in self.numbers]
        spinner_chars = ['◐', '◓', '◑', '◒']
        i = 0
        for num_count, delay in animation_stages:
            await asyncio.sleep(delay)
            spinner = spinner_chars[i % len(spinner_chars)]
            i += 1
            deleted_numbers = sorted(self._get_random_subset(animation_numbers, num_count, result))
            animation_numbers = [n for n in animation_numbers if n not in deleted_numbers]
            frame = f"🎯 {spinner} ...\n"
            frame += self._generate_table(animation_numbers, selected_numbers=selected_numbers)
            animation_frames.append(frame)
            frame_times.append(delay)
            if send_frame:
                await send_frame(bot, user_id, message_id, frame)
        final_frame = f"🎯 ✓ {result:2d}\n"
        final_frame += self._generate_table(animation_numbers, result, selected_numbers=selected_numbers)
        if send_frame:
            await send_frame(bot, user_id, message_id, final_frame)
        frame_times.append(1.5)
        animation_frames.append(final_frame)
        return {
            'total_frames': len(animation_frames),
            'final_result': f"{result:2d}",
            'animation_duration': sum(frame_times),
            "icon": self.icon
        }

    @staticmethod
    def _get_random_subset(numbers: list, count: int, excluded_number: int) -> list:
        """Получает рандомное подмножество чисел, исключая указанное число"""
        filtered_numbers = [num for num in numbers if num != excluded_number]
        if count >= len(filtered_numbers):
            return filtered_numbers
        subset = filtered_numbers.copy()
        shuffle(subset)
        return subset[:count]

    @staticmethod
    def _generate_table(visible_numbers: list, result: int = None, selected_numbers: set = None) -> str:
        """
        Генерирует стабильную таблицу 9х10 (всегда одинакового размера).
        Все невидимые позиции заполняются ⚫, чтобы таблица не прыгала.
        Выбранные числа заменяются на зелёные смайлики.

        :param visible_numbers: Видимые числа в таблице
        :param result: Финальный результат (выделяется 🎯)
        :param selected_numbers: Множество выбранных пользователем чисел
        """
        if selected_numbers is None:
            selected_numbers = set()
        cols = 10
        table = ""
        visible_set = set(visible_numbers)
        for i in range(0, 90, cols):
            row = ""
            for j in range(cols):
                num = i + j
                if result and num == result:
                    row += "🎯 "
                elif num in selected_numbers and num in visible_set:
                    row += "✅ "
                elif num in visible_set:
                    row += f"{num:2d} "
                else:
                    row += "⬛️ "
            table += row + "\n"
        return table

    def _get_game_data(self, result: int, bet_data: Optional[str] = None) -> dict[str, Any]:
        """Создает структуру game_data для рулетки"""
        bet_value = bet_data.split(':')[1]
        selected_numbers = bet_value.split(',')
        return {
            'result': result,
            'bet_value': ', '.join(selected_numbers)
        }
