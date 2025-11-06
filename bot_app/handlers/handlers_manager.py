from aiogram import types
from typing import Any

from bot_app.keyboards import KeyboardManager


class HandlersManager:
    # ════════════════ Регистрация ════════════════
    @staticmethod
    async def register_cancel(bot, chat_id: int):
        await bot.database_interface.update_user(chat_id,
                                                 input_type=0,
                                                 email_verified=True,
                                                 block_input=False)
        await bot.main_menu(chat_id)

    @staticmethod
    async def register_back(bot, callback_query: types.CallbackQuery):
        await bot.registration_menu(callback_query.message)

    @staticmethod
    async def games_start(bot, chat_id: int):
        await bot.database_interface.update_balance(chat_id, 100, 'deposit')
        await bot.database_interface.update_balance(chat_id, -100, 'bet')

    # ═════════════════ Настройки ═════════════════
    @staticmethod
    async def settings(bot, chat_id: int, user_data: dict[str, Any]):
        text = str(await bot.get_text(chat_id, "SETTINGS"))
        text = text.replace("semga05@mail.ru", await bot.get_text(chat_id, "NO_EMAIL"))
        await bot.send_message(chat_id, text,
                               reply_markup=KeyboardManager.get_settings_keyboard(user_data.get("language", "en")))

    @staticmethod
    async def change_language(bot, chat_id: int):
        await bot.send_message(chat_id, await bot.get_text(chat_id, "CHANGE_LANGUAGE"),
                               reply_markup=KeyboardManager.get_language_keyboard())

    @staticmethod
    async def change_game(bot, chat_id: int, user_data: dict[str, Any]):
        await bot.send_message(chat_id, await bot.get_text(chat_id, "CHANGE_GAME", user_data),
                               reply_markup=KeyboardManager.get_change_game_keyboard(
                                   bot.CasinoGames,
                                   user_data.get("language", "ru")))

    @staticmethod
    async def set_game(bot, chat_id: int, command: str):
        game_id = int(command[len("set-game:"):])
        await bot.database_interface.update_user(chat_id, selected_game=game_id)
        await bot.main_menu(chat_id)

    @staticmethod
    async def change_email(bot, callback_query: types.CallbackQuery):
        await bot.registration_menu(callback_query.message, first_message="CHANGE_EMAIL", ignore_db=True)

    @staticmethod
    async def language(bot, chat_id: int, command: str):
        language_code = command[len("language:"):]
        await bot.database_interface.update_user(chat_id, language=language_code)
        await bot.main_menu(chat_id)

    # ═══════════════════ Баланс ══════════════════
    @staticmethod
    async def balance(bot, chat_id: int, user_data: dict[str, Any]):
        await bot.send_message(chat_id, await bot.get_text(chat_id, "BALANCE"),
                               reply_markup=KeyboardManager.get_balance_keyboard(user_data.get("language", "en")))

    @staticmethod
    async def balance_deposit(bot, chat_id: int):
        providers = bot.payment_gateway.get_providers("deposit")
        text = "\n".join([p.get_provider_name() for p in providers])
        await bot.send_message(chat_id, text)
        deposit = await bot.payment_gateway.initiate_deposit(chat_id, 100, providers[0].get_provider_name(), "RUB")
        await bot.send_message(chat_id, deposit.get("payment_url"))

    @staticmethod
    async def balance_withdraw(bot, chat_id: int):
        providers = bot.payment_gateway.get_providers("withdraw")

    # ════════════════ Пользователь ═══════════════
    @staticmethod
    async def user(bot, chat_id: int, command: str):
        username = command[len("user:"):]
        user = await bot.database_interface.get_user_by_username(username)
        await bot.send_userinfo(chat_id, user, profile=True)
        await bot.main_menu(chat_id)

    # ════════════════ Админ-панель ═══════════════
    @staticmethod
    async def admin_panel(bot, chat_id: int, user_data: dict[str, Any]):
        if chat_id not in bot.admins_id:
            return
        await bot.send_message(chat_id, await bot.get_text(chat_id, "ADMIN_PANEL"),
                               reply_markup=KeyboardManager.get_admin_keyboard(user_data.get("language", "en")))

    @staticmethod
    async def admin_summary(bot, chat_id: int, user_data: dict[str, Any]):
        needed, count, avg_bal, max_bal, min_bal = await bot.database_interface.get_needed()
        text = (
            f"{await bot.get_text(chat_id, "ADMIN_SUMMARY_COUNT")}: {count}\n"
            f"{await bot.get_text(chat_id, "ADMIN_SUMMARY_NEEDED")}: {int(needed)} руб\n"
            f"{await bot.get_text(chat_id, "ADMIN_SUMMARY_AVG_BALANCE")}: {int(avg_bal)} руб\n"
            f"{await bot.get_text(chat_id, "ADMIN_SUMMARY_MAX_BALANCE")}: {max_bal}\n"
            f"{await bot.get_text(chat_id, "ADMIN_SUMMARY_MIN_BALANCE")}: {min_bal}"
        )
        await bot.send_message(chat_id, text,
                               reply_markup=KeyboardManager.get_back_keyboard(
                                   user_data.get("language", "en"),
                                   callback_data="admin-panel"))

    @staticmethod
    async def admin_list_players(bot, chat_id: int, command: str, user_data: dict[str, Any]):
        page = int(command.split(':')[1]) if ':' in command else 1
        text, lines, add_next_page = await bot.get_users_page(page)
        await bot.send_message(chat_id, text,
                               reply_markup=KeyboardManager.get_users_keyboard(
                                   user_data.get("language", "en"), lines, page, add_next_page))

    @staticmethod
    async def admin_show_logs(bot, chat_id: int, command: str, user_data: dict[str, Any]):
        page = int(command.split(':')[1]) if ':' in command else 1
        text, add_next_page = await bot.get_logs_page(page)
        await bot.send_message(chat_id, text,
                               reply_markup=KeyboardManager.get_logs_keyboard(
                                   user_data.get("language", "en"), page, add_next_page))

    @staticmethod
    async def admin_show_tables(bot, chat_id: int, language_code: str):
        ok, tables = await bot.database_interface.get_tables()
        if not ok:
            await bot.send_message(chat_id, tables[0],
                                   reply_markup=KeyboardManager.get_back_keyboard(
                                       language_code,
                                       callback_data="admin-panel"))
            return
        await bot.send_message(chat_id, "Таблицы:",
                               reply_markup=KeyboardManager.get_tables_keyboard(tables, language_code))

    @staticmethod
    async def admin_show_table(bot, chat_id: int, table: str, user_data: dict[str, Any]):
        bd = await bot.database_interface.display_table(table)
        for row in bd:
            await bot.send_message(chat_id, row)
        await HandlersManager.admin_panel(bot, chat_id, user_data)

    @staticmethod
    async def admin_user(bot, chat_id: int, command: str, user_data: dict[str, Any]):
        username = command[len("admin-user:"):]
        await bot.send_userinfo(chat_id, await bot.database_interface.get_user_by_username(username), True)
        await HandlersManager.admin_panel(bot, chat_id, user_data)

    @staticmethod
    async def rules(bot, chat_id: int, user_data: dict[str, Any]):
        await bot.send_message(chat_id,
                               bot.CasinoGames[user_data.get("selected_game", 0)].rules(
                                   user_data.get("language", "en")),
                               reply_markup=KeyboardManager.get_back_keyboard(user_data.get("language", "en")))
