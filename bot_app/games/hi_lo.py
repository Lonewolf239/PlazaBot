import random
from typing import Any, Optional, Callable, Dict
from . import InteractiveGameBase, GameResult, GameStatus


class HiLo(InteractiveGameBase):
    """Hi-Lo игра — угадай выше или ниже будет следующая карта"""
    def __init__(self, max_bet: float, config_name: str = "honest"):
        super().__init__(max_bet, config_name)
        self.load_config()
        self.icon = "🎴"
        self._name = {"ru": "Hi-Lo", "en": "Hi-Lo"}
        self._rules = self.generate_rules()
        self.need_bet_data = False

    def load_config(self):
        """Загрузить конфигурацию игры"""
        self.config = {
            "multiplier_win": 1.25,
            "max_streak": 10,
            "card_values": list(range(1, 14))
        }

    def get_config_info(self) -> str:
        return f"Коэффициент выигрыша: {self.config['multiplier_win']}x | Макс серия: {self.config['max_streak']}"

    def generate_rules(self) -> dict:
        multiplier = self.config['multiplier_win']
        max_streak = self.config['max_streak']
        rules_ru = f"""
<b>{self.icon} Правила Hi-Lo</b>

<b>🎯 КАК ИГРАТЬ</b>
Вам показывается первая карта.
Предскажите: будет ли следующая карта ВЫШЕ или НИЖЕ.
За каждый правильный ход множитель растёт.

<b>💰 МНОЖИТЕЛИ ВЫИГРЫША</b>
• 1 правильный ход → ×{multiplier}
• 2 правильных хода → ×{multiplier * 2:.2f}
• 3 правильных хода → ×{multiplier * 3:.2f}
• ...до {max_streak} ходов подряд

<b>✅ ВЫИГРЫШ</b>
Каждый правильный прогноз увеличивает ваш множитель на {multiplier}x.
Максимум {max_streak} ходов подряд до автоматического выигрыша!

<b>🎲 ОСОБЕННОСТИ</b>
Одинаковое значение карт = поражение и конец игры
❌ Неправильный прогноз = проигрыш и конец игры

<b>🍀 Удачи!</b>
"""
        rules_en = f"""
<b>{self.icon} Hi-Lo Rules</b>

<b>🎯 HOW TO PLAY</b>
You see the first card.
Predict if the next card is HIGHER or LOWER.
Each correct prediction increases your multiplier.

<b>💰 WIN MULTIPLIERS</b>
• 1 correct prediction → ×{multiplier}
• 2 correct predictions → ×{multiplier * 2:.2f}
• 3 correct predictions → ×{multiplier * 3:.2f}
• ...up to {max_streak} predictions in a row

<b>✅ WIN</b>
Each correct prediction multiplies your winnings by {multiplier}x.
Maximum {max_streak} predictions in a row for auto-win!

<b>🎲 FEATURES</b>
Same card value = loss and game over
❌ Wrong prediction = loss and game over

<b>🍀 Good luck!</b>
"""
        return {
            "ru": rules_ru,
            "en": rules_en
        }

    async def play(self, bot, user_id: int, message_id: int, bet: float,
                   bet_data: Optional[str] = None, send_frame: Optional[Callable] = None) -> GameResult:
        """Главный loop игры"""
        if not self.get_session(bot, user_id):
            self.create_session_in_manager(bot, user_id, bet, bet_data)
        session = self.get_session(bot, user_id)
        current_card = random.choice(self.config['card_values'])
        session['state'] = {
            'current_card': current_card,
            'streak': 0,
            'multiplier': 1.0,
            'history': []
        }
        self.update_session(bot, user_id, state=session['state'])
        round_state = await self._format_round_state(bot, user_id, session)
        if send_frame:
            await self.send_initial_message(bot, user_id, message_id, round_state, "hilo")
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

    async def process_action(self, bot, user_id: int, action: str) -> Dict[str, Any]:
        """Обработать ход игрока: 'high' или 'low'"""
        session = self.get_session(bot, user_id)
        if not session:
            return {'error': await bot.get_text(user_id, "SESSION_EXPIRED")}
        if action == 'surrender':
            state = session['state']
            if state['streak'] == 0:
                state['multiplier'] = 1.0
            self.update_session(bot, user_id, state=state, game_over=True)
            return {
                'success': True,
                'correct': False,
                'game_over': True,
                'surrendered': True
            }
        state = session['state']
        new_card = random.choice(self.config['card_values'])
        current_card = state['current_card']
        is_correct = False
        if action == 'high' and new_card > current_card:
            is_correct = True
        elif action == 'low' and new_card < current_card:
            is_correct = True
        if new_card == current_card:
            is_correct = False
        state['current_card'] = new_card
        if is_correct:
            state['streak'] += 1
            state['multiplier'] = self.config['multiplier_win'] * state['streak']
            state['history'].append({
                'prediction': action,
                'result': new_card,
                'correct': True
            })
            self.update_session(bot, user_id, state=state)
            if state['streak'] >= self.config['max_streak']:
                self.update_session(bot, user_id, game_over=True)
                return {
                    'success': True,
                    'correct': True,
                    'game_over': True
                }
            return {
                'success': True,
                'correct': True,
                'streak': state['streak'],
                'multiplier': f"×{state['multiplier']:.1f}"
            }
        else:
            state['multiplier'] = 0
            state['history'].append({
                'prediction': action,
                'result': new_card,
                'correct': False
            })
            self.update_session(bot, user_id, state=state, game_over=True)
            return {
                'success': False,
                'correct': False,
                'game_over': True
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
        bet = session['bet']
        multiplier = state['multiplier']
        win_amount = bet * multiplier
        return win_amount, multiplier

    async def get_round_state(self, bot, user_id: int) -> str:
        """Получить текущее состояние раунда для отображения"""
        session = self.get_session(bot, user_id)
        return await self._format_round_state(bot, user_id, session)

    async def _format_round_state(self, bot, user_id: int, session: Dict[str, Any]) -> str:
        """Форматировать состояние раунда в текст"""
        state = session['state']
        current_card = state['current_card']
        streak = state['streak']
        multiplier = state['multiplier']
        card_display = self._get_card_display(current_card)
        user_data = await bot.database_interface.get_user(user_id)
        custom_data = {"icon": self.icon, "card_display": card_display,
                       "streak": streak, "multiplier": multiplier}
        return await bot.get_text(user_id, "HILO_ROUND_STATE", user_data, custom_data)

    @staticmethod
    def _get_card_display(value: int) -> str:
        """Преобразить значение карты в красивый формат"""
        card_names = {
            1: "🂡 ACE",
            11: "🂫 JACK",
            12: "🂭 QUEEN",
            13: "🂮 KING"
        }
        if value in card_names:
            return card_names[value]
        return f"{'🃏'} {value}"

    async def get_final_result_text(self, bot, user_id: int) -> str:
        """Финальный текст результата"""
        session = self.get_session(bot, user_id)
        state = session['state']
        current_card = state['current_card']
        card_display = self._get_card_display(current_card)
        bet = session['bet']
        win_amount = bet * state['multiplier']
        user_data = await bot.database_interface.get_user(user_id)
        custom_data = {"last_card": card_display, "streak": state['streak'],
                       "multiplier": state['multiplier'], "win_amount": win_amount}
        return await bot.get_text(user_id, "HILO_FINAL_RESULT", user_data, custom_data)

    async def get_game_data(self, result: Any, bet_data: Optional[str]) -> dict[str, Any]:
        """Получить структурированные данные игры для логирования"""
        return {"game_type": "hilo"}
