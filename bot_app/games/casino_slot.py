import asyncio
import random
from collections import Counter
from typing import Callable, Any, Optional

from .config import SlotConfig
from .base_game import BaseGame, GameStatus, GameResult


class CasinoSlot(BaseGame):
    """Слот-машина"""
    def __init__(self, config: str = "honest"):
        """
        Инициализация слота

        :param config: 'honest', 'aggressive' или 'generous'
        """
        super().__init__(config)
        self.icon = "🎰"
        self._name = {"ru": "Слот-машина", "en": "Slot machine"}
        config_type_upper = config.upper()
        if hasattr(SlotConfig, config_type_upper):
            self.config = getattr(SlotConfig, config_type_upper)
        else:
            self.config = SlotConfig.HONEST
        self._rules = {
            "ru": (
                f"ℹ️ Правила слота\n"
                f"— 3× 7️⃣: выигрыш × {self.config['multipliers']['jackpot']}\n"
                f"— 3× 💎: выигрыш × {self.config['multipliers']['big_win']}\n"
                f"— 3× 🔔: выигрыш × {self.config['multipliers']['medium_win']}\n"
                f"— 3× фрукт: выигрыш × {self.config['multipliers']['small_win']}\n"
                f"— 2× фрукт: вернуть ставку\n"
            ),
            "en": (
                f"ℹ️ Slot Rules\n"
                f"— 3× 7️⃣: win × {self.config['multipliers']['jackpot']}\n"
                f"— 3× 💎: win × {self.config['multipliers']['big_win']}\n"
                f"— 3× 🔔: win × {self.config['multipliers']['medium_win']}\n"
                f"— 3× fruit: win × {self.config['multipliers']['small_win']}\n"
                f"— 2× fruit: return bet\n"
            )
        }
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

    async def play(self, bot, user_id: int, message_id: int,
                   bet: float, bet_date: Optional[str] = None, send_frame: Optional[Callable] = None) -> GameResult:
        """Запуск слота"""
        self.game_over = False
        self.current_status = GameStatus.RUNNING
        self.frame_time = self.start_frame_time

        spin = self.do_spin()
        animation_data = await self.animate(spin, bot, user_id, message_id, send_frame)
        win_amount, multiplier = self.evaluate_spin(spin, bet)

        result = GameResult(
            status=GameStatus.FINISHED,
            win_amount=win_amount,
            bet_amount=bet,
            multiplier=multiplier,
            is_win=win_amount > 0,
            game_data={
                'spin': spin,
                'symbols_info': self._get_spin_info(spin)
            },
            animations_data=animation_data
        )

        return await self._finalize_game(result)

    @staticmethod
    def _get_spin_info(spin: list[str]) -> dict[str, Any]:
        """Получить информацию о результате спина"""
        counts = Counter(spin)
        return {
            'counts': dict(counts),
            'all_same': len(counts) == 1,
            'unique_count': len(counts)
        }

    def evaluate_spin(self, result: list[str], bet: float) -> tuple[float, float]:
        """
        Оценка результата спина.
        :return: (сумма выигрыша, множитель)
        """
        counts = Counter(result)
        mults = self.config['multipliers']
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

    def do_spin(self) -> list[str]:
        """Генерация результата спина на основе конфигурированных вероятностей."""
        probs = self.config['probabilities']
        roll = random.random()
        if roll < probs['jackpot']:
            return ['7️⃣'] * 3
        elif roll < probs['jackpot'] + probs['big_win']:
            return ['💎'] * 3
        elif roll < probs['jackpot'] + probs['big_win'] + probs['medium_win']:
            return ['🔔'] * 3
        elif roll < probs['jackpot'] + probs['big_win'] + probs['medium_win'] + probs['small_win']:
            fruit = random.choice(self.fruits)
            return [fruit] * 3
        elif (roll < probs['jackpot'] + probs['big_win'] + probs['medium_win'] +
              probs['small_win'] + probs['break_even']):
            sym = random.choice(self.fruits)
            other = random.choice([s for s in self.fruits if s != sym])
            result = [sym, sym, other]
            random.shuffle(result)
            return result
        else:
            return [random.choice(self.reel_order) for _ in range(3)]

    async def animate(self, final_result: list[str], bot, user_id: int, message_id: int,
                      send_frame: Optional[Callable]) -> dict[str, Any]:
        """
        Анимация спина.
        :return: данные анимации для логирования/отладки
        """
        animation_frames = []
        if send_frame:
            await send_frame(bot, user_id, message_id, self.start_output)
            animation_frames.append(self.start_output)
        reels = [self.reel_order * 5, self.reel_order * 7, self.reel_order * 9]
        positions = [random.randint(0, len(reels[r]) - 1) for r in range(3)]
        total_steps = 12
        stop_delays = [total_steps, total_steps + 3, total_steps + 6]
        for step in range(total_steps + 7):
            frame_symbols = []
            for reel_index in range(3):
                if step < stop_delays[reel_index]:
                    positions[reel_index] = (positions[reel_index] + 1) % len(reels[reel_index])
                    frame_symbols.append(reels[reel_index][positions[reel_index]])
                else:
                    frame_symbols.append(final_result[reel_index])
            frame = "🎰 " + " | ".join(frame_symbols)
            if send_frame:
                await send_frame(bot, user_id, message_id, frame)
            animation_frames.append(frame)
            self.frame_time += step * 0.002
            if step < total_steps + 6:
                await asyncio.sleep(self.frame_time)
        return {
            'total_frames': len(animation_frames),
            'final_symbols': ' | '.join(final_result),
            'animation_duration': sum(self.frame_time for _ in range(len(animation_frames)))
        }
