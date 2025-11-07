from typing import List, Any
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class Messages:
    TEXT = {
        "MAIN_MENU": {
            "games": {"ru": "Начать игру", "en": "Start Game"},
            "profile": {"ru": "Профиль", "en": "Profile"},
            "settings": {"ru": "Настройки", "en": "Settings"},
            "balance": {"ru": "Баланс", "en": "Balance"},
            "rules": {"ru": "Правила игры", "en": "Rules"},
            "help": {"ru": "Поддержка", "en": "Help"},
            "referral": {"ru": "Рефералка", "en": "Referral"},
            "admin": {"ru": "Админ-панель", "en": "Admin Panel"},
        },
        "SETTINGS": {
            "game": {"ru": "Сменить игру", "en": "Change Game"},
            "language": {"ru": "Сменить язык", "en": "Change Language"},
            "email": {"ru": "Сменить почту", "en": "Change Email"}
        },
        "BALANCE": {
            "deposit": {"ru": "Пополнить баланс", "en": "Deposit"},
            "withdraw": {"ru": "Вывести средства", "en": "Withdraw"}
        },
        "ADMIN": {
            "summary": {"ru": "Сводка по балансу", "en": "Balance Summary"},
            "players": {"ru": "Список игроков", "en": "Player List"},
            "logs": {"ru": "Логи событий", "en": "Event Logs"},
            "database": {"ru": "Показать БД", "en": "Show Database"}
        },
        "REFERRAL": {
            "create": {"ru": "Создать рефералку", "en": "Create Referral"},
            "stats": {"ru": "Статистика рефералки", "en": "Referral Stats"}
        },
        "OTHERS": {
            "cancel": {"ru": "Отмена", "en": "Cancel"},
            "back": {"ru": "Назад", "en": "Back"}
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
            "withdraw": "💸"
        },
        "ADMIN": {
            "summary": "📊",
            "players": "👥",
            "logs": "🗒️",
            "database": "🗄️"
        },
        "REFERRAL": {
            "create": "➕",
            "stats": "👥"
        },
        "OTHERS": {
            "cancel": "❌",
            "back": "◀️"
        }
    }

    @staticmethod
    def get_text(tag, button, language):
        return f"{Messages.ICONS[tag][button]} {Messages.TEXT[tag][button][language]}"


class KeyboardManager:
    @staticmethod
    def get_back_keyboard(language_code, callback_data: str = "back") -> InlineKeyboardMarkup:
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
    def get_main_keyboard(game_icon: str, admin: bool, language_code: str) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.button(text=f"{game_icon}{Messages.get_text('MAIN_MENU', 'games', language_code)}",
                  callback_data="games-start")
        kb.button(text=Messages.get_text("MAIN_MENU", "profile", language_code),
                  callback_data="profile")
        kb.button(text=Messages.get_text("MAIN_MENU", "settings", language_code),
                  callback_data="settings")
        kb.button(text=Messages.get_text("MAIN_MENU", "balance", language_code),
                  callback_data="balance")
        kb.button(text=Messages.get_text("MAIN_MENU", "rules", language_code),
                  callback_data="rules")
        kb.button(text=Messages.get_text("MAIN_MENU", "help", language_code), url="https://t.me/plaza_support_BOT")
        kb.button(text=Messages.get_text("MAIN_MENU", "referral", language_code), callback_data="referral-menu")
        if admin:
            kb.button(text=Messages.get_text("MAIN_MENU", "admin", language_code),
                      callback_data="admin-panel")
        kb.adjust(2, 2, 2, 1, 1)
        return kb.as_markup()

    @staticmethod
    def get_register_cancel_keyboard(language_code: str) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.button(text=Messages.get_text("OTHERS", "cancel", language_code),
                  callback_data="register_cancel")
        kb.adjust(1)
        return kb.as_markup()

    @staticmethod
    def get_settings_keyboard(language_code: str) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.button(text=Messages.get_text("SETTINGS", "game", language_code),
                  callback_data="change-game")
        kb.button(text=Messages.get_text("SETTINGS", "language", language_code),
                  callback_data="change-language")
        kb.button(text=Messages.get_text("SETTINGS", "email", language_code),
                  callback_data="change-email")
        kb.button(text=Messages.get_text("OTHERS", "back", language_code),
                  callback_data="back")
        kb.adjust(1)
        return kb.as_markup()

    @staticmethod
    def get_change_game_keyboard(games: List[Any], language_code: str) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        for i, game in enumerate(games):
            kb.button(text=f"{game.icon} {game.name(language_code)}", callback_data=f"set-game:{i}")
        kb.adjust(1)
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
    def get_currency_type_keyboard(language_code: str, operation_type: str) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.button(text="Crypt", callback_data=f"balance-crypt:{operation_type}")
        kb.button(text="Fiat", callback_data=f"balance-fiat:{operation_type}")
        kb.button(text=Messages.get_text("OTHERS", "cancel", language_code),
                  callback_data="back")
        kb.adjust(2, 1)
        return kb.as_markup()

    @staticmethod
    def get_currency_keyboard(language_code: str, currency_list: tuple,
                              operation_type: str, size: int = 2) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        for currency_code in currency_list:
            kb.button(text=currency_code, callback_data=f"{operation_type}-select-currency:{currency_code}")
        kb.button(text=Messages.get_text("OTHERS", "cancel", language_code),
                  callback_data="back")
        kb.adjust(size)
        return kb.as_markup()

    @staticmethod
    def get_amount_keyboard(language_code: str, currency: str,
                            operation_type: str, rates: float) -> InlineKeyboardMarkup:
        usd_amounts = [0.1, 0.25, 0.5, 1, 2, 5, 10, 50, 100, 200, 500]
        if currency in rates:
            rate = crypto_rates[currency]
        amounts = []
        for usd_amount in usd_amounts:
            converted = usd_amount / rate
            if currency in ["BTC", "ETH", "TON"]:
                converted = round(converted, 8)
            elif currency in fiat_rates:
                converted = round(converted, 2) if rate > 0.01 else int(converted)
            else:
                converted = round(converted, 6)
            amounts.append(converted)
        kb = InlineKeyboardBuilder()

        for amount in amounts:
            if isinstance(amount, float) and amount < 1:
                display_text = f"{amount:.8f}".rstrip('0').rstrip('.')
            elif isinstance(amount, float):
                display_text = f"{amount:.2f}".rstrip('0').rstrip('.')
            else:
                display_text = str(amount)
            kb.button(
                text=f"{display_text}",
                callback_data=f"do-{operation_type}:{currency}:{amount}"
            )
        kb.button(
            text=Messages.get_text("OTHERS", "cancel", language_code),
            callback_data="back"
        )
        kb.adjust(3)
        return kb.as_markup()

    @staticmethod
    def get_pay_keyboard(deposit: dict[str, Any]):
        kb = InlineKeyboardBuilder()
        kb.button(text='Оплатить', url=deposit['payment_url'])
        kb.button(text="Отменить платёж", callback_data=f"cancel-deposit:{deposit['internal_tx_id']}")
        kb.adjust(1)
        return kb.as_markup()

    @staticmethod
    def get_admin_keyboard(language_code) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.button(text=Messages.get_text("ADMIN", "summary", language_code),
                  callback_data="admin-summary")
        kb.button(text=Messages.get_text("ADMIN", "players", language_code),
                  callback_data="admin-list-players")
        kb.button(text=Messages.get_text("ADMIN", "logs", language_code),
                  callback_data="admin-show-logs")
        kb.button(text=Messages.get_text("ADMIN", "database", language_code),
                  callback_data="admin-show-tables")
        kb.button(text=Messages.get_text("OTHERS", "back", language_code),
                  callback_data="back")
        kb.adjust(1)
        return kb.as_markup()

    @staticmethod
    def get_logs_keyboard(language_code, page: int = 1, add_next_page: bool = True) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        if page > 1:
            kb.button(text="◀️", callback_data=f"admin-show-logs:{page - 1}")
        kb.button(text=Messages.get_text("OTHERS", "back", language_code),
                  callback_data="admin-panel")
        if add_next_page:
            kb.button(text="▶️", callback_data=f"admin-show-logs:{page + 1}")
        kb.adjust(3)
        return kb.as_markup()

    @staticmethod
    def get_users_keyboard(language_code, lines: list, page: int = 1,
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
    def get_tables_keyboard(tables: List[str], language_code) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        for table in tables:
            kb.button(text=table, callback_data=f"admin-tables:{table}")
        kb.button(text=Messages.get_text("OTHERS", "back", language_code),
                  callback_data="admin-panel")
        kb.adjust(1)
        return kb.as_markup()

    @staticmethod
    def get_referral_keyboard(language_code) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.button(text=Messages.get_text("REFERRAL", "create", language_code), callback_data="referral-create")
        kb.button(text=Messages.get_text("REFERRAL", "stats", language_code), callback_data="referral-stats")
        kb.button(text=Messages.get_text("OTHERS", "back", language_code),
                  callback_data="back")
        kb.adjust(1)
        return kb.as_markup()

    @staticmethod
    def get_referral_cancel_keyboard(language_code) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.button(text=Messages.get_text("OTHERS", "cancel", language_code),
                  callback_data="referral-cancel")
        kb.adjust(1)
        return kb.as_markup()
