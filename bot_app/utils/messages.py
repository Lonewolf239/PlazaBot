class Messages:
    TEXT = {
        # ═════════════════ Регистрация ═════════════════
        "REGISTRATION": {
            "ru": "Регистрация!\nПожалуйста, введите ваш адрес электронной почты (мы будем отправлять вам чеки).",
            "en": "Registration!\nPlease enter your email address (we’ll send receipts there)."
        },
        "CHANGE_EMAIL": {
            "ru": "Изменение адреса электронной почты.\nПожалуйста, введите новый адрес электронной почты.",
            "en": "Change email address.\nPlease enter your new email address."
        },
        "REGISTRATION_ERROR_EMAIL": {
            "ru": "Ошибка: указанный адрес электронной почты некорректен. Пожалуйста, попробуйте еще раз.",
            "en": "Error: The entered email address is invalid. Please try again."
        },
        "REGISTRATION_ERROR_CODE": {
            "ru": "Ошибка: неверный код подтверждения. Попробуйте еще раз.",
            "en": "Error: Incorrect confirmation code. Please try again."
        },
        "REGISTRATION_STEP_TWO": {
            "ru": "Подтверждение! На указанную почту отправлен 6-значный код. Пожалуйста, введите его ниже:",
            "en": "Confirmation! A 6-digit code has been sent to your email. Please enter it below:"
        },
        "REGISTRATION_COMPLETED": {
            "ru": "Спасибо! Регистрация успешно завершена. Вы указали адрес: {email}.",
            "en": "Thank you! Registration is complete. You have specified the email: {email}."
        },

        # ═════════════════ Главное меню ════════════════
        "MAIN_MENU": {
            "ru": "Добро пожаловать в наше меню! Чем я могу помочь вам сегодня?",
            "en": "Welcome to our menu! How can I assist you today?"
        },
        "SETTINGS": {
            "ru": "Настройки.\nВыбранная игра: {selected_game}\nПочта: {email}",
            "en": "Settings.\nSelected game: {selected_game}\nEmail: {email}"
        },
        "CHANGE_LANGUAGE": {
            "ru": "Выберите язык. Пожалуйста, выберите предпочитаемый язык:",
            "en": "Select language. Please choose your preferred language:"
        },

        # ═════════════════ Пользователь ════════════════
        "USERINFO": {
            "ru": (
                "👤 Профиль пользователя\n"
                "Имя: {username}\n"
                "Баланс: {balance}₽\n"
                "Выигрыши: {winnings}₽\n"
                "Дата регистрации: {registered_at}"
            ),
            "en": (
                "👤 User Profile\n"
                "Username: {username}\n"
                "Balance: {balance}₽\n"
                "Winnings: {winnings}₽\n"
                "Registration date: {registered_at}"
            )
        },
        "USERINFO_ADMIN": {
            "ru": (
                "👤 Профиль пользователя\n"
                "ID: {user_id}\n"
                "Имя: {username}\n"
                "Баланс: {balance}₽\n"
                "Выигрыши: {winnings}₽\n"
                "Email: {email} ({email_verified})\n"
                "Выбранная игра: {selected_game}\n"
                "Язык интерфейса: {language}\n"
                "Дата регистрации: {registered_at}"
            ),
            "en": (
                "👤 User Profile\n"
                "ID: {user_id}\n"
                "Username: {username}\n"
                "Balance: {balance}₽\n"
                "Winnings: {winnings}₽\n"
                "Email: {email} ({email_verified})\n"
                "Selected game: {selected_game}\n"
                "Interface language: {language}\n"
                "Registration date: {registered_at}"
            )
        },

        # ════════════════════ Баланс ═══════════════════
        "BALANCE": {
            "ru": "💰 Ваш баланс: {balance} руб",
            "en": "💰 Your balance: {balance} rub"
        },

        # ═════════════════ Админ-панель ════════════════
        "ADMIN_PANEL": {
            "ru": "Админ-панель:",
            "en": "Admin panel:"
        },
        "ADMIN_SUMMARY_COUNT": {
            "ru": "Количество игроков",
            "en": "Number of players"
        },
        "ADMIN_SUMMARY_NEEDED": {
            "ru": "Сумма на счетах",
            "en": "Total balance"
        },
        "ADMIN_SUMMARY_AVG_BALANCE": {
            "ru": "Средний баланс",
            "en": "Average balance"
        },
        "ADMIN_SUMMARY_MAX_BALANCE": {
            "ru": "Максимум",
            "en": "Maximum"
        },
        "ADMIN_SUMMARY_MIN_BALANCE": {
            "ru": "Минимум",
            "en": "Minimum"
        },
    }
