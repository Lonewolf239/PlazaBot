from collections import deque
from secrets import SystemRandom
from io import BytesIO
from typing import Any, Optional, Callable, Dict
from PIL import Image, ImageDraw
from . import InteractiveGameBase, GameResult, GameStatus
from ..resources import ResourceLoader


class Blackjack(InteractiveGameBase):
    """Блэкджек — набери 21 очко или больше дилера, не перебирая"""
    def __init__(self, max_bet: float, config_name: str = "honest"):
        super().__init__(max_bet, config_name)
        self.load_config()
        self.icon = "♠️"
        self._name = {"ru": "Блэкджек", "en": "Blackjack"}
        self._rules = self.generate_rules()
        self.need_bet_data = False
        self.game_type = "blackjack"

    def load_config(self):
        """Загрузить конфигурацию игры"""
        self.config = {
            "multiplier_win": 2.0,
            "multiplier_draw": 1.0,
            "multiplier_blackjack": 2.5,
            "max_hand_value": 21
        }

    def get_config_info(self) -> str:
        return f"Выигрыш: ×{self.config['multiplier_win']} | Блэкджек: ×{self.config['multiplier_blackjack']}"

    def generate_rules(self) -> dict:
        """Генерировать правила игры"""
        rules_ru = f"""
<b>{self.icon} Правила Блэкджека</b>

<b>🎯 КАК ИГРАТЬ</b>
Цель: набрать 21 очко или близко к нему, но не превышать.
Вы играете против дилера.
Каждому выдаётся по 2 карты.

<b>💰 МНОЖИТЕЛИ ВЫИГРЫША</b>
• Выигрыш (21 против дилера) ×{self.config['multiplier_win']}
• Блэкджек (21 с первых 2 карт) ×{self.config['multiplier_blackjack']}

<b>✅ СТРАТЕГИЯ</b>
Hit (Брать): взять ещё карту
Stand (Стоять): остановиться, передать ход дилеру

<b>🎲 ОСОБЕННОСТИ</b>
• Туз считается 11 (или 1, если перебор)
• Валет, Дама, Король = 10 очков
• Если вы превышаете 21 → автоматический проигрыш
• Дилер обязан брать до 17 включительно

<b>🍀 Удачи!</b>
"""
        rules_en = f"""
<b>{self.icon} Blackjack Rules</b>

<b>🎯 HOW TO PLAY</b>
Goal: Get 21 or close to it without going over.
You play against the dealer.
Each player gets 2 cards.

<b>💰 WIN MULTIPLIERS</b>
• Win (21 vs Dealer) ×{self.config['multiplier_win']}
• Blackjack (21 with first 2 cards) ×{self.config['multiplier_blackjack']}

<b>✅ STRATEGY</b>
Hit: Take another card
Stand: Stop and pass turn to dealer

<b>🎲 FEATURES</b>
• Ace counts as 11 (or 1 if bust)
• Jack, Queen, King = 10 points
• If you exceed 21 → automatic loss
• Dealer must hit up to 17 including

<b>🍀 Good luck!</b>
"""
        return {
            "ru": rules_ru,
            "en": rules_en
        }

    @staticmethod
    def _init_deck() -> deque:
        """Инициализировать стандартную колоду (52 карты, 1 масть для упрощения)"""
        cards = [card for _ in range(4) for card in range(1, 14)]
        deck_list = list(cards)
        for _ in range(len(deck_list)):
            idx1 = SystemRandom().randint(0, len(deck_list) - 1)
            idx2 = SystemRandom().randint(0, len(deck_list) - 1)
            deck_list[idx1], deck_list[idx2] = deck_list[idx2], deck_list[idx1]
        return deque(deck_list)

    @staticmethod
    def _get_card_from_deck(session: Dict) -> int:
        """
        Вернуть номер карты из колоды в session.
        Если колода закончилась, пересоздать её.
        """
        if 'deck' not in session:
            session['deck'] = Blackjack._init_deck()
        deck = session['deck']
        if not deck:
            session['deck'] = Blackjack._init_deck()
            deck = session['deck']
        return deck.popleft()

    @staticmethod
    def _draw_initial_hands(session: Dict) -> tuple:
        """Раздать начальные руки: 2 карты игроку и 2 карты дилеру"""
        player_hand = [Blackjack._get_card_from_deck(session), Blackjack._get_card_from_deck(session)]
        dealer_hand = [Blackjack._get_card_from_deck(session), Blackjack._get_card_from_deck(session)]
        return player_hand, dealer_hand

    @staticmethod
    def _get_card_value(card: int) -> int:
        """Получить значение карты (1-13: Туз, 2-10, Валет, Дама, Король)"""
        if card == 1:
            return 11
        elif card >= 11:
            return 10
        else:
            return card

    def _calculate_hand_value(self, hand: list[int]) -> tuple[int, int]:
        """Рассчитать значение руки. Возвращает (мягкое значение, жёсткое значение)"""
        value = 0
        aces = 0
        for card in hand:
            card_value = self._get_card_value(card)
            if card == 1:
                aces += 1
            value += card_value
        soft_value = value
        while value > 21 and aces > 0:
            value -= 10
            aces -= 1
        return soft_value, value

    def _is_blackjack(self, hand: list[int]) -> bool:
        """Проверить, является ли рука блэкджеком"""
        if len(hand) != 2:
            return False
        _, value = self._calculate_hand_value(hand)
        return value == 21

    @staticmethod
    def _get_card_suit_filename(card: int) -> str:
        card_names = {
            1: "ace", 2: "2", 3: "3", 4: "4", 5: "5",
            6: "6", 7: "7", 8: "8", 9: "9", 10: "10",
            11: "jack", 12: "queen", 13: "king", 14: "hide"
        }
        return f"{card_names.get(card, 'card')}_spades.png"

    def _get_field_display(self, player_hand: list[int], dealer_hand: list[int],
                           show_dealer_hole: bool = True, title: str = "Blackjack", language: str = "en") -> BytesIO:
        """
        Генерирует красивое двуязычное изображение стола блэкджека с увеличенными картами.
        Карты увеличены с сохранением правильного смещения.
        """
        fonts = ResourceLoader.load_fonts()
        CARD_SCALE = 1.05
        STYLE = {
            'bg_color': '#0a0e27',
            'table_bg': '#051a0a',
            'card_bg': '#1a1a2e',
            'card_border': '#2d5016',
            'text_normal': '#ffffff',
            'text_value': '#4ade80',
            'text_warning': '#ef4444',
            'text_success': '#4ade80',
            'text_secondary': '#94a3b8',
            'card_width': int(80 * CARD_SCALE),
            'card_height': int(109 * CARD_SCALE),
            'padding': 25,
            'spacing': int(15 * CARD_SCALE),
            'border_width': 2,
            'font_title': fonts.get('large'),
            'font_label': fonts.get('medium'),
            'font_value': fonts.get('medium'),
            'font_small': fonts.get('small'),
            'accent_color': '#10b981'
        }
        img_width = 1200
        img_height = 900
        img = Image.new('RGB', (img_width, img_height), color=STYLE['bg_color'])
        draw = ImageDraw.Draw(img)
        draw.text((img_width // 2, 25), title, fill=STYLE['text_value'],
                  font=STYLE['font_title'], anchor='mm')
        draw.line([(STYLE['padding'], 50), (img_width - STYLE['padding'], 50)],
                  fill=STYLE['text_value'], width=3)
        dealer_section_y = 90
        dealer_label = "ДИЛЕР" if language == "ru" else "DEALER"
        draw.rectangle(
            [(STYLE['padding'], dealer_section_y - 5),
             (img_width - STYLE['padding'], dealer_section_y + STYLE['card_height'] + 80)],
            outline=STYLE['accent_color'], width=2)
        draw.text((STYLE['padding'] + 15, dealer_section_y + 20), dealer_label,
                  fill=STYLE['text_value'], font=STYLE['font_label'], anchor='lm')
        _, dealer_value = self._calculate_hand_value(dealer_hand)
        max_cards = max(len(dealer_hand), len(player_hand))
        cards_total_width = max_cards * STYLE['card_width'] + (max_cards - 1) * STYLE['spacing']
        cards_x_start = (img_width - cards_total_width) // 2
        dealer_cards_y = dealer_section_y + 60
        for idx, card in enumerate(dealer_hand):
            card_x = cards_x_start + idx * (STYLE['card_width'] + STYLE['spacing'])
            if idx > 0 and show_dealer_hole:
                self._draw_card(img, card_x, dealer_cards_y, STYLE, 14)
            else:
                self._draw_card(img, card_x, dealer_cards_y, STYLE, card)
        dealer_value_display = "?" if show_dealer_hole else str(dealer_value)
        dealer_color = STYLE['text_normal']
        dealer_status = ""
        if not show_dealer_hole:
            if dealer_value > 21:
                dealer_status = "BUST!" if language == "en" else "ПЕРЕБОР!"
                dealer_color = STYLE['text_warning']
            elif dealer_value == 21:
                dealer_status = "BLACKJACK"
                dealer_color = STYLE['text_success']
            else:
                dealer_color = STYLE['text_value']
        status_x = img_width - STYLE['padding'] - 20
        draw.text((status_x, dealer_section_y + 20),
                  f"Σ: {dealer_value_display}",
                  fill=dealer_color, font=STYLE['font_value'], anchor='rm')
        if dealer_status:
            draw.text((status_x, dealer_section_y + 55), dealer_status,
                      fill=dealer_color, font=STYLE['font_label'], anchor='rm')
        separator_y = dealer_cards_y + STYLE['card_height'] + 50
        draw.line([(STYLE['padding'], separator_y), (img_width - STYLE['padding'], separator_y)],
                  fill=STYLE['card_border'], width=2)
        draw.text((img_width // 2, separator_y), "VS", fill=STYLE['text_secondary'],
                  font=STYLE['font_small'], anchor='mm')
        player_section_y = separator_y + 50
        player_label = "ВАША РУКА" if language == "ru" else "YOUR HAND"
        draw.rectangle([(STYLE['padding'], player_section_y - 5),
                        (img_width - STYLE['padding'], player_section_y + STYLE['card_height'] + 80)],
                       outline=STYLE['accent_color'], width=2)
        draw.text((STYLE['padding'] + 15, player_section_y + 20), player_label,
                  fill=STYLE['text_value'], font=STYLE['font_label'], anchor='lm')
        _, player_value = self._calculate_hand_value(player_hand)
        player_cards_y = player_section_y + 60
        for idx, card in enumerate(player_hand):
            card_x = cards_x_start + idx * (STYLE['card_width'] + STYLE['spacing'])
            self._draw_card(img, card_x, player_cards_y, STYLE, card)
        player_color = STYLE['text_value']
        player_status = ""
        if player_value > 21:
            player_status = "BUST!" if language == "en" else "ПЕРЕБОР!"
            player_color = STYLE['text_warning']
        elif player_value == 21:
            player_status = "BLACKJACK"
            player_color = STYLE['text_success']
        draw.text((status_x, player_section_y + 20),
                  f"Σ: {player_value}", fill=player_color, font=STYLE['font_value'], anchor='rm')
        if player_status:
            draw.text((status_x, player_section_y + 55),
                      player_status, fill=player_color, font=STYLE['font_label'], anchor='rm')
        info_y = img_height - 30
        hit_text = "HIT" if language == "en" else "ЕЩЕ"
        stand_text = "STAND" if language == "en" else "СТОП"
        tips_text = f"← {hit_text}  |  {stand_text} →"
        draw.text((img_width // 2, info_y), tips_text,
                  fill=STYLE['text_secondary'], font=STYLE['font_small'], anchor='mm')
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        return img_byte_arr

    def _draw_card(self, img, x: int, y: int, style: dict, card_value: int = None):
        width = style["card_width"]
        height = style["card_height"]
        card_img = ResourceLoader.load_image_no_square("blackjack", self._get_card_suit_filename(card_value),
                                                       (width, height))
        ResourceLoader.paste_image_centered_no_square(img, card_img, x, y, width, height)

    async def play(self, bot, user_id: int, message_id: int, bet: float,
                   bet_data: Optional[str] = None, send_frame: Optional[Callable] = None) -> GameResult:
        """Главный loop игры"""
        if not self.get_session(bot, user_id):
            self.create_session_in_manager(bot, user_id, bet, bet_data)
        session = self.get_session(bot, user_id)
        if 'deck' not in session:
            session['deck'] = self._init_deck()
        player_hand, dealer_hand = self._draw_initial_hands(session)
        session['state'] = {
            'player_hand': player_hand,
            'dealer_hand': dealer_hand,
            'game_status': 'playing',
            'multiplier': 1.0,
            'result': None
        }
        user_data = await bot.database_interface.get_user(user_id)
        language = user_data.get("language", "ru")
        if self._is_blackjack(player_hand):
            if self._is_blackjack(dealer_hand):
                session['state']['result'] = 'draw'
                session['state']['multiplier'] = self.config['multiplier_draw']
                session['state']['game_status'] = 'finished'
            else:
                session['state']['result'] = 'win'
                session['state']['multiplier'] = self.config['multiplier_blackjack']
                session['state']['game_status'] = 'finished'
            self.update_session(bot, user_id, state=session['state'], game_over=True)
            round_state = await self._format_round_state(bot, user_id, session, language)
            await self.send_initial_message(bot, user_id, message_id, round_state, "blackjack")
            return GameResult(
                status=GameStatus.FINISHED,
                win_amount=bet * session['state']['multiplier'],
                bet_amount=bet,
                user_bet=None,
                multiplier=session['state']['multiplier'],
                is_win=True,
                game_data=await self.get_game_data(None, bet_data),
                animations_data={
                    "final_result": round_state,
                    "icon": self.icon
                },
                bet_data=bet_data,
                session=bot.game_manager.get_user_session(user_id)
            )
        elif self._is_blackjack(dealer_hand):
            session['state']['result'] = 'loss'
            session['state']['multiplier'] = 0
            session['state']['game_status'] = 'finished'
            self.update_session(bot, user_id, state=session['state'], game_over=True)
            round_state = await self._format_round_state(bot, user_id, session, language)
            await self.send_initial_message(bot, user_id, message_id, round_state, "blackjack")
            return GameResult(
                status=GameStatus.FINISHED,
                win_amount=0,
                bet_amount=bet,
                user_bet=None,
                multiplier=0,
                is_win=False,
                game_data=await self.get_game_data(None, bet_data),
                animations_data={
                    "final_result": round_state,
                    "icon": self.icon
                },
                bet_data=bet_data,
                session=bot.game_manager.get_user_session(user_id)
            )
        self.update_session(bot, user_id, state=session['state'])
        round_state = await self._format_round_state(bot, user_id, session, language)
        await self.send_initial_message(bot, user_id, message_id, round_state, "blackjack")
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
        """Обработать ход игрока: 'hit' (брать) или 'stand' (стоять)"""
        session = self.get_session(bot, user_id)
        if not session:
            return {'error': await bot.get_text(user_id, "SESSION_EXPIRED")}
        state = session['state']
        if action == 'hit':
            state['player_hand'].append(self._get_card_from_deck(session))
            _, player_value = self._calculate_hand_value(state['player_hand'])
            if player_value > 21:
                state['game_status'] = 'finished'
                state['multiplier'] = 0
                state['result'] = 'bust'
                self.update_session(bot, user_id, state=state, game_over=True)
                return {
                    'success': True,
                    'action': 'hit',
                    'game_over': True,
                    'result': 'bust'
                }
            self.update_session(bot, user_id, state=state)
            return {
                'success': True,
                'action': 'hit',
                'player_value': player_value,
                'game_over': False
            }
        elif action == 'stand':
            _, dealer_value = self._calculate_hand_value(state['dealer_hand'])
            cheat_chance = 0.25
            use_cheat = SystemRandom().random() < cheat_chance
            while dealer_value < 17:
                _, player_value = self._calculate_hand_value(state['player_hand'])
                if use_cheat and (dealer_value < player_value and dealer_value < 21 and
                                  SystemRandom().random() < 0.7):
                    new_card = self._get_strategic_card_from_deck(session, dealer_value, player_value)
                else:
                    new_card = self._get_card_from_deck(session)
                state['dealer_hand'].append(new_card)
                _, dealer_value = self._calculate_hand_value(state['dealer_hand'])
            _, player_value = self._calculate_hand_value(state['player_hand'])
            if dealer_value > 21:
                state['result'] = 'win'
                state['multiplier'] = self.config['multiplier_win']
            elif player_value > dealer_value:
                state['result'] = 'win'
                state['multiplier'] = self.config['multiplier_win']
            elif player_value == dealer_value:
                state['result'] = 'draw'
                state['multiplier'] = self.config['multiplier_draw']
            else:
                state['result'] = 'loss'
                state['multiplier'] = 0
            state['game_status'] = 'finished'
            self.update_session(bot, user_id, state=state, game_over=True)
            return {
                'success': True,
                'action': 'stand',
                'game_over': True,
                'result': state['result'],
                'player_value': player_value,
                'dealer_value': dealer_value
            }
        return {'error': 'Invalid action'}

    def _get_strategic_card_from_deck(self, session: Dict, current_dealer_value: int, player_value: int) -> int:
        """Получить стратегическую карту из реальной колоды с подглядом"""
        if 'deck' not in session or not session['deck']:
            session['deck'] = self._init_deck()
        deck = session['deck']
        deck_list = list(deck)
        look_ahead = min(3, len(deck_list))
        for idx in range(look_ahead):
            card = deck_list[idx]
            if self._is_card_beneficial(card, current_dealer_value, player_value):
                deck_list[0], deck_list[idx] = deck_list[idx], deck_list[0]
                session['deck'] = deque(deck_list)
                return session['deck'].popleft()
        return deck.popleft()

    def _is_card_beneficial(self, card, current_dealer_value, player_value):
        """Проверяет, выгодна ли карта для дилера"""
        new_value = current_dealer_value + self._get_card_value(card)
        if new_value <= 21:
            return new_value > current_dealer_value and new_value >= 17
        elif new_value > 21:
            return current_dealer_value < player_value
        return False

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

    async def get_round_state(self, bot, user_id: int) -> dict[str, Any]:
        """Получить текущее состояние раунда для отображения"""
        session = self.get_session(bot, user_id)
        user_data = await bot.database_interface.get_user(user_id)
        language = user_data.get("language", "ru")
        return await self._format_round_state(bot, user_id, session, language)

    async def _format_round_state(self, bot, user_id: int, session: Dict, language: str = "ru") -> dict[str, Any]:
        """Форматировать состояние раунда для отображения с изображением"""
        state = session.get('state', {})
        user_data = await bot.database_interface.get_user(user_id)
        game_name = self.name(user_data.get("language", language))
        player_hand = state.get('player_hand', [])
        dealer_hand = state.get('dealer_hand', [])
        game_status = state.get('game_status', 'playing')
        show_dealer_hole = game_status != 'finished'
        image = self._get_field_display(
            player_hand,
            dealer_hand,
            show_dealer_hole=show_dealer_hole,
            title=game_name,
            language=language
        )
        _, player_value = self._calculate_hand_value(player_hand)
        _, dealer_value = self._calculate_hand_value(dealer_hand)
        text = f"{self.icon} {game_name}"
        return {"text": text, "image": image}

    async def get_final_result_message(self, bot, user_id: int) -> dict[str, Any]:
        """Финальный текст результата с изображением"""
        session = self.get_session(bot, user_id)
        state = session['state']
        user_data = await bot.database_interface.get_user(user_id)
        language = user_data.get("language", "ru")
        game_name = self.name(language)
        player_hand = state.get('player_hand', [])
        dealer_hand = state.get('dealer_hand', [])
        _, player_value = self._calculate_hand_value(player_hand)
        _, dealer_value = self._calculate_hand_value(dealer_hand)
        image = self._get_field_display(
            player_hand,
            dealer_hand,
            show_dealer_hole=False,
            title=game_name,
            language=language
        )
        result_map_ru = {
            'win': '✅ ВЫИГРЫШ',
            'draw': '🤝 НИЧЬЯ',
            'loss': '❌ ПРОИГРЫШ',
            'bust': '💥 ПЕРЕБОР'
        }
        result_map_en = {
            'win': '✅ WIN',
            'draw': '🤝 DRAW',
            'loss': '❌ LOSS',
            'bust': '💥 BUST'
        }
        result_map = result_map_en if language == "en" else result_map_ru
        result_text = result_map.get(state['result'], 'FINISHED' if language == "en" else 'ЗАВЕРШЕНО')
        text = f"{self.icon} {game_name} - {result_text}"
        return {"text": text, "image": image}

    async def get_game_data(self, result: Any, bet_data: Optional[str]) -> dict[str, Any]:
        """Получить структурированные данные игры для логирования"""
        return {"game_type": "blackjack"}
