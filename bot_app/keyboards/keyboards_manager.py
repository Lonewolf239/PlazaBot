from typing import List, Any, Type, Dict, Optional
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot_app.games import BaseGame, BetParameter


class Messages:
    TEXT = {
        "MAIN_MENU": {
            "games": {"ru": "Начать игру", "en": "Start Game"},
            "profile": {"ru": "Профиль", "en": "Profile"},
            "settings": {"ru": "Настройки", "en": "Settings"},
            "balance": {"ru": "Баланс", "en": "Balance"},
            "rules": {"ru": "Правила игры", "en": "Rules"},
            "help": {"ru": "Поддержка", "en": "Help"},
            "news": {"ru": "Новостной канал", "en": "News channel"},
            "referral": {"ru": "Рефералка", "en": "Referral"},
            "admin": {"ru": "Админ-панель", "en": "Admin Panel"}
        },
        "SETTINGS": {
            "game": {"ru": "Сменить игру", "en": "Change Game"},
            "language": {"ru": "Сменить язык", "en": "Change Language"},
            "email": {"ru": "Сменить почту", "en": "Change Email"}
        },
        "BALANCE": {
            "deposit": {"ru": "Пополнить баланс", "en": "Deposit"},
            "withdraw": {"ru": "Вывести средства", "en": "Withdraw"},
            "pay": {"ru": "Оплатить", "en": "Pay"},
            "check": {"ru": "Проверить", "en": "Check"},
            "cancel_payment": {"ru": "Отменить платёж", "en": "Cancel Payment"}
        },
        "ADMIN": {
            "summary": {"ru": "Сводка по балансу", "en": "Balance Summary"},
            "players": {"ru": "Список игроков", "en": "Player List"},
            "logs": {"ru": "Логи событий", "en": "Event Logs"},
            "database": {"ru": "Показать БД", "en": "Show Database"},
            "issue_balance": {"ru": "Выдать 1000$", "en": "Give out $1000"},
            "reset_balance": {"ru": "Обнулить баланс", "en": "Reset balance"},
            "get_balance": {"ru": "Получить баланс", "en": "Get balance"},
            "game_settings": {"ru": "Настройки игры", "en": "Game Settings"},
            "game_config": {"ru": "Конфиг игры", "en": "Game Config"},
            "bot_config": {"ru": "Настройка бота", "en": "Bot setup"},
            "set_bot_channel_config": {"ru": "Изменить канал", "en": "Change channel"},
            "set_bot_news_channel_config": {"ru": "Изменить новостной", "en": "Change news"},
            "remove_bot_config": {"ru": "Удалить", "en": "Remove"},
            "max_bet": {"ru": "Макс ставка", "en": "Max Bet"},
            "message_channel": {"ru": "Отправить сообщение", "en": "Send a message"},
            "custom_message": {"ru": "Кастомное сообщение", "en": "Custom message"},
            "startup_channel": {"ru": "Отправить стартовое", "en": "Send start"}
        },
        "REFERRAL": {
            "create": {"ru": "Создать рефералку", "en": "Create Referral"},
            "stats": {"ru": "Статистика рефералки", "en": "Referral Stats"}
        },
        "OTHERS": {
            "cancel": {"ru": "Отмена", "en": "Cancel"},
            "back": {"ru": "Назад", "en": "Back"},
            "confirm_yes": {"ru": "Да", "en": "Yes"},
            "confirm_no": {"ru": "Нет", "en": "No"},
            "try_again": {"ru": "Попробовать снова", "en": "Try again"},
            "prev_page": {"ru": "", "en": ""},
            "next_page": {"ru": "", "en": ""},
            "did_deb": {"en": "Играй сейчас/Play Now"},
            "bot_open": {"en": "Открыть бота/Open the bot"}
        }
    }

    ICONS = {
        "MAIN_MENU": {
            "games": "",
            "profile": "👤",
            "settings": "⚙️",
            "balance": "💳",
            "rules": "📖",
            "help": "🆘",
            "news": "📢",
            "referral": "🔗",
            "admin": "👨‍💻"
        },
        "SETTINGS": {
            "game": "🎮",
            "language": "🌐",
            "email": "📧"
        },
        "BALANCE": {
            "deposit": "➕",
            "withdraw": "💸",
            "pay": "💳",
            "check": "🔍",
            "cancel_payment": "❌"
        },
        "ADMIN": {
            "summary": "📊",
            "players": "👥",
            "logs": "🗒️",
            "database": "🗄️",
            "issue_balance": "💰",
            "reset_balance": "♻️",
            "get_balance": "🏦",
            "game_settings": "🛠️",
            "game_config": "🧩",
            "bot_config": "⚙️",
            "set_bot_channel_config": "⚙️",
            "set_bot_news_channel_config": "⚙️",
            "remove_bot_config": "🗑️",
            "max_bet": "🔧",
            "message_channel": "💬",
            "custom_message": "📝",
            "startup_channel": "🚀"
        },
        "REFERRAL": {
            "create": "➕",
            "stats": "👥"
        },
        "OTHERS": {
            "cancel": "❌",
            "back": "◀️",
            "confirm_yes": "✅",
            "confirm_no": "❌",
            "try_again": "🔄",
            "prev_page": "◀️",
            "next_page": "▶️",
            "did_deb": "🎮",
            "bot_open": "🤖"
        }
    }

    @staticmethod
    def get_text(tag, button, language) -> str:
        return f"{Messages.ICONS[tag][button]} {Messages.TEXT[tag][button][language]}"


class KeyboardManager:
    @staticmethod
    def get_back_keyboard(language_code: str, callback_data: str = "back") -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.button(text=Messages.get_text("OTHERS", "back", language_code), callback_data=callback_data)
        kb.adjust(1)
        return kb.as_markup()

    @staticmethod
    def get_delete_keyboard() -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.button(text="🗑", callback_data="delete")
        kb.adjust(1)
        return kb.as_markup()

    @staticmethod
    def get_main_keyboard(game_icon: str, admin: bool, language_code: str, support_url: str,
                          news_channel_username: str = None) -> InlineKeyboardMarkup:
        keyboard = [
            [
                InlineKeyboardButton(
                    text=f"{game_icon}{Messages.get_text('MAIN_MENU', 'games', language_code)}",
                    callback_data="select-bet"
                )
            ],
            [
                InlineKeyboardButton(
                    text=Messages.get_text("MAIN_MENU", "profile", language_code),
                    callback_data="profile"
                ),
                InlineKeyboardButton(
                    text=Messages.get_text("MAIN_MENU", "balance", language_code),
                    callback_data="balance"
                )
            ],
            [
                InlineKeyboardButton(
                    text=Messages.get_text("SETTINGS", "game", language_code),
                    callback_data="change-game"
                ),
                InlineKeyboardButton(
                    text=Messages.get_text("SETTINGS", "language", language_code),
                    callback_data="change-language"
                )
            ],
            [
                InlineKeyboardButton(
                    text=Messages.get_text("MAIN_MENU", "rules", language_code),
                    callback_data="rules"
                ),
                InlineKeyboardButton(
                    text=Messages.get_text("MAIN_MENU", "referral", language_code),
                    callback_data="referral-menu"
                )
            ]
        ]
        help_keyboard_row = [
            InlineKeyboardButton(
                text=Messages.get_text("MAIN_MENU", "help", language_code),
                url=f"https://t.me/{support_url}"
            )
        ]
        if news_channel_username:
            help_keyboard_row.append(
                InlineKeyboardButton(
                    text=Messages.get_text("MAIN_MENU", "news", language_code),
                    url=f"https://t.me/{news_channel_username}"
                )
            )
        keyboard.append(help_keyboard_row)
        if admin:
            keyboard.append([
                InlineKeyboardButton(
                    text=Messages.get_text("MAIN_MENU", "admin", language_code),
                    callback_data="admin-panel"
                )
            ])
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def get_register_cancel_keyboard(language_code: str) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.button(text=Messages.get_text("OTHERS", "cancel", language_code),
                  callback_data="register_cancel")
        kb.adjust(1)
        return kb.as_markup()

    @staticmethod
    def get_change_game_keyboard(games: Dict[str, Type[BaseGame]], language_code: str) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        for game_id, game_class in games.items():
            game_instance = game_class(50)
            kb.button(
                text=f"{game_instance.icon} {game_instance.name(language_code)}",
                callback_data=f"set-game:{game_id}"
            )
        kb.adjust(2)
        return kb.as_markup()

    @staticmethod
    def get_language_keyboard() -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.button(text="🇷🇺", callback_data="language:ru")
        kb.button(text="🇺🇸", callback_data="language:en")
        kb.adjust(2)
        return kb.as_markup()

    @staticmethod
    def get_balance_keyboard(language_code: str) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.button(text=Messages.get_text("BALANCE", "deposit", language_code), callback_data="balance-deposit")
        kb.button(text=Messages.get_text("BALANCE", "withdraw", language_code), callback_data="balance-withdraw")
        kb.button(text=Messages.get_text("OTHERS", "back", language_code),
                  callback_data="back")
        kb.adjust(2, 1)
        return kb.as_markup()

    @staticmethod
    def get_currency_keyboard(language_code: str, currency_list: tuple,
                              operation_type: str, size: int = 2) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        for currency in currency_list:
            kb.button(text=f"{currency["name"]} [{currency["code"]}]",
                      callback_data=f"{operation_type}-select-currency:{currency["code"]}")
        kb.button(text=Messages.get_text("OTHERS", "cancel", language_code),
                  callback_data="back")
        kb.adjust(size)
        return kb.as_markup()

    @staticmethod
    async def get_interactive_game_keyboard(game_type: str, language: str,
                                            game_session: Optional[Dict] = None) -> InlineKeyboardMarkup:
        """Клавиатура для интерактивной игры с кнопкой завершения"""
        kb = InlineKeyboardBuilder()
        if game_type.startswith("hilo"):
            kb.button(text="📈 Выше" if language == "ru" else "📈 Higher",
                      callback_data="game_action:hilo_started:high")
            kb.button(text="📉 Ниже" if language == "ru" else "📉 Lower",
                      callback_data="game_action:hilo_started:low")
            kb.adjust(2)
            if "started" in game_type:
                kb.button(text="🏁 Завершить" if language == "ru" else "🏁 End Game",
                          callback_data="game_action:hilo:surrender")
            kb.adjust(2, 1)
        elif game_type.startswith("mines"):
            opened = set()
            field = {}
            if game_session and 'state' in game_session:
                state = game_session['state']
                opened = state.get('opened', set())
                field = state.get('field', {})
            for row in range(5):
                for col in range(5):
                    cell_num = row * 5 + col
                    if cell_num in opened:
                        coefficient = field.get(cell_num, 0.0)
                        if coefficient == 0.0:
                            cell_text = "💣"
                        else:
                            cell_text = f"{coefficient:.2f}x"
                        kb.button(text=cell_text, callback_data=f"game_action:mines_started:opened_{cell_num}")
                    else:
                        kb.button(text="⬜", callback_data=f"game_action:mines_started:{cell_num}")
            if "started" in game_type:
                kb.button(text="💰 Забрать" if language == "ru" else "💰 Cash Out",
                          callback_data="game_action:mines:cashout")
            kb.adjust(5, 5, 5, 5, 5, 1)
        elif game_type == "crash":
            kb.button(text="💰 Забрать" if language == "ru" else "💰 Cash Out",
                      callback_data="game_action:crash:cashout")
            kb.adjust(1, 1)
        if game_type.startswith("blackjack"):
            kb.button(text="🎴 Hit" if language == "en" else "🎴 Ещё",
                      callback_data="game_action:blackjack:hit")
            kb.button(text="🛑 Stand" if language == "en" else "🛑 Стоп",
                      callback_data="game_action:blackjack:stand")
            kb.adjust(2)
        return kb.as_markup()

    @staticmethod
    def build_deposit_amount(currency: str, language_code: str) -> InlineKeyboardMarkup:
        from bot_app.payments import CryptoPay
        kb = InlineKeyboardBuilder()
        usd_amounts = [0.1, 0.25, 0.5, 1, 2, 5, 10, 50, 100, 200, 500]
        if currency == "JET":
            rate = 1
        else:
            rate = CryptoPay.get_crypto_rate(currency)
        if rate is None:
            kb.button(text=Messages.get_text("OTHERS", "cancel", language_code),
                      callback_data="back")
            kb.adjust(1)
            return False, kb.as_markup()
        amounts = []
        for usd_amount in usd_amounts:
            converted = usd_amount / rate
            amounts.append((converted, usd_amount))
        for amount, usd_amount in amounts:
            if isinstance(amount, float) and amount < 1:
                crypto_display = f"{amount:.8f}".rstrip('0').rstrip('.')
            elif isinstance(amount, float):
                crypto_display = f"{amount:.2f}".rstrip('0').rstrip('.')
            else:
                crypto_display = str(amount)
            display_text = f"{crypto_display} [{usd_amount}$]"
            kb.button(
                text=display_text,
                callback_data=f"do-deposit:{currency}:{amount}"
            )
        kb.button(
            text=Messages.get_text("OTHERS", "cancel", language_code),
            callback_data="back"
        )
        return kb

    @staticmethod
    def build_withdraw_amount(currency: str, language_code: str, balance: str) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        percentages = [25, 50, 75, 100]
        for percentage in percentages:
            withdraw_amount = (float(balance) * percentage) / 100
            button_text = f"{percentage}% [{withdraw_amount:.2f}$]"
            kb.button(
                text=button_text,
                callback_data=f"do-withdraw:{currency}:{withdraw_amount}"
            )
        kb.button(
            text=Messages.get_text("OTHERS", "cancel", language_code),
            callback_data="back"
        )
        kb.adjust(2, 2, 1)
        return kb

    @staticmethod
    def get_amount_keyboard(language_code: str, currency: str,
                            operation_type: str, balance: str) -> tuple[bool, InlineKeyboardMarkup]:
        if operation_type == "deposit":
            kb = KeyboardManager.build_deposit_amount(currency, language_code)
        else:
            kb = KeyboardManager.build_withdraw_amount(currency, language_code, balance)
        kb.adjust(2)
        return True, kb.as_markup()

    @staticmethod
    def get_pay_keyboard(language_code: str, deposit: dict[str, Any], transaction_id: str) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.button(text=Messages.get_text("BALANCE", "pay", language_code), url=deposit['payment_url'])

        # TODO: удалить после реализации вебхуков
        kb.button(text=Messages.get_text("BALANCE", "check", language_code),
                  callback_data=f"check-deposit:{transaction_id}")

        kb.button(text=Messages.get_text("BALANCE", "cancel_payment", language_code),
                  callback_data=f"cancel-deposit:{transaction_id}")
        kb.adjust(1)
        return kb.as_markup()

    @staticmethod
    def get_confirm_keyboard(callback_data: str, language_code: str) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.button(text=Messages.get_text("OTHERS", "confirm_yes", language_code),
                  callback_data=f"{callback_data}:yes")
        kb.button(text=Messages.get_text("OTHERS", "confirm_no", language_code),
                  callback_data=f"{callback_data}:no")
        kb.adjust(2)
        return kb.as_markup()

    @staticmethod
    def get_admin_keyboard(language_code: str) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.button(text=Messages.get_text("ADMIN", "summary", language_code),
                  callback_data="admin-summary")
        kb.button(text=Messages.get_text("ADMIN", "players", language_code),
                  callback_data="admin-list-players")
        kb.button(text=Messages.get_text("ADMIN", "logs", language_code),
                  callback_data="admin-show-logs")
        kb.button(text=Messages.get_text("ADMIN", "database", language_code),
                  callback_data="admin-show-tables")
        kb.button(text=Messages.get_text("ADMIN", "issue_balance", language_code),
                  callback_data="admin-issue-balance")
        kb.button(text=Messages.get_text("ADMIN", "reset_balance", language_code),
                  callback_data="admin-reset-balance")
        kb.button(text=Messages.get_text("ADMIN", "get_balance", language_code),
                  callback_data="admin-get-balance")
        kb.button(text=Messages.get_text("ADMIN", "game_settings", language_code),
                  callback_data="admin-game-settings")
        kb.button(text=Messages.get_text("ADMIN", "game_config", language_code),
                  callback_data="admin-game-config")
        kb.button(text=Messages.get_text("ADMIN", "bot_config", language_code),
                  callback_data="admin-bot-config")
        kb.button(text=Messages.get_text("ADMIN", "max_bet", language_code),
                  callback_data="update-max-bet")
        kb.button(text=Messages.get_text("ADMIN", "message_channel", language_code),
                  callback_data="channel-message")
        kb.button(text=Messages.get_text("OTHERS", "back", language_code),
                  callback_data="back")
        kb.adjust(2)
        return kb.as_markup()

    @staticmethod
    def get_news_keyboard(language_code: str) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.button(text=Messages.get_text("ADMIN", "startup_channel", language_code),
                  callback_data="channel-message:startup")
        kb.button(text=Messages.get_text("ADMIN", "custom_message", language_code),
                  callback_data="channel-message:custom")
        kb.button(text=Messages.get_text("OTHERS", "back", language_code),
                  callback_data="back")
        kb.adjust(2)
        return kb.as_markup()

    @staticmethod
    def get_custom_message_cancel(language_code: str) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.button(text=Messages.get_text("OTHERS", "cancel", language_code),
                  callback_data="custom-message-cancel")
        kb.adjust(1)
        return kb.as_markup()

    @staticmethod
    def build_keyboard_from_text(text: str) -> InlineKeyboardBuilder:
        kb = InlineKeyboardBuilder()
        if text == "[NONE]":
            return kb
        lines = text.strip().split('\n')
        try:
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if '|' not in line:
                    return kb
                parts = line.split('|', 1)
                if len(parts) != 2:
                    return kb
                button_text = parts[0].strip()
                button_url = parts[1].strip()
                if not button_text or not button_url:
                    return kb
                if not (button_url.startswith('http://') or
                        button_url.startswith('https://') or
                        button_url.startswith('tg://')):
                    return kb
                kb.button(text=button_text, url=button_url)
            if not kb.buttons:
                return kb
            return kb
        except Exception:
            return kb

    @staticmethod
    def get_markup_from_text(language_code: str, text: str) -> InlineKeyboardMarkup:
        kb = KeyboardManager.build_keyboard_from_text(text)
        kb.button(text=Messages.get_text("OTHERS", "cancel", language_code),
                  callback_data="custom-message-cancel")
        kb.button(text=Messages.get_text("ADMIN", "message_channel", language_code),
                  callback_data="custom-message-send")
        kb.adjust(1)
        return kb.as_markup()

    @staticmethod
    def remove_control_buttons(message: Message) -> InlineKeyboardMarkup:
        """
        Извлекает клавиатуру из сообщения и удаляет кнопки управления
        """
        if not message.reply_markup:
            return None
        current_markup = message.reply_markup
        new_keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        for row in current_markup.inline_keyboard:
            new_row = []
            for button in row:
                if button.callback_data not in ["custom-message-cancel", "custom-message-send"]:
                    new_row.append(button)
            if new_row:
                new_keyboard.inline_keyboard.append(new_row)
        return new_keyboard

    @staticmethod
    def get_logs_keyboard(language_code: str, page: int = 1, add_next_page: bool = True) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        if page > 1:
            kb.button(text=Messages.get_text("OTHERS", "prev_page", language_code),
                      callback_data=f"admin-show-logs:{page - 1}")
        kb.button(text=Messages.get_text("OTHERS", "back", language_code),
                  callback_data="admin-panel")
        if add_next_page:
            kb.button(text=Messages.get_text("OTHERS", "next_page", language_code),
                      callback_data=f"admin-show-logs:{page + 1}")
        kb.adjust(3)
        return kb.as_markup()

    @staticmethod
    def get_users_keyboard(language_code: str, lines: list, page: int = 1,
                           add_next_page: bool = True) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        for line in lines:
            kb.row(InlineKeyboardButton(text=line, callback_data=f"admin-user:{line}"))
        nav_buttons = []
        if page > 1:
            nav_buttons.append(InlineKeyboardButton(text="◀️", callback_data=f"admin-list-players:{page - 1}"))
        nav_buttons.append(InlineKeyboardButton(
            text=Messages.get_text("OTHERS", "back", language_code),
            callback_data="admin-panel"))
        if add_next_page:
            nav_buttons.append(InlineKeyboardButton(text="▶️", callback_data=f"admin-list-players:{page + 1}"))
        kb.row(*nav_buttons)
        return kb.as_markup()

    @staticmethod
    def get_tables_keyboard(tables: List[str], language_code: str) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        for table in tables:
            kb.button(text=table, callback_data=f"admin-tables:{table}")
        kb.button(text=Messages.get_text("OTHERS", "back", language_code),
                  callback_data="admin-panel")
        kb.adjust(1)
        return kb.as_markup()

    @staticmethod
    def get_games_keyboard(command: str, games: Dict[str, Type[BaseGame]], language_code: str) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        for game_id, game_class in games.items():
            game_instance = game_class(50)
            kb.button(
                text=f"{game_instance.icon} {game_instance.name(language_code)}",
                callback_data=f"{command}:{game_id}")
        kb.button(text=Messages.get_text("OTHERS", "back", language_code),
                  callback_data="admin-panel")
        kb.adjust(2)
        return kb.as_markup()

    @staticmethod
    def get_game_configs_keyboard(game_id: int, configs: list[str], language_code: str) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        for config in configs:
            kb.button(
                text=config,
                callback_data=f"admin-game-settings:{game_id}:{config}")
        kb.button(text=Messages.get_text("OTHERS", "back", language_code),
                  callback_data="admin-panel")
        kb.adjust(2)
        return kb.as_markup()

    @staticmethod
    def get_bot_config(language_code: str) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.button(text=Messages.get_text("ADMIN", "set_bot_channel_config", language_code),
                  callback_data="admin-bot-config:set_channel")
        kb.button(text=Messages.get_text("ADMIN", "set_bot_news_channel_config", language_code),
                  callback_data="admin-bot-config:set_news")
        kb.button(text=Messages.get_text("ADMIN", "remove_bot_config", language_code),
                  callback_data="admin-bot-config:remove")
        kb.button(text=Messages.get_text("OTHERS", "back", language_code),
                  callback_data="admin-panel")
        kb.adjust(2)
        return kb.as_markup()

    @staticmethod
    def get_bet_parameter_keyboard(parameter: BetParameter, language: str, bet_type: str,
                                   selected_values: list = None, need_select=False) -> InlineKeyboardMarkup:
        """Создать клавиатуру для выбора параметра с поддержкой multi-select"""
        if selected_values is None:
            selected_values = []
        kb = InlineKeyboardBuilder()
        options = parameter.options
        values = options.get('values', [])
        adjust = 2
        for item in values:
            display_text = item.get(language, item.get('en', ''))
            emoji = item.get('emoji', '')
            value = item.get('value', '')
            if parameter.validation_func is not None:
                try:
                    is_valid = parameter.validation_func(item, bet_type)
                    if not is_valid:
                        continue
                except Exception:
                    continue
            adjust = int(item.get('adjust', 2))
            if isinstance(value, list):
                for num in value:
                    status_emoji = ""
                    if need_select:
                        is_selected = str(num) in selected_values
                        status_emoji = "✅ " if is_selected else "⬜ "
                    kb.button(
                        text=f"{status_emoji}{num}",
                        callback_data=f"select-bet-data:{parameter.param_type}:{num}"
                    )
            else:
                if parameter.multi_select:
                    is_selected = value in selected_values
                    status_emoji = "✅" if is_selected else "⬜"
                    display_text = f"{status_emoji} {emoji} {display_text}".strip()
                else:
                    display_text = f"{emoji} {display_text}".strip()
                kb.button(
                    text=display_text,
                    callback_data=f"select-bet-data:{parameter.param_type}:{value}"
                )
        if parameter.multi_select:
            kb.button(
                text="✅ Готово" if language == 'ru' else "✅ Done",
                callback_data=f"finalize-bet-data:{parameter.param_type}"
            )
        kb.button(
            text=Messages.get_text("OTHERS", "back", language),
            callback_data="back"
        )
        kb.adjust(adjust)
        return kb.as_markup()

    @staticmethod
    def get_bet_data_keyboard(bet_data_type: str, options: dict, language: str):
        """Получить клавиатуру для выбора bet_data"""
        keyboards = {
            # 'lines': KeyboardManager._get_lines_keyboard
        }
        if bet_data_type not in keyboards:
            return None
        return keyboards[bet_data_type](options, language)

    @staticmethod
    def get_bet_keyboard(game: BaseGame, balance: float, language_code: str) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        max_bet = min(game.max_bet, balance)
        min_bet = 0.01
        bet_values = []
        if max_bet <= 10:
            n_points = 12
            step = (max_bet - min_bet) / (n_points - 1) if max_bet > min_bet else 0
            bet_values = [round(min_bet + i * step, 2) for i in range(n_points)]
            bet_values = [v for v in bet_values if v <= max_bet]
        else:
            import math
            log_min = math.log10(min_bet)
            log_max = math.log10(max_bet)
            step = (log_max - log_min) / 18
            for i in range(19):
                log_val = log_min + step * i
                val = 10 ** log_val
                if val < 1:
                    bet_values.append(round(val, 2))
                elif val < 100:
                    bet_values.append(round(val, 1))
                else:
                    bet_values.append(int(val))
            bet_values = sorted(set(bet_values))
        if min_bet <= balance <= max_bet and round(balance, 2) not in bet_values:
            bet_values.append(round(balance, 2))
        bet_values = sorted(set(bet_values))
        for bet in bet_values:
            text = f"{bet:.2f}".rstrip('0').rstrip('.') + '$'
            kb.button(text=text, callback_data=f"start-game:{bet}")
        kb.button(text=Messages.get_text("OTHERS", "back", language_code),
                  callback_data="back")
        kb.adjust(3)
        return kb.as_markup()

    @staticmethod
    def get_game_again_keyboard(language_code: str) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.button(text=Messages.get_text("OTHERS", "try_again", language_code),
                  callback_data="select-bet")
        kb.button(text=Messages.get_text("OTHERS", "back", language_code),
                  callback_data="back")
        kb.adjust(2)
        return kb.as_markup()

    @staticmethod
    def get_channel_announcement_keyboard(bot_username: str) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.button(text=Messages.get_text("OTHERS", "did_deb", "en"),
                  url=f"https://t.me/{bot_username}?start=deb")
        kb.adjust(1)
        return kb.as_markup()

    @staticmethod
    async def get_bot_open_keyboard(bot) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        bot_username = (await bot.get_me()).username
        kb.button(text=Messages.get_text("OTHERS", "bot_open", "en"),
                  url=f"https://t.me/{bot_username}?start=start")
        kb.adjust(1)
        return kb.as_markup()

    @staticmethod
    def get_referral_keyboard(language_code: str) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.button(text=Messages.get_text("REFERRAL", "create", language_code),
                  callback_data="referral-create")
        kb.button(text=Messages.get_text("REFERRAL", "stats", language_code),
                  callback_data="referral-stats")
        kb.button(text=Messages.get_text("OTHERS", "back", language_code),
                  callback_data="back")
        kb.adjust(1)
        return kb.as_markup()

    @staticmethod
    def get_channel_startup_keyboard(bot_username: str, support_bot_username: str):
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=Messages.get_text("OTHERS", "bot_open", "en"),
                        url=f"https://t.me/{bot_username}?start=start"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="📞 Техподдержка / Support",
                        url=f"https://t.me/{support_bot_username}?start=start"
                    )
                ]
            ]
        )

    @staticmethod
    def get_referral_cancel_keyboard(language_code: str) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.button(text=Messages.get_text("OTHERS", "cancel", language_code),
                  callback_data="referral-cancel")
        kb.adjust(1)
        return kb.as_markup()

    @staticmethod
    def get_channel_keyboard(channel_username) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.button(text="📢 Подписаться", url=f"https://t.me/{channel_username}")
        kb.button(text="✅ Проверить подписку", callback_data="check-subscription")
        kb.adjust(1)
        return kb.as_markup()
