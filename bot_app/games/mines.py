from secrets import randbelow
from io import BytesIO
from PIL import Image, ImageDraw
from typing import Any, Optional, Callable, Dict
from . import InteractiveGameBase, GameResult, GameStatus
from .config import MinesConfig
from ..resources import ResourceLoader


class Mines(InteractiveGameBase):
    """Mines игра — открывай ячейки и избегай бомб на поле 5x5"""
    def __init__(self, max_bet: float, config_name: str = "honest"):
        super().__init__(max_bet, config_name)
        self.load_config()
        self.icon = "💣"
        self._name = {"ru": "Мины", "en": "Mines"}
        self._rules = self.generate_rules()
        self.need_bet_data = False
        self.GRID_SIZE = 5
        self.TOTAL_CELLS = self.GRID_SIZE * self.GRID_SIZE
        self.game_type = "mines"

    def load_config(self):
        """Загружает конфигурацию в зависимости от выбранного режима"""
        config_type_upper = self.config_name.upper()
        if hasattr(MinesConfig, config_type_upper):
            self.config = getattr(MinesConfig, config_type_upper)
        else:
            self.config = MinesConfig.HONEST

    def get_config_info(self) -> str:
        return (f"Бомб: {self.config['bombs_count']}\nКоэффициенты в ячейках: "
                f"{self.config['min_coef']}x-{self.config['max_coef']}x")

    def generate_rules(self) -> dict:
        bombs = self.config['bombs_count']
        min_coef = self.config['min_coef']
        max_coef = self.config['max_coef']
        rules_ru = f"""
<b>{self.icon} Правила Мин</b>

<b>🎯 КАК ИГРАТЬ</b>
Перед вами поле 5×5 (25 ячеек).
На поле спрятано {bombs} 💣 бомб.
В остальных ячейках спрятаны коэффициенты от {min_coef}x до {max_coef}x!

<b>📈 МНОЖИТЕЛИ ВЫИГРЫША</b>
• Каждая открытая ячейка содержит случайный коэффициент
• Ваш общий множитель = сумма всех открытых коэффициентов

<b>✅ ВЫИГРЫШ</b>
• Откройте ячейку — коэффициент суммируется
• В любой момент можете забрать выигрыш кнопкой "💰 Забрать"

<b>💣 БОМБА</b>
• Открыли бомбу? Игра заканчивается
• Вы теряете ставку и весь множитель

<b>🎲 ОСОБЕННОСТИ</b>
• Коэффициенты в ячейках случайные
• Чем больше открыто ячеек, тем выше риск
• Можно выиграть максимум на всех безопасных ячейках

<b>🍀 Удачи!</b>
"""
        rules_en = f"""
<b>{self.icon} Mines Rules</b>

<b>🎯 HOW TO PLAY</b>
You have a 5×5 grid (25 cells).
There are {bombs} 💣 bombs hidden on the field.
The remaining cells contain coefficients from {min_coef}x to {max_coef}x!

<b>📈 WIN MULTIPLIERS</b>
• Each opened cell contains a random coefficient
• Your total multiplier = the sum of all opened coefficients

<b>✅ WIN</b>
• Open a cell — coefficient gets multiplied
• Cash out anytime with "💰 Cash Out" button

<b>💣 BOMB</b>
• Hit a bomb? Game over
• You lose your bet and all multipliers

<b>🎲 FEATURES</b>
• Coefficients in cells are random
• More cells opened = higher risk
• Maximum win when all safe cells are opened

<b>🍀 Good luck!</b>
"""
        return {
            "ru": rules_ru,
            "en": rules_en
        }

    def _generate_field(self) -> Dict[int, float]:
        field = {}
        bomb_count = self.config['bombs_count']
        bomb_positions = set()
        while len(bomb_positions) < bomb_count:
            bomb_positions.add(randbelow(self.TOTAL_CELLS))
        for cell in range(self.TOTAL_CELLS):
            if cell in bomb_positions:
                field[cell] = 0.0
            else:
                field[cell] = self.get_coefficient()
        return field

    def get_coefficient(self):
        min_coef = self.config["min_coef"]
        max_coef = self.config["max_coef"]
        random_value = randbelow(1000000) / 1000000
        random_value = random_value ** 3
        coefficient = min_coef + random_value * (max_coef - min_coef)
        return round(coefficient, 2)

    @staticmethod
    def _calculate_multiplier(coefficients: list[float]) -> float:
        """Рассчитать множитель как произведение всех коэффициентов"""
        if not coefficients:
            return 1.0
        multiplier = sum(coefficients)
        return round(multiplier, 2)

    def _cell_to_coords(self, cell: int) -> tuple[int, int]:
        """Преобразовать номер ячейки в координаты (строка, столбец)"""
        row = cell // self.GRID_SIZE
        col = cell % self.GRID_SIZE
        return row, col

    async def play(self, bot, user_id: int, message_id: int, bet: float,
                   bet_data: Optional[str] = None, send_frame: Optional[Callable] = None) -> GameResult:
        """Главный loop игры"""
        if not self.get_session(bot, user_id):
            self.create_session_in_manager(bot, user_id, bet, bet_data)
        session = self.get_session(bot, user_id)
        session['state'] = {
            'field': None,
            'opened': set(),
            'coefficients': [],
            'multiplier': 1.0,
            'field_generated': False
        }
        self.update_session(bot, user_id, state=session['state'])
        round_state = await self.get_round_state(bot, user_id)
        await self.send_initial_message(bot, user_id, message_id, round_state, "mines")
        return GameResult(
            status=GameStatus.RUNNING,
            win_amount=0,
            bet_amount=bet,
            user_bet=None,
            multiplier=1.0,
            is_win=False,
            game_data=await self.get_game_data(None, bet_data),
            animations_data={
                "final_result": round_state,
                "icon": self.icon
            },
            bet_data=bet_data
        )

    async def get_phantom_win(self, user_id: int, bet: float, bot: Optional[Any] = None) -> GameResult:
        field = self._generate_field()
        safe_cells_total = self.TOTAL_CELLS - self.config['bombs_count']
        max_open = min(randbelow(6) + 3, safe_cells_total)
        opened = set()
        coefficients = []
        for _ in range(max_open):
            while True:
                cell = randbelow(self.TOTAL_CELLS)
                if cell not in opened and field[cell] != 0.0:
                    opened.add(cell)
                    coefficients.append(field[cell])
                    break
        multiplier = self._calculate_multiplier(coefficients)
        win_amount = bet * multiplier
        session = {'bet': bet, 'state': {
            'multiplier': multiplier,
            'opened': opened,
            'field_generated': True,
            'field': field
        }}
        final_result = await self.get_final_result_message(bot, user_id, session)
        game_result = GameResult(
            status=GameStatus.FINISHED,
            win_amount=win_amount,
            bet_amount=bet,
            user_bet=None,
            multiplier=multiplier,
            is_win=True,
            game_data=await self.get_game_data(None, None),
            animations_data={
                'icon': self.icon,
                'final_result': final_result['text'],
                'final_result_image': final_result['image']
            },
            bet_data=None
        )

        return await self._finalize_game(game_result)

    async def process_action(self, bot, user_id: int, action: str) -> Dict[str, Any]:
        """Обработать ход игрока: открытие ячейки или забрать выигрыш"""
        session = self.get_session(bot, user_id)
        if not session:
            return {'error': await bot.get_text(user_id, "SESSION_EXPIRED")}
        state = session['state']
        if action == 'cashout':
            if len(state['opened']) == 0:
                state['multiplier'] = 1.0
            self.update_session(bot, user_id, state=state, game_over=True)
            return {
                'success': True,
                'game_over': True,
                'cashed_out': True,
                'opened_cell': None
            }
        try:
            cell = int(action)
        except ValueError:
            return {'error': 'Invalid action'}
        if cell < 0 or cell >= self.TOTAL_CELLS:
            return {'error': 'Invalid cell'}
        if cell in state['opened']:
            return {'error': 'Cell already opened'}
        if not state['field_generated']:
            state['field'] = self._generate_field()
            state['field_generated'] = True
        state['opened'].add(cell)
        cell_coefficient = state['field'][cell]
        if cell_coefficient == 0.0:
            state['multiplier'] = 0.0
            self.update_session(bot, user_id, state=state, game_over=True)
            return {
                'success': False,
                'game_over': True,
                'hit_bomb': True,
                'bomb_cell': cell,
                'opened_cell': cell,
                'coefficient': cell_coefficient
            }
        state['coefficients'].append(cell_coefficient)
        state['multiplier'] = self._calculate_multiplier(state['coefficients'])
        self.update_session(bot, user_id, state=state)
        safe_cells = self.TOTAL_CELLS - self.config['bombs_count']
        if len(state['opened']) >= safe_cells:
            self.update_session(bot, user_id, game_over=True)
            return {
                'success': True,
                'game_over': True,
                'all_safe_opened': True,
                'opened_cell': cell,
                'coefficient': cell_coefficient,
                'multiplier': state['multiplier']
            }
        return {
            'success': True,
            'game_over': False,
            'opened_cell': cell,
            'coefficient': cell_coefficient,
            'multiplier': state['multiplier']
        }

    async def is_game_over(self, bot, user_id: int) -> bool:
        """Проверить, завершена ли игра"""
        session = self.get_session(bot, user_id)
        if not session:
            return True
        return session.get('game_over', False)

    async def get_game_result(self, bot, user_id: int) -> tuple[float, float]:
        """Получить финальный выигрыш и множитель"""
        session = self.get_session(bot, user_id)
        if not session:
            return 0, 0
        state = session['state']
        multiplier = state['multiplier']
        win_amount = session['bet'] * multiplier
        return win_amount, multiplier

    async def get_round_state(self, bot, user_id: int) -> dict[str, Any]:
        """Получить текущее состояние раунда для отображения"""
        session = self.get_session(bot, user_id)
        return await self._format_round_state(bot, user_id, session)

    async def _format_round_state(self, bot, user_id: int, session: Dict[str, Any]) -> dict[str, Any]:
        """Форматировать состояние раунда в текст"""
        state = session['state']
        opened_count = len(state['opened'])
        multiplier = state['multiplier']
        potential_win = session['bet'] * multiplier
        user_data = await bot.database_interface.get_user(user_id)
        custom_data = {"icon": self.icon, "opened_count": opened_count,
                       "multiplier": f"{multiplier:.2f}", "potential_win": f"{potential_win:.2f}"}
        return {"text": await bot.get_text(user_id, "MINES_ROUND_STATE", user_data, custom_data)}

    def _get_field_display(self, state: Dict[str, Any]) -> BytesIO:
        """
        Генерирует изображение поля используя готовые PNG картинки.
        Возвращает BytesIO объект, совместимый с bot.send_photo().
        """
        STYLE = {
            'bg_color': '#030302',
            'cell_unopened': '#01090c',
            'cell_opened': '#121921',
            'cell_border': '#334353',
            'text_opened': '#ffffff',
            'text_unopened': '#888888',
            'cell_size': 80,
            'padding': 10,
            'border_width': 2,
            'icon_scale': 0.5,
            'mine_scale': 0.6,
        }
        grid_cols = self.GRID_SIZE
        grid_rows = self.GRID_SIZE
        img_width = grid_cols * STYLE['cell_size'] + (grid_cols + 1) * STYLE['padding']
        img_height = grid_rows * STYLE['cell_size'] + (grid_rows + 1) * STYLE['padding']
        img = Image.new('RGB', (img_width, img_height), color=STYLE['bg_color'])
        draw = ImageDraw.Draw(img)
        mine_img = ResourceLoader.load_image("mines", "mine.png",
                                             size=int(STYLE['cell_size'] * STYLE['mine_scale']))
        explosion_img = ResourceLoader.load_image("mines", "explosion.png",
                                                  size=int(STYLE['cell_size'] * STYLE['mine_scale']))
        fonts = ResourceLoader.load_fonts()
        font_medium = fonts['medium']
        font_small = fonts['small']
        for cell in range(self.TOTAL_CELLS):
            row = cell // self.GRID_SIZE
            col = cell % self.GRID_SIZE
            x = col * STYLE['cell_size'] + (col + 1) * STYLE['padding']
            y = row * STYLE['cell_size'] + (row + 1) * STYLE['padding']
            is_opened = cell in state['opened']
            is_mine = state['field_generated'] and state['field'].get(cell, -1) == 0.0
            cell_bg_color = STYLE['cell_opened'] if is_opened else STYLE['cell_unopened']
            draw.rectangle(
                [x, y, x + STYLE['cell_size'], y + STYLE['cell_size']],
                fill=cell_bg_color,
                outline=STYLE['cell_border'],
                width=STYLE['border_width']
            )
            try:
                if is_mine and mine_img:
                    if is_opened and explosion_img:
                        ResourceLoader.paste_image_centered(img, explosion_img, x, y, STYLE['cell_size'])
                    else:
                        ResourceLoader.paste_image_centered(img, mine_img, x, y, STYLE['cell_size'])
                elif not is_mine:
                    coefficient = state['field'].get(cell, 1.0) if state['field_generated'] else 1.0
                    text = f"{coefficient:.2f}x"
                    text_color = STYLE['text_opened'] if is_opened else STYLE['text_unopened']
                    icon_font = font_medium if len(text) <= 4 else font_small
                    draw.text(
                        (x + STYLE['cell_size'] // 2, y + STYLE['cell_size'] // 2),
                        text,
                        fill=text_color,
                        font=icon_font,
                        anchor='mm'
                    )
            except Exception as e:
                print(f"❌ Ошибка при обработке ячейки {cell}: {e}")
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        return img_byte_arr

    async def get_final_result_message(self, bot, user_id: int,
                                       session: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Финальный текст результата"""
        if session is None:
            session = self.get_session(bot, user_id)
        state = session['state']
        bet = session['bet']
        multiplier = state['multiplier']
        win_amount = bet * multiplier
        opened_count = len(state['opened'])
        field_display = self._get_field_display(state)
        user_data = await bot.database_interface.get_user(user_id)
        tag = "MINES_LOST"
        custom_data = {"icon": self.icon, "opened_count": opened_count}
        if multiplier > 0:
            custom_data.update({"multiplier": f"{multiplier:.2f}", "win_amount": f"{win_amount:.2f}"})
            tag = "MINES_WIN"
        text = await bot.get_text(user_id, tag, user_data, custom_data)
        return {"text": text, "image": field_display}

    async def get_game_data(self, result: Any, bet_data: Optional[str]) -> dict[str, Any]:
        """Получить структурированные данные игры для логирования"""
        return {"game_type": "mines"}
