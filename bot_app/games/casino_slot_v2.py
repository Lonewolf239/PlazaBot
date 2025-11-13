import asyncio
from secrets import randbelow, choice
from collections import Counter
from typing import Callable, Any, Optional
from . import BaseGame, GameStatus, GameResult
from .config import SlotV2Config


class CasinoSlotV2(BaseGame):
    """Слот-машина 3x3 с горизонтальными, вертикальными и диагональными линиями"""
    def __init__(self, max_bet: float, config_name: str = "honest"):
        super().__init__(max_bet, config_name)
        self.load_config()
        self.icon = "🎰"
        self._name = {"ru": "Слот-машина V2", "en": "Slot machine V2"}
        self._rules = self.generate_rules()
        self.fruits = ['🍒', '🍋', '🍊', '🍇', '🍉']
        self.symbols = {
            '🍒': 1,
            '🍋': 1,
            '🍊': 1,
            '🍇': 2,
            '🍉': 2,
            '🔔': 5,
            '💎': 8,
            '7️⃣': 15
        }
        self.reel_order = list(self.symbols.keys())
        self.start_output = "🎰\n[*] [*] [*]\n[*] [*] [*]\n[*] [*] [*]"
        self.start_frame_time = 0.05

    def load_config(self):
        config_type_upper = self.config_name.upper()
        if hasattr(SlotV2Config, config_type_upper):
            self.config = getattr(SlotV2Config, config_type_upper)
        else:
            self.config = SlotV2Config.HONEST

    def get_config_info(self) -> str:
        probs = self.config['probabilities']
        mults = self.config['multipliers']
        rtp = (
                probs['jackpot'] * mults['jackpot'] +
                probs['big_win'] * mults['big_win'] +
                probs['medium_win'] * mults['medium_win'] +
                probs['small_win'] * mults['small_win']
        )
        house_edge = (1 - rtp) * 100
        win_chance = (1 - probs['loss']) * 100
        return (
            f"📊 {self.config['name']}\n"
            f"RTP: {rtp * 100:.1f}% | House Edge: {house_edge:.1f}%\n"
            f"Вероятность выигрыша/при своём: {win_chance:.1f}%"
        )

    def generate_rules(self) -> dict:
        multipliers = self.config['multipliers']
        rules_ru = f"""
{self.icon} Правила Slot V2

🎯 КАК ИГРАТЬ
Нажми кнопку, чтобы запустить девять ячеек.
Комбинируй одинаковые символы по линиям для выигрыша!

💰 МНОЖИТЕЛИ ЛИНИЙ
• 3× 7️⃣ на линии — {multipliers['jackpot']}x
• 3× 💎 на линии — {multipliers['big_win']}x
• 3× 🔔 на линии — {multipliers['medium_win']}x
• 3× фруктов на линии — {multipliers['small_win']}x

✅ ВЫИГРЫШ
Совпадения по любой горизонтали, вертикали или диагонали

🍀 Удачи!
"""
        rules_en = f"""
{self.icon} Slot V2 Rules

🎯 HOW TO PLAY
Click the button to spin a 3x3 grid.
Match symbols on any line to win!

💰 LINE MULTIPLIERS
• 3× 7️⃣ in a line — {multipliers['jackpot']}x
• 3× 💎 in a line — {multipliers['big_win']}x
• 3× 🔔 in a line — {multipliers['medium_win']}x
• 3× fruit in a line — {multipliers['small_win']}xW

✅ WIN
Matches on any row, column or diagonal

🍀 Good luck!
"""
        return {"ru": rules_ru, "en": rules_en}

    async def play(self, bot, user_id: int, message_id: int, bet: float, bet_data: Optional[str] = None,
                   send_frame: Optional[Callable] = None) -> GameResult:
        """Запуск слота"""
        self.game_over = False
        self.current_status = GameStatus.RUNNING
        self.frame_time = self.start_frame_time
        result = [self.generate_result(), self.generate_result(), self.generate_result()]
        win_amount, multiplier = self.evaluate_result(result, bet, bet_data)
        animation_data = await self.create_animation(result, bot, user_id, message_id, send_frame)
        game_result = GameResult(
            status=GameStatus.FINISHED,
            win_amount=win_amount,
            bet_amount=bet,
            user_bet=None,
            multiplier=multiplier,
            is_win=win_amount > 0,
            game_data=self.get_game_data(result, bet_data),
            animations_data=animation_data,
            bet_data=bet_data
        )
        return await self._finalize_game(game_result)

    def generate_result(self, bet_data: Optional[str] = None) -> list[str]:
        """Генерация результата спина на основе конфигурированных вероятностей."""
        probs = self.config['probabilities']
        roll = randbelow(1000) / 1000.0
        if roll < probs['jackpot']:
            return ['7️⃣'] * 3
        elif roll < probs['jackpot'] + probs['big_win']:
            return ['💎'] * 3
        elif roll < probs['jackpot'] + probs['big_win'] + probs['medium_win']:
            return ['🔔'] * 3
        elif roll < probs['jackpot'] + probs['big_win'] + probs['medium_win'] + probs['small_win']:
            fruit = choice(self.fruits)
            return [fruit] * 3
        elif (roll < probs['jackpot'] + probs['big_win'] + probs['medium_win'] +
              probs['small_win'] + probs['break_even']):
            sym = choice(self.fruits)
            other = choice([s for s in self.fruits if s != sym])
            result = [sym, sym, other]
            indices = list(range(len(result)))
            shuffled_indices = []
            while indices:
                idx = choice(indices)
                shuffled_indices.append(idx)
                indices.remove(idx)
            return [result[i] for i in shuffled_indices]
        else:
            return [choice(self.reel_order) for _ in range(3)]

    @staticmethod
    def get_all_lines(grid: list[list[str]]) -> list[list[str]]:
        """Получить все линии для проверки (3 горизонтальных, 3 вертикальных, 2 диагональных)"""
        lines = []
        lines.extend(grid)
        for col in range(3):
            lines.append([grid[row][col] for row in range(3)])
        lines.append([grid[i][i] for i in range(3)])
        lines.append([grid[i][2 - i] for i in range(3)])
        return lines

    def evaluate_result(self, grid: list[list[str]], bet: float, bet_data: Optional[str] = None) -> tuple[float, float]:
        """Оценка результата спина с перемножением множителей"""
        mults = self.config['multipliers']
        lines = self.get_all_lines(grid)
        multipliers_list = []
        for line in lines:
            counts = Counter(line)
            if counts.get('7️⃣', 0) == 3:
                multipliers_list.append(mults['jackpot'])
            elif counts.get('💎', 0) == 3:
                multipliers_list.append(mults['big_win'])
            elif counts.get('🔔', 0) == 3:
                multipliers_list.append(mults['medium_win'])
            else:
                fruit_counts = {sym: count for sym, count in counts.items() if sym in self.fruits}
                if fruit_counts:
                    if any(count == 3 for count in fruit_counts.values()):
                        multipliers_list.append(mults['small_win'])
        if multipliers_list:
            final_multiplier = 1.0
            for mult in multipliers_list:
                final_multiplier *= mult
            win_amount = bet * final_multiplier
            return win_amount, final_multiplier
        else:
            return 0.0, 0.0

    @staticmethod
    def format_grid_frame(grid: list[list[str]], highlight_line_idx: Optional[int] = None) -> str:
        """Форматирование сетки для вывода с опциональной подсветкой линии"""
        frame_lines = []
        for row_idx, row in enumerate(grid):
            row_str = " | ".join(row)
            if highlight_line_idx is not None:
                if highlight_line_idx < 3:
                    if row_idx == highlight_line_idx:
                        row_str = " | ".join(row)
            frame_lines.append(row_str)

        return "🎰\n" + "\n".join(frame_lines)

    async def create_animation(self, grid: list[list[str]], bot, user_id: int, message_id: int,
                               send_frame: Optional[Callable] = None, bet_data: Optional[str] = None) -> dict[str, Any]:
        """Анимация спина с вращением колонок"""
        animation_frames = []
        if send_frame:
            await send_frame(bot, user_id, message_id, {"text": self.start_output})
            animation_frames.append(self.start_output)
        reels = [self.reel_order * 6, self.reel_order * 6, self.reel_order * 6]
        positions = [randbelow(len(reel)) for reel in reels]
        total_steps = 15
        stop_delays = [total_steps, total_steps + 4, total_steps + 8]
        for step in range(total_steps + 10):
            frame_grid = [['*', '*', '*'], ['*', '*', '*'], ['*', '*', '*']]
            for col_idx in range(3):
                if step < stop_delays[col_idx]:
                    positions[col_idx] = (positions[col_idx] + 1) % len(reels[col_idx])
                    current_pos = positions[col_idx]
                    prev_pos = (current_pos - 1) % len(reels[col_idx])
                    next_pos = (current_pos + 1) % len(reels[col_idx])
                    frame_grid[0][col_idx] = reels[col_idx][prev_pos]
                    frame_grid[1][col_idx] = reels[col_idx][current_pos]
                    frame_grid[2][col_idx] = reels[col_idx][next_pos]
                else:
                    for row_idx in range(3):
                        frame_grid[row_idx][col_idx] = grid[row_idx][col_idx]
            frame = "🎰\n"
            for row in frame_grid:
                frame += " | ".join(row) + "\n"
            frame = frame.rstrip()
            if send_frame:
                await send_frame(bot, user_id, message_id, {"text": frame})
            animation_frames.append(frame)
            frame_delay = self.start_frame_time + (step / total_steps) * 0.08
            if step < total_steps + 9:
                await asyncio.sleep(frame_delay)
        final_frame = self.format_grid_frame(grid)
        if send_frame:
            await send_frame(bot, user_id, message_id, {"text": final_frame})
        animation_frames.append(final_frame)
        return {
            'total_frames': len(animation_frames),
            'final_result': final_frame,
            'icon': self.icon,
            'animation_type': 'reel_spin'
        }

    def get_game_data(self, grid: list[list[str]], bet_data: Optional[str] = None,
                      lines_hit: Optional[list] = None) -> dict[str, Any]:
        """Создаёт структуру game_data для слота"""
        flat = [sym for row in grid for sym in row]
        counts = Counter(flat)
        symbols_info = {
            'counts': dict(counts),
            'unique_count': len(counts),
            'total_symbols': 9
        }
        return {
            'grid': grid,
            'symbols_info': symbols_info,
            'hits': lines_hit or [],
            'total_lines_checked': 8
        }
