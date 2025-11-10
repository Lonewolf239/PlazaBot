import asyncio
from secrets import randbelow, choice
from collections import Counter
from typing import Callable, Any, Optional
from . import BaseGame, GameStatus, GameResult
from .config import SlotConfig


class CasinoSlot(BaseGame):
    """Слот-машина"""
    def __init__(self, max_bet: float, config_name: str = "honest"):
        """
        Инициализация слота

        :param config_name: 'honest', 'aggressive' или 'generous'
        """
        super().__init__(max_bet, config_name)
        self.load_config()
        self.icon = "🎰"
        self._name = {"ru": "Слот-машина", "en": "Slot machine"}
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
        self.start_output = "🎰 [*] | [*] | [*]"
        self.start_frame_time = 0.03

    def load_config(self):
        config_type_upper = self.config_name.upper()
        if hasattr(SlotConfig, config_type_upper):
            self.config = getattr(SlotConfig, config_type_upper)
        else:
            self.config = SlotConfig.HONEST

    def get_config_info(self) -> str:
        """Получить информацию о конфигурации"""
        probs = self.config['probabilities']
        mults = self.config['multipliers']
        rtp = (
                probs['jackpot'] * mults['jackpot'] +
                probs['big_win'] * mults['big_win'] +
                probs['medium_win'] * mults['medium_win'] +
                probs['small_win'] * mults['small_win'] +
                probs['break_even'] * mults['break_even']
        )
        house_edge = (1 - rtp) * 100
        win_chance = (1 - probs['loss']) * 100
        return (
            f"📊 {self.config['name']}\n"
            f"RTP: {rtp * 100:.1f}% | House Edge: {house_edge:.1f}%\n"
            f"Вероятность выигрыша/при своём: {win_chance:.1f}%"
        )

    def generate_rules(self) -> dict:
        """Генерирует HTML-версию правил с множителями из конфига"""
        multipliers = self.config['multipliers']
        rules_ru = f"""
<b>{self.icon} Правила Слот-машины</b>

<b>🎯 КАК ИГРАТЬ</b>
Нажми кнопку, чтобы запустить три барабана.
Комбинируй одинаковые символы, чтобы выиграть!

<b>💰 МНОЖИТЕЛИ ВЫИГРЫША</b>
• 3× 7️⃣ → {multipliers['jackpot']}x
• 3× 💎 → {multipliers['big_win']}x
• 3× 🔔 → {multipliers['medium_win']}x
• 3× фрукт → {multipliers['small_win']}x
• 2× фрукт → 1x

<b>✅ ВЫИГРЫШ</b>
Собери три одинаковых символа на линии и получи выигрыш!
Джекпот (3× 7️⃣) — наибольший приз!

<b>🍀 Удачи!</b>
"""
        rules_en = f"""
<b>{self.icon} Slot Machine Rules</b>

<b>🎯 HOW TO PLAY</b>
Click the button to spin the three reels.
Match matching symbols to win!

<b>💰 WIN MULTIPLIERS</b>
• f3× 7️⃣ → {multipliers['jackpot']}x
• f3× 💎 → {multipliers['big_win']}x
• f3× 🔔 → {multipliers['medium_win']}x
• f3× fruit → {multipliers['small_win']}x
• 2× fruit → 1x

<b>✅ WIN</b>
Collect three identical symbols on a line and win!
Jackpot (3× 7️⃣) — the biggest prize!

<b>🍀 Good luck!</b>
"""
        return {
            "ru": rules_ru,
            "en": rules_en
        }

    async def play(self, bot, user_id: int, message_id: int,
                   bet: float, bet_data: Optional[str] = None, send_frame: Optional[Callable] = None) -> GameResult:
        """Запуск слота"""
        self.game_over = False
        self.current_status = GameStatus.RUNNING
        self.frame_time = self.start_frame_time

        result = self.generate_result()
        win_amount, multiplier = self.evaluate_result(result, bet, bet_data)
        animation_data = await self.create_animation(result, bot, user_id,
                                                     message_id, send_frame)

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

    def evaluate_result(self, result: list[str], bet: float, bet_data: Optional[str] = None) -> tuple[float, float]:
        """
        Оценка результата спина.
        :return: (сумма выигрыша, множитель)
        """
        mults = self.config['multipliers']
        counts = Counter(result)
        if counts.get('7️⃣', 0) == 3:
            multiplier = mults['jackpot']
            return bet * multiplier, multiplier
        if counts.get('💎', 0) == 3:
            multiplier = mults['big_win']
            return bet * multiplier, multiplier
        if counts.get('🔔', 0) == 3:
            multiplier = mults['medium_win']
            return bet * multiplier, multiplier
        if all(sym in self.fruits for sym in result):
            if len(counts) == 1:
                multiplier = mults['small_win']
                return bet * multiplier, multiplier
            elif len(counts) == 2:
                return bet, 1.0
        return 0, 0.0

    async def create_animation(self, result: list[str], bot, user_id: int,
                               message_id: int, send_frame: Optional[Callable] = None,
                               bet_data: Optional[str] = None) -> dict[str, Any]:
        """
        Анимация спина.
        :return: данные анимации
        """
        animation_frames = []
        if send_frame:
            await send_frame(bot, user_id, message_id, self.start_output)
            animation_frames.append(self.start_output)
        reels = [self.reel_order * 5, self.reel_order * 7, self.reel_order * 9]
        positions = [randbelow(len(reels[r])) for r in range(3)]
        total_steps = 12
        stop_delays = [total_steps, total_steps + 3, total_steps + 6]
        for step in range(total_steps + 7):
            frame_symbols = []
            for reel_index in range(3):
                if step < stop_delays[reel_index]:
                    positions[reel_index] = (positions[reel_index] + 1) % len(reels[reel_index])
                    frame_symbols.append(reels[reel_index][positions[reel_index]])
                else:
                    frame_symbols.append(result[reel_index])
            frame = "🎰 " + " | ".join(frame_symbols)
            if send_frame:
                await send_frame(bot, user_id, message_id, frame)
            animation_frames.append(frame)
            self.frame_time += step * 0.002
            if step < total_steps + 6:
                await asyncio.sleep(self.frame_time)
        return {
            'total_frames': len(animation_frames),
            'final_result': ' | '.join(result),
            'animation_duration': sum(self.frame_time for _ in range(len(animation_frames))),
            "icon": self.icon
        }

    def get_game_data(self, result: list[str], bet_data: Optional[str] = None) -> dict[str, Any]:
        """Создает структуру game_data для слота"""
        counts = Counter(result)
        symbols_info = {
            'counts': dict(counts),
            'all_same': len(counts) == 1,
            'unique_count': len(counts)
        }
        return {
            'spin': result,
            'symbols_info': symbols_info
        }
