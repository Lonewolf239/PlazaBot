import asyncio
from secrets import randbelow, choice
from typing import Optional, Callable, Any
from . import BaseGame, GameStatus, GameResult, BetParameter
from .config import DiceConfig


class Dice(BaseGame):
    def __init__(self, max_bet: float, config_name: str = "honest"):
        super().__init__(max_bet, config_name)
        self.animation_settings = None
        self.load_config()
        self.icon = "🎲"
        self._name = {"ru": "Кости", "en": "Dice"}
        self._rules = self.generate_rules()
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
                    {'ru': 'Дубль (любой)', 'en': 'Doubles (any)', 'emoji': '🎲🎲', 'value': 'any',
                     'bet_type': 'doubles', 'adjust': 2},
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

    def generate_rules(self) -> dict:
        """Генерирует HTML-версию правил с множителями из конфига"""
        multipliers = self.config['multipliers']
        rules_ru = f"""
<b>{self.icon} Правила Костей</b>

<b>🎯 КАК ИГРАТЬ</b>
Бросаются два кубика (значения от 1 до 6).
Выбери тип ставки и предскажи результат!

<b>📋 ТИПЫ СТАВОК</b>

<b>➕ Сумма (2-12)</b>
Угадай сумму двух кубиков.
Каждой сумме — свой множитель (редкие суммы дают больше).
• Сумма 2 → {multipliers.get('sum_2', 0)}x
• Сумма 3 → {multipliers.get('sum_3', 0)}x
• Сумма 4 → {multipliers.get('sum_4', 0)}x
• Сумма 5 → {multipliers.get('sum_5', 0)}x
• Сумма 6 → {multipliers.get('sum_6', 0)}x
• Сумма 7 → {multipliers.get('sum_7', 0)}x
• Сумма 8 → {multipliers.get('sum_8', 0)}x
• Сумма 9 → {multipliers.get('sum_9', 0)}x
• Сумма 10 → {multipliers.get('sum_10', 0)}x
• Сумма 11 → {multipliers.get('sum_11', 0)}x
• Сумма 12 → {multipliers.get('sum_12', 0)}x

<b>⚖️ Четность</b>
• Четная сумма → {multipliers.get('parity', 0)}x
• Нечетная сумма → {multipliers.get('parity', 0)}x

<b>🎲🎲 Дубль</b>
• Дубль (любой) — оба кубика показывают одно число → {multipliers.get('doubles', 0)}x

<b>⚔️ Сравнение</b>
• Первый кубик > Второй → {multipliers.get('compare', 0)}x
• Второй кубик > Первый → {multipliers.get('compare', 0)}x
• Кубики равны → {multipliers.get('compare', 0)}x

<b>📊 Диапазон</b>
• Сумма &lt; 7 → {multipliers.get('range', 0)}x
• Сумма &gt; 7 → {multipliers.get('range', 0)}x
• Сумма = 7 → {multipliers.get('range', 0)}x

<b>✅ ВЫИГРЫШ</b>
Сделай ставку, выбери тип и значение — выигрыш зависит от твоего выбора!

<b>🍀 Удачи!</b>
"""
        rules_en = f"""
<b>{self.icon} Dice Rules</b>

<b>🎯 HOW TO PLAY</b>
Two dice are rolled (values from 1 to 6).
Choose a bet type and predict the result!

<b>📋 BET TYPES</b>

<b>➕ Sum (2-12)</b>
Guess the sum of two dice.
Each sum has its own multiplier (rare sums give more).
• Sum 2 → {multipliers.get('sum_2', 0)}x
• Sum 3 → {multipliers.get('sum_3', 0)}x
• Sum 4 → {multipliers.get('sum_4', 0)}x
• Sum 5 → {multipliers.get('sum_5', 0)}x
• Sum 6 → {multipliers.get('sum_6', 0)}x
• Sum 7 → {multipliers.get('sum_7', 0)}x
• Sum 8 → {multipliers.get('sum_8', 0)}x
• Sum 9 → {multipliers.get('sum_9', 0)}x
• Sum 10 → {multipliers.get('sum_10', 0)}x
• Sum 11 → {multipliers.get('sum_11', 0)}x
• Sum 12 → {multipliers.get('sum_12', 0)}x

<b>⚖️ Parity</b>
• Even sum → {multipliers.get('parity', 0)}x
• Odd sum → {multipliers.get('parity', 0)}x

<b>🎲🎲 Doubles</b>
• Doubles (any) — both dice show the same number → {multipliers.get('doubles', 0)}x

<b>⚔️ Compare</b>
• First die > Second → {multipliers.get('compare', 0)}x
• Second die > First → {multipliers.get('compare', 0)}x
• Dice are equal → {multipliers.get('compare', 0)}x

<b>📊 Range</b>
• Sum &lt; 7 → {multipliers.get('range', 0)}x
• Sum &gt; 7 → {multipliers.get('range', 0)}x
• Sum = 7 → {multipliers.get('range', 0)}x

<b>✅ WIN</b>
Make a bet, choose a type and value — your winnings depend on your choice!

<b>🍀 Good luck!</b>
"""
        return {
            "ru": rules_ru,
            "en": rules_en
        }

    async def play(self, bot, user_id: int, message_id: int,
                   bet: float, bet_data: Optional[str] = None, send_frame: Optional[Callable] = None) -> GameResult:
        """Запуск игры в кости"""
        self.game_over = False
        self.current_status = GameStatus.RUNNING
        dice1, dice2 = self.generate_result(bet_data)
        win_amount, multiplier = self.evaluate_result((dice1, dice2), bet, bet_data)
        animation_data = await self.create_animation((dice1, dice2), bot, user_id, message_id, send_frame)
        game_data = self.get_game_data((dice1, dice2), bet_data)
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

    async def get_phantom_win(self, user_id: int, bet: float, bot: Optional[Any] = None) -> GameResult:
        bet_types = ['sum', 'parity', 'doubles', 'compare', 'range']
        bet_type = choice(bet_types)
        bet_data = "bet_type:"
        bet_data += bet_type + ";bet_value:"
        if bet_type == "sum":
            bet_value = str(2 + randbelow(11))
        elif bet_type == "parity":
            bet_value = choice(['even', 'odd'])
        elif bet_type == "doubles":
            bet_value = str(randbelow(6) + 1)
        elif bet_type == "compare":
            bet_value = choice(['first_greater', 'second_greater', 'equal'])
        else:
            bet_value = choice(['less_than_7', 'greater_than_7', 'equal_7'])
        bet_data += bet_value
        while True:
            result = self.generate_result()
            win_amount, multiplier = self.evaluate_result(result, bet, bet_data)
            if win_amount > bet:
                break
        dice1, dice2 = result
        game_data = self.get_game_data(result, bet_data)
        game_result = GameResult(
            status=GameStatus.FINISHED,
            win_amount=win_amount,
            bet_amount=bet,
            user_bet=f"{game_data["bet_type"]} {game_data["bet_value"]}",
            multiplier=multiplier,
            is_win=True,
            game_data=game_data,
            animations_data={
                'icon': self.icon,
                'final_result': f"🎲 {dice1} + 🎲 {dice2} = {dice1 + dice2} 🎉",
                'final_result_image': None
            },
            bet_data=bet_data
        )
        return await self._finalize_game(game_result)

    def generate_result(self, bet_data: Optional[str] = None) -> tuple[int, int]:
        """
        Генерирует результат броска двух костей (значения от 1 до 6 для каждого).
        Возвращает кортеж (dice1, dice2)
        """
        dice1 = randbelow(6) + 1
        dice2 = randbelow(6) + 1
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
                               send_frame: Optional[Callable] = None,
                               bet_data: Optional[str] = None) -> dict[str, Any]:
        animation_frames = self.animation_settings.get('frames', 20)
        frame_delay = self.animation_settings.get('delay', 0.1)
        dice1_values = [randbelow(6) + 1 for _ in range(animation_frames)]
        dice2_values = [randbelow(6) + 1 for _ in range(animation_frames)]
        for i in range(animation_frames):
            frame_text = (f"🎲 {dice1_values[i]} + 🎲 {dice2_values[i]}  "
                          f"= {dice1_values[i] + dice2_values[i]}  "
                          f"{'🎉' if i == animation_frames - 1 else '🔄'}")
            if send_frame:
                await send_frame(bot, user_id, message_id, {"text": frame_text})
            if frame_delay > 0:
                await asyncio.sleep(frame_delay)
        dice1_final, dice2_final = result
        final_sum = dice1_final + dice2_final
        final_text = f"🎲 {dice1_final} + 🎲 {dice2_final} = {final_sum} 🎉"
        if send_frame:
            await send_frame(bot, user_id, message_id, {"text": final_text})
        return {
            'total_frames': animation_frames,
            'final_result': result,
            'animation_duration': animation_frames * frame_delay,
            'icon': self.icon
        }

    def get_game_data(self, result: tuple[int, int], bet_data: Optional[str] = None) -> dict[str, Any]:
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
