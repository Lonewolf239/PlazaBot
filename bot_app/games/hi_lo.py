import random
from typing import Any, Optional, Callable, Dict
from . import InteractiveGameBase, GameResult, GameStatus


class HiLo(InteractiveGameBase):
    """Hi-Lo игра — угадай выше или ниже будет следующая карта"""

    def __init__(self, max_bet: float, config_name: str = "honest"):
        super().__init__(max_bet, config_name)
        self.load_config()
        self.icon = "📊"
        self._name = {"ru": "Hi-Lo", "en": "Hi-Lo"}
        self._rules = self.generate_rules()

        # Конфиг за правила выигрыша
        self.config_data = {
            "multiplier_win": 2.0,  # x2 за каждый правильный ход
            "max_streak": 10,  # Максимум правильных ходов подряд
            "card_values": list(range(1, 14))  # Значения карт (1-13)
        }

    def load_config(self):
        """Загрузить конфигурацию игры"""
        self.config = {
            "multiplier_win": 2.0,
            "max_streak": 10,
            "card_values": list(range(1, 14))
        }

    def get_config_info(self) -> str:
        return f"Коэффициент выигрыша: {self.config['multiplier_win']}x | Макс серия: {self.config['max_streak']}"

    def generate_rules(self) -> dict:
        return {
            "ru": f"""
🎴 **Правила Hi-Lo:**
1️⃣ Вам показывается первая карта
2️⃣ Предскажите: будет ли следующая карта **ВЫШЕ** или **НИЖЕ**
3️⃣ За каждый правильный ход множитель ×2
4️⃣ Максимум {self.config.get('max_streak', 10)} правильных ходов подряд
5️⃣ Ошибка = конец игры
⚠️ Одинаковое значение = поражение
            """,
            "en": f"""
🎴 **Hi-Lo Rules:**
1️⃣ You see the first card
2️⃣ Predict if next card is **HIGHER** or **LOWER**
3️⃣ Each correct prediction = ×2 multiplier
4️⃣ Maximum {self.config.get('max_streak', 10)} consecutive wins
5️⃣ Wrong guess = game over
⚠️ Same value = loss
            """
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

        round_state = self._format_round_state(session)

        if send_frame:
            await self.send_initial_message(bot, user_id, message_id, round_state, "hilo")

        return GameResult(
            status=GameStatus.RUNNING,
            win_amount=0,
            bet_amount=int(bet),
            user_bet="",
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
        """
        Обработать ход игрока: 'high' или 'low'
        """
        if not bot:
            return {'error': '❌ Ошибка: bot не инициализирован'}

        session = self.get_session(bot, user_id)

        if not session:
            return {'error': '❌ Сессия истекла'}

        if action == 'surrender':
            state = session['state']
            self.update_session(bot, user_id, state=state, game_over=True)

            return {
                'success': True,
                'correct': False,
                'message': f"🏁 Вы вышли из игры!\n🔥 Финальная серия: {state['streak']}\n"
                           f"💰 Выигрыш: ×{state['multiplier']:.2f}",
                'game_over': True,
                'surrendered': True
            }

        state = session['state']

        # Генерируем новую карту
        new_card = random.choice(self.config['card_values'])
        current_card = state['current_card']

        # Проверяем предсказание
        is_correct = False
        if action == 'high' and new_card > current_card:
            is_correct = True
        elif action == 'low' and new_card < current_card:
            is_correct = True

        # Если одинаковое значение — автопроигрыш
        if new_card == current_card:
            is_correct = False

        # Обновляем состояние
        if is_correct:
            state['streak'] += 1
            state['multiplier'] = self.config['multiplier_win'] ** state['streak']
            state['current_card'] = new_card
            state['history'].append({
                'prediction': action,
                'result': new_card,
                'correct': True
            })
            self.update_session(bot, user_id, state=state)

            # Проверяем макс серию
            if state['streak'] >= self.config['max_streak']:
                self.update_session(bot, user_id, game_over=True)
                return {
                    'success': True,
                    'correct': True,
                    'message': f"✅ Правильно! Карта: {new_card}\n🎉 Макс серия достигнута!",
                    'game_over': True
                }

            return {
                'success': True,
                'correct': True,
                'message': f"✅ Правильно! Карта: {new_card}",
                'streak': state['streak'],
                'multiplier': f"×{state['multiplier']:.1f}"
            }

        else:
            state['history'].append({
                'prediction': action,
                'result': new_card,
                'correct': False
            })
            self.update_session(bot, user_id, state=state, game_over=True)

            return {
                'success': False,
                'correct': False,
                'message': f"❌ Неправильно! Карта была: {new_card}\n🏁 Игра окончена!\n"
                           f"🔥 Финальная серия: {state['streak']}",
                'game_over': True
            }

    async def is_game_over(self, bot, user_id: int) -> bool:
        """Проверить, завершена ли игра"""
        if not bot:
            return True

        session = self.get_session(bot, user_id)
        if not session:
            return True
        return session.get('game_over', False)

    async def get_game_result(self, bot, user_id: int) -> tuple[float, float]:
        """Получить финальный выигрыш и множитель"""
        if not bot:
            return 0, 0

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
        if not bot:
            return "❌ Ошибка инициализации"

        session = self.get_session(bot, user_id)
        if not session:
            return "❌ Сессия не найдена"

        return self._format_round_state(session)

    def _format_round_state(self, session: Dict[str, Any]) -> str:
        """Форматировать состояние раунда в текст"""
        state = session['state']
        current_card = state['current_card']
        streak = state['streak']
        multiplier = state['multiplier']

        # Красивое отображение карты
        card_suit = self._get_card_display(current_card)

        text = f"""📊 **Hi-Lo Game**
Текущая карта: {card_suit}
🔥 Серия: {streak}
💰 Множитель: ×{multiplier:.2f}"""
        return text

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
        if not bot:
            return "❌ Ошибка"

        session = self.get_session(bot, user_id)
        if not session:
            return "❌ Ошибка"

        state = session['state']
        return f"""🏁 Hi-Lo завершена!
🔥 Серия: {state['streak']}
💰 Множитель: ×{state['multiplier']:.2f}"""

    async def get_game_data(self, result: Any, bet_data: Optional[str]) -> dict[str, Any]:
        """Получить структурированные данные игры для логирования"""
        return {
            "game_type": "hi_lo",
            "version": "1.0"
        }
