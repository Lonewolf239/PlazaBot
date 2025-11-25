import asyncio
from secrets import randbelow
from typing import Any, Optional, Callable, Dict
from . import InteractiveGameBase, GameResult, GameStatus
from ..handlers import InteractiveGameHandlers


class Crash(InteractiveGameBase):
    """Crash Game - коэффициент растет, в случайный момент взрывается 💥"""
    def __init__(self, max_bet: float, config_name: str = "honest"):
        super().__init__(max_bet, config_name)
        self.load_config()
        self.icon = "🚀"
        self._name = {"ru": "Crash", "en": "Crash"}
        self._rules = self.generate_rules()
        self.game_type = "crash"
        self.need_bet_data = False

    def load_config(self):
        """Загружает конфигурацию игры"""
        self.config = {
            "min_crash_coef": 1.01,
            "max_crash_coef": 5.0,
            "increment": 0.015
        }

    def get_config_info(self) -> str:
        return "Коэффициент растет на 0.01 каждый шаг и взрывается в случайный момент 💥"

    def generate_rules(self) -> dict:
        """Генерирует правила игры на русском и английском"""
        rules_ru = f"""
{self.icon} Правила Crash

🎯 КАК ИГРАТЬ

Коэффициент начинает расти с 1.0x и увеличивается на 0.01 каждый шаг.

В случайный момент — КРАХ! 💥

💰 ВЫИГРЫШ

• Нажмите "💰 Забрать" в любой момент

• Забранный коэффициент = ваш выигрыш

• Выигрыш = ставка × коэффициент

💣 КРАХ

• Если не успеете забрать перед крахом

• Вы теряете всю ставку

• Коэффициент падает на 0x

⚡ СТРАТЕГИЯ

• Рискуйте больше = больше выигрыш

• Но коэффициент может крашиться!

• Баланс между жадностью и безопасностью

🍀 Удачи!
"""
        rules_en = f"""
{self.icon} Crash Rules

🎯 HOW TO PLAY

The coefficient starts at 1.0x and increases by 0.01 every step.

At a random moment — CRASH! 💥

💰 WIN

• Click "💰 Cash Out" anytime

• Cashed coefficient = your win

• Prize = bet × coefficient

💣 CRASH

• If you don't cash out before the crash

• You lose your entire bet

• Coefficient drops to 0x

⚡ STRATEGY

• Risk more = bigger win

• But the coefficient can crash!

• Balance between greed and safety

🍀 Good luck!
"""
        return {"ru": rules_ru, "en": rules_en}

    @staticmethod
    def _generate_crash_point() -> float:
        """
        Генерирует точку краша с концентрацией на мелких значениях

        Распределение:
        - ~50% краш в диапазоне 1.01-1.5x
        - ~30% краш в диапазоне 1.5-3.0x
        - Среднее значение: 1.67x

        Параметры:
        - max = 3.0 - максимальный возможный краш
        - power = 2.0 - степень агрессивности (квадрат)
        """
        max_crash = 5.0
        power = 2.0
        random_value = randbelow(1000000) / 1000000
        crash_coef = 1.01 + (max_crash - 1.01) * (random_value ** power)
        return crash_coef

    def _next_coefficient(self, current: float) -> float:
        """Получить следующий коэффициент"""
        return round(current + self.config["increment"], 2)

    @staticmethod
    def _calculate_win(bet: float, coefficient: float) -> float:
        """Рассчитать выигрыш"""
        return round(bet * coefficient, 2)

    async def _auto_update_coefficient(self, bot, user_id: int, message_id: int, send_frame: Optional[Callable] = None):
        """Автоматически обновляет коэффициент с заданной задержкой"""
        while True:
            try:
                await asyncio.sleep(0.05)
                session = self.get_session(bot, user_id)
                if not session:
                    break
                state = session.get('state', {})
                if state.get('crashed') or state.get('cashed_out'):
                    break
                current = state.get('current_coef', 1.0)
                crash_point = state.get('crash_coef', 1.1)
                state['current_coef'] = self._next_coefficient(current)
                if current >= crash_point:
                    state['crashed'] = True
                    self.update_session(bot, user_id, state=state, game_over=True)
                await send_frame(bot, user_id, message_id, self.game_type, await self.get_round_state(bot, user_id))
                self.update_session(bot, user_id, state=state)
            except Exception as e:
                print(f"Error in auto_update_coefficient: {e}")
                break

    async def play(self, bot, user_id: int, message_id: int, bet: float, promoter_data: list[bool | float | float],
                   bet_data: Optional[str] = None, send_frame: Optional[Callable] = None) -> GameResult:
        """Главный loop игры"""
        if not self.get_session(bot, user_id):
            self.create_session_in_manager(bot, user_id, bet, bet_data)
        session = self.get_session(bot, user_id)
        session['state'] = {
            'current_coef': 1.0,
            'crash_coef': self._generate_crash_point(),
            'crashed': False,
            'cashed_out': False,
            'cash_out_coef': None,
        }
        self.update_session(bot, user_id, state=session['state'])
        update_task = asyncio.create_task(self._auto_update_coefficient(bot, user_id, message_id,
                                                                        InteractiveGameHandlers.update_game_frame))
        session['update_task'] = update_task
        round_state = await self.get_round_state(bot, user_id)
        await self.send_initial_message(bot, user_id, message_id, round_state, "crash")
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
        # TODO: сделать когда crash будет добавлен
        bet_data = f"bet_value:{randbelow(2)}"
        while True:
            result = self.generate_result(bet_data)
            win_amount, multiplier = self.evaluate_result(result, bet, bet_data)
            if win_amount > bet:
                break
        result_side = "🦅" if result == 1 else "🪙"
        game_result = GameResult(
            status=GameStatus.FINISHED,
            win_amount=win_amount,
            bet_amount=bet,
            user_bet=None,
            multiplier=multiplier,
            is_win=True,
            game_data=await self.get_game_data(result, None),
            animations_data={
                'icon': self.icon,
                'final_result': f"✨ {result_side} ✨",
                'final_result_image': None
            },
            bet_data=bet_data
        )
        return await self._finalize_game(game_result)

    async def process_action(self, bot, user_id: int, action: str,
                             promoter_data: list[bool | float | float]) -> Dict[str, Any]:
        """Обработать ход игрока: забрать выигрыш или проверить крах"""
        session = self.get_session(bot, user_id)
        if not session:
            return {'error': 'SESSION_EXPIRED'}
        state = session['state']
        if state['crashed'] or state['cashed_out']:
            return {'error': 'Game already finished'}
        if action == 'cashout':
            state['cashed_out'] = True
            state['cash_out_coef'] = state['current_coef']
            if 'update_task' in session:
                session['update_task'].cancel()
            self.update_session(bot, user_id, state=state, game_over=True)
            return {
                'success': True,
                'game_over': True,
                'cashed_out': True,
                'coefficient': state['current_coef']
            }
        return {'error': 'Invalid action'}

    async def is_game_over(self, bot, user_id: int) -> bool:
        """Проверить, завершена ли игра"""
        session = self.get_session(bot, user_id)
        if not session:
            return True
        state = session['state']
        return state.get('crashed', False) or state.get('cashed_out', False)

    async def get_game_result(self, bot, user_id: int) -> tuple[float, float]:
        """Получить финальный выигрыш и множитель"""
        session = self.get_session(bot, user_id)
        if not session:
            return 0, 0
        state = session['state']
        bet = session['bet']
        if state['crashed']:
            return 0, 0
        if state['cashed_out']:
            multiplier = state['cash_out_coef']
            win_amount = self._calculate_win(bet, multiplier)
            return win_amount, multiplier

    async def get_round_state(self, bot, user_id: int) -> dict[str, Any]:
        """Получить текущее состояние раунда для отображения"""
        session = self.get_session(bot, user_id)
        return await self._format_round_state(bot, user_id, session)

    async def _format_round_state(self, bot, user_id: int, session: Dict[str, Any]) -> dict[str, Any]:
        """Форматировать состояние раунда в текст"""
        state = session['state']
        bet = session['bet']
        current_coef = state['current_coef']
        potential_win = self._calculate_win(bet, current_coef)
        status = "🚀 ЛЕТИМ!" if not state['crashed'] and not state['cashed_out'] else ""
        if state['crashed']:
            status = "💥 КРАХ!"
        elif state['cashed_out']:
            status = "✅ ЗАБРАЛИ!"
        text = (
            f"{self.icon} <b>CRASH GAME</b>\n\n"
            f"📈 Текущий коэффициент: <b>{current_coef:.2f}x</b>\n"
            f"💸 Потенциальный выигрыш: {potential_win:.2f}$\n"
            f"{status}"
        )
        return {"text": text}

    async def get_final_result_message(self, bot, user_id: int,
                                       session: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Финальный результат игры"""
        if session is None:
            session = self.get_session(bot, user_id)
        state = session['state']
        bet = session['bet']

        user_data = await bot.database_interface.get_user(user_id)

        if state['crashed']:
            text = (
                f"\n{self.icon} <b>CRASH GAME - РЕЗУЛЬТАТ</b>\n\n"
                f"💥 <b>КРАХ НА {state['current_coef']:.2f}x!</b>"
            )
        elif state['cashed_out']:
            multiplier = state['cash_out_coef']
            win_amount = self._calculate_win(bet, multiplier)
            text = (
                f"\n{self.icon} <b>CRASH GAME - РЕЗУЛЬТАТ</b>\n\n"
                f"✅ <b>УСПЕШНО ЗАБРАЛИ НА {multiplier:.2f}x!</b>\n"
                f"🎉 Выигрыш: {win_amount:.2f}$"
            )
        else:
            text = (
                f"{self.icon} <b>CRASH GAME - РЕЗУЛЬТАТ</b>\n\n"
                f"❌ Что-то пошло не так"
            )

        return {"text": text}

    async def get_game_data(self, result: Any, bet_data: Optional[str]) -> dict[str, Any]:
        """Получить структурированные данные игры для логирования"""
        return {"game_type": "crash"}
