import asyncio
from io import BytesIO
from secrets import choice, SystemRandom, randbelow
from typing import Optional, Callable, Any
from PIL import Image, ImageDraw
from . import BaseGame, BetParameter, GameResult, GameStatus
from .config import RouletteV2Config
from ..resources import ResourceLoader


class Lottery(BaseGame):
    def __init__(self, max_bet: float, config_name: str = "honest"):
        """
        Инициализация рулетки

        :param config_name: 'honest', 'aggressive' или 'generous'
        """
        super().__init__(max_bet, config_name)
        self.load_config()
        self.icon = "🎯"
        self._name = {"ru": "Лотерея", "en": "Lottery"}
        self._rules = self.generate_rules()
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
<b>{self.icon} Правила Лотереи</b>

<b>🎯 КАК ИГРАТЬ</b>
Выбери от 1 до 6 чисел от 0 до 89.
Каждое число стоит одну ставку.

<b>💰 МНОЖИТЕЛИ ВЫИГРЫША</b>
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
<b>{self.icon} Lottery Rules</b>

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

    async def play(self, bot, user_id: int, message_id: int, bet: float, promoter_data: list[bool | float | float],
                   bet_data: Optional[str] = None, send_frame: Optional[Callable] = None) -> GameResult:
        """Запуск рулетки"""
        self.game_over = False
        self.current_status = GameStatus.RUNNING
        result = self.generate_result()
        win_amount, multiplier = self.evaluate_result(result, bet, bet_data)
        if promoter_data[0] and promoter_data[1] <= promoter_data[2] and randbelow(100) < 15:
            while win_amount == 0:
                result = self.generate_result()
                win_amount, multiplier = self.evaluate_result(result, bet, bet_data)
        animation_data = await self.create_animation(result, bot, user_id, message_id, send_frame, bet_data)
        game_data = self.get_game_data(result, bet_data)
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

    async def get_phantom_win(self, user_id: int, bet: float, bot: Optional[Any] = None) -> GameResult:
        confidence = 90
        selected_number = 0
        max_tickets = 6
        for ticket in range(1, max_tickets + 1):
            if randbelow(100) < confidence:
                selected_number = ticket
                confidence -= randbelow(6) + 20
            else:
                break
        if selected_number == 0:
            selected_number = 1
        numbers = SystemRandom().sample(range(90), selected_number)
        bet_data = "bet_value:" + ",".join(map(str, numbers))
        bet = bet * selected_number
        result = choice(numbers)
        win_amount, multiplier = self.evaluate_result(result, bet, bet_data)
        game_data = self.get_game_data(result, bet_data)
        frame_image = self._get_field_display([], result, selected_numbers=[result])
        game_result = GameResult(
            status=GameStatus.FINISHED,
            win_amount=win_amount,
            bet_amount=bet,
            user_bet=game_data["bet_value"],
            multiplier=multiplier,
            is_win=True,
            game_data=game_data,
            animations_data={'icon': self.icon, 'final_result': f"🎯 ✓ {result:2d}", 'final_result_image': frame_image},
            bet_data=bet_data
        )
        return await self._finalize_game(game_result)

    def generate_result(self, bet_data: Optional[str] = None) -> int:
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
        start_frame = "🎯 ..."
        frame_image = self._get_field_display(list(range(90)), selected_numbers=selected_numbers)
        if send_frame:
            await send_frame(bot, user_id, message_id, {"text": start_frame, "image": frame_image})
        frame_times.append(0.5)
        animation_frames.append(start_frame)
        animation_stages = [
            (15, 0.65),
            (11, 0.65),
            (9, 0.65),
            (8, 0.65),
            (8, 0.65),
            (7, 0.65),
            (6, 0.65),
            (6, 0.65),
            (6, 0.65),
            (5, 0.65),
            (4, 0.65),
            (3, 0.65),
            (1, 0.65)
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
            frame = f"🎯 {spinner} ..."
            frame_image = self._get_field_display(animation_numbers, selected_numbers=selected_numbers)
            animation_frames.append(frame)
            frame_times.append(delay)
            if send_frame:
                await send_frame(bot, user_id, message_id, {"text": frame, "image": frame_image})
        final_frame = f"🎯 ✓ {result:2d}"
        frame_image = self._get_field_display(animation_numbers, result, selected_numbers=selected_numbers)
        if send_frame:
            await send_frame(bot, user_id, message_id, {"text": final_frame, "image": frame_image})
        frame_times.append(1.5)
        animation_frames.append(final_frame)
        return {
            'total_frames': len(animation_frames),
            'final_result': f"{result:2d}",
            'final_result_image': frame_image,
            'animation_duration': sum(frame_times),
            "icon": self.icon
        }

    @staticmethod
    def _get_field_display(visible_numbers: list, result: int = None, selected_numbers: set = None) -> BytesIO:
        """
        Генерирует изображение поля рулетки (9x10 сетка с числами).
        Возвращает BytesIO объект, совместимый с bot.send_photo().
        """
        if selected_numbers is None:
            selected_numbers = set()
        STYLE = {
            'bg_color': '#030302',
            'cell_unopened': '#01090c',
            'cell_opened': '#121921',
            'cell_selected': '#0f1f0f',
            'cell_result': '#1a1a00',
            'cell_border': '#334353',
            'cell_result_border': '#FFD700',
            'cell_selected_border': '#4CAF50',
            'text_normal': '#888888',
            'text_selected': '#76FF03',
            'text_result': '#FFD700',
            'cell_size': 60,
            'padding': 8,
            'border_width': 1,
        }
        COLS = 10
        ROWS = 9
        img_width = COLS * STYLE['cell_size'] + (COLS + 1) * STYLE['padding']
        img_height = ROWS * STYLE['cell_size'] + (ROWS + 1) * STYLE['padding']
        img = Image.new('RGB', (img_width, img_height), color=STYLE['bg_color'])
        draw = ImageDraw.Draw(img)
        font = ResourceLoader.load_fonts()["small"]
        visible_set = set(visible_numbers)
        for cell in range(90):
            row = cell // COLS
            col = cell % COLS
            x = col * STYLE['cell_size'] + (col + 1) * STYLE['padding']
            y = row * STYLE['cell_size'] + (row + 1) * STYLE['padding']
            is_visible = cell in visible_set
            is_selected = cell in selected_numbers and is_visible
            is_result = result is not None and cell == result
            text_color = STYLE['text_normal']
            cell_border = STYLE['cell_border']
            text = f"{cell:2d}"
            if is_selected:
                cell_border = STYLE['cell_selected_border']
                cell_bg_color = STYLE['cell_selected']
                text_color = STYLE['text_selected']
            elif is_result:
                cell_border = STYLE['cell_result_border']
                cell_bg_color = STYLE['cell_result']
                text_color = STYLE['text_result']
            elif is_visible:
                cell_bg_color = STYLE['cell_opened']
            else:
                text = "X"
                cell_bg_color = STYLE['cell_unopened']
            draw.rectangle([x, y, x + STYLE['cell_size'], y + STYLE['cell_size']],
                           fill=cell_bg_color, outline=cell_border, width=STYLE['border_width'])
            draw.text((x + STYLE['cell_size'] // 2, y + STYLE['cell_size'] // 2), text,
                      fill=text_color, font=font, anchor='mm')
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        return img_byte_arr

    @staticmethod
    def _get_random_subset(numbers: list, count: int, excluded_number: int) -> list:
        """Получает рандомное подмножество чисел, исключая указанное число"""
        filtered_numbers = [num for num in numbers if num != excluded_number]
        if count >= len(filtered_numbers):
            return filtered_numbers
        subset = filtered_numbers.copy()
        SystemRandom().shuffle(subset)
        return subset[:count]

    def get_game_data(self, result: int, bet_data: Optional[str] = None) -> dict[str, Any]:
        """Создает структуру game_data для рулетки"""
        bet_value = bet_data.split(':')[1]
        selected_numbers = bet_value.split(',')
        return {
            'result': result,
            'bet_value': ', '.join(selected_numbers)
        }
