class Messages:
    REGISTRATION = {
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
        }
    }
    MAIN_MENU = {
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
        }
    }
    USERINFO = {
        "NO_EMAIL": {
            "ru": "Почта не указана",
            "en": "Email not specified"
        },
        "USERINFO": {
            "ru": (
                "👤 Профиль пользователя\n"
                "Имя: username\n"
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
                "Имя: username\n"
                "Хэш имени: {hashed_username}\n"
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
                "Hashed username: {hashed_username}\n"
                "Balance: {balance}₽\n"
                "Winnings: {winnings}₽\n"
                "Email: {email} ({email_verified})\n"
                "Selected game: {selected_game}\n"
                "Interface language: {language}\n"
                "Registration date: {registered_at}"
            )
        },
        "USERINFO_NO_GAMES": {
            "ru": "Данных об играх пока нет.",
            "en": "There is no data on games yet."
        },
        "USERINFO_FOFAVORITE_GAME": {
            "ru": "Любимая игра: favorite_game_name, [favorite_play_times]",
            "en": "Favorite game: favorite_game_name, [favorite_play_times]"
        },
        "USERINFO_GAMES_LIST": {
            "ru": "game_name, [count]",
            "en": "game_name, [count]"
        },
        "USERINFO_GAMES_LIST_TITLE": {
            "ru": "Всего игр",
            "en": "Total games"
        }
    }
    BALANCE = {
        "BALANCE": {
            "ru": "💰 Ваш баланс: {balance} руб",
            "en": "💰 Your balance: {balance} rub"
        }
    }
    REFERRAL_MESSAGES = {
        "REFERRAL_MENU": {
            "ru": (
                "💰 <b>Реферальная программа</b>\n\n"
                "Приглашай друзей через свой личный бот-клон и получай награды!\n\n"
                "📊 <b>Как это работает:</b>\n"
                "1️⃣ Ты создаёшь своего уникального бота в @BotFather\n"
                "2️⃣ Отправляешь токен этому боту\n"
                "3️⃣ Получаешь личную реф-ссылку\n"
                "4️⃣ Делишься ссылкой с друзьями\n"
                "5️⃣ Получаешь награду за каждого нового пользователя\n\n"
                "<i>Каждый ваш бот-клон работает полностью автономно</i>"
            ),
            "en": (
                "💰 <b>Referral Program</b>\n\n"
                "Invite friends through your personal bot clone and get rewards!\n\n"
                "📊 <b>How it works:</b>\n"
                "1️⃣ You create your unique bot in @BotFather\n"
                "2️⃣ Send the token to this bot\n"
                "3️⃣ Get your personal referral link\n"
                "4️⃣ Share the link with friends\n"
                "5️⃣ Get rewards for each new user\n\n"
                "<i>Each of your bot clones works completely autonomously</i>"
            )
        },
        "REFERRAL_CLONE_BOT_STEP1": {
            "ru": (
                "🤖 <b>Создание бота-клона</b>\n\n"
                "Сейчас я помогу тебе создать персональный бот. Выполни следующие шаги:\n\n"
                "<b>Шаг 1:</b> Перейди в @BotFather\n"
                "<b>Шаг 2:</b> Отправь команду <code>/newbot</code>\n"
                "<b>Шаг 3:</b> Дай боту название (например, \"Casino_Username\")\n"
                "<b>Шаг 4:</b> Дай боту username (должен заканчиваться на \"_bot\")\n"
                "<b>Шаг 5:</b> BotFather пришлёт тебе токен\n"
                "<b>Шаг 6:</b> Скопируй токен и отправь его сюда\n\n"
                "⚠️ <i>Не делись токеном ни с кем!</i>"
            ),
            "en": (
                "🤖 <b>Creating a bot clone</b>\n\n"
                "Now I'll help you create a personal bot. Follow these steps:\n\n"
                "<b>Step 1:</b> Go to @BotFather\n"
                "<b>Step 2:</b> Send the command <code>/newbot</code>\n"
                "<b>Step 3:</b> Give your bot a name (for example, \"Casino_Username\")\n"
                "<b>Step 4:</b> Give your bot a username (must end with \"_bot\")\n"
                "<b>Step 5:</b> BotFather will send you a token\n"
                "<b>Step 6:</b> Copy the token and send it here\n\n"
                "⚠️ <i>Don't share the token with anyone!</i>"
            )
        },
        "REFERRAL_CLONE_BOT_STEP2": {
            "ru": "⏳ Проверяю токен...",
            "en": "⏳ Checking token..."
        },
        "REFERRAL_CLONE_BOT_SUCCESS": {
            "ru": (
                "✅ <b>Бот создан успешно!</b>\n\n"
                "🤖 Имя бота: {bot_name}\n"
                "Каждый новый пользователь твоего бота будет считаться твоим рефералом.\n"
                "За каждого реферала ты получаешь:\n"
                "💰 5% от каждой ставки\n"
                "💎 10% от каждого депозита\n"
                "🏆 2% от каждого выигрыша\n\n"
                "<i>Твой бот работает 24/7 и привлекает рефералов автоматически</i>"
            ),
            "en": (
                "✅ <b>Bot created successfully!</b>\n\n"
                "🤖 Bot name: {bot_name}\n"
                "Every new user who follows your link will be counted as your referral.\n"
                "For each referral you get:\n"
                "💰 5% from each bet\n"
                "💎 10% from each deposit\n"
                "🏆 2% from each win\n\n"
                "<i>Your bot works 24/7 and attracts referrals automatically</i>"
            )
        },
        "REFERRAL_INVALID_TOKEN": {
            "ru": "❌ <b>Невалидный токен</b>\n\n🔄 Попробуй ещё раз. Убедись, что:\n• Токен скопирован полностью\n• Токен содержит двоеточие\n• Бот имеет username",
            "en": "❌ <b>Invalid token</b>\n\n🔄 Try again. Make sure:\n• Token is copied completely\n• Token contains a colon\n• Bot has a username"
        },
        "REFERRAL_BOT_CREATION_ERROR": {
            "ru": "❌ <b>Ошибка создания бота</b>\n\nВозможно, этот токен уже использован или произошла ошибка на сервере.",
            "en": "❌ <b>Error creating bot</b>\n\nPossibly, this token is already used or server error occurred."
        },
        "REFERRAL_MY_REFERRALS": {
            "ru": (
                "👥 <b>Твои рефералы</b>\n\n"
                "📊 <b>Статистика:</b>\n"
                "👤 Всего рефералов: <code>{total_referrals}</code>\n"
                "✅ Активных: <code>{active_referrals}</code>\n"
                "💰 Получено наград: <code>{total_rewards} ⚡</code>\n\n"
                "📈 <b>Топ боты:</b>\n"
                "{top_bots}\n\n"
                "<i>Обновлено: только что</i>"
            ),
            "en": (
                "👥 <b>Your Referrals</b>\n\n"
                "📊 <b>Statistics:</b>\n"
                "👤 Total referrals: <code>{total_referrals}</code>\n"
                "✅ Active: <code>{active_referrals}</code>\n"
                "💰 Rewards earned: <code>{total_rewards} ⚡</code>\n\n"
                "📈 <b>Top bots:</b>\n"
                "{top_bots}\n\n"
                "<i>Updated: just now</i>"
            )
        },
        "REFERRAL_MY_BOTS": {
            "ru": (
                "🤖 <b>Твои боты-клоны</b>\n\n"
                "<b>Активные боты: {active_count}</b>\n\n"
                "{bots_list}\n\n"
                "💡 <i>Совет: Создай несколько ботов для разных ниш друзей!</i>"
            ),
            "en": (
                "🤖 <b>Your Bot Clones</b>\n\n"
                "<b>Active bots: {active_count}</b>\n\n"
                "{bots_list}\n\n"
                "💡 <i>Tip: Create multiple bots for different groups of friends!</i>"
            )
        },
        "REFERRAL_BOT_DISABLED": {
            "ru": "⚠️ Этот бот был отключен. Ты всё ещё получаешь награды, но новые пользователи не могут присоединиться.",
            "en": "⚠️ This bot has been disabled. You still receive rewards, but new users cannot join."
        },
        "REFERRAL_REWARD_NOTIFICATION": {
            "ru": (
                "🎉 <b>Новый реферал!</b>\n\n"
                "👤 Пользователь присоединился через бота <code>{bot_name}</code>\n"
                "💰 Ты получил: <code>+100 ⚡</code>\n\n"
                "Баланс: {new_balance} ⚡"
            ),
            "en": (
                "🎉 <b>New Referral!</b>\n\n"
                "👤 A user joined through your <code>{bot_name}</code> bot\n"
                "💰 You received: <code>+100 ⚡</code>\n\n"
                "Balance: {new_balance} ⚡"
            )
        },
        "REFERRAL_COPY_LINK": {
            "ru": (
                "🔗 <b>Твоя реф-ссылка скопирована!</b>\n\n"
                "Можешь поделиться ей в:\n"
                "📱 WhatsApp\n"
                "📧 Email\n"
                "💬 Telegram группа\n"
                "🌍 Социальные сети\n\n"
                "<i>Количество переходов обновляется в реальном времени</i>"
            ),
            "en": (
                "🔗 <b>Your referral link copied!</b>\n\n"
                "You can share it in:\n"
                "📱 WhatsApp\n"
                "📧 Email\n"
                "💬 Telegram groups\n"
                "🌍 Social networks\n\n"
                "<i>Click count updates in real time</i>"
            )
        },
        "REFERRAL_STATS_BOT": {
            "ru": (
                "📊 <b>Статистика бота @{bot_name}</b>\n\n"
                "👥 Рефералов привлечено: <code>{referrals_count}</code>\n"
                "✅ Активных пользователей: <code>{active_count}</code>\n"
                "💰 Всего наград: <code>{total_reward} ⚡</code>\n"
                "📈 CTR: <code>{ctr}%</code>\n"
                "⏱️ Создан: <code>{created_date}</code>\n\n"
                "🔗 Ссылка: <code>{ref_link}</code>"
            ),
            "en": (
                "📊 <b>Bot @{bot_name} Statistics</b>\n\n"
                "👥 Referrals attracted: <code>{referrals_count}</code>\n"
                "✅ Active users: <code>{active_count}</code>\n"
                "💰 Total rewards: <code>{total_reward} ⚡</code>\n"
                "📈 CTR: <code>{ctr}%</code>\n"
                "⏱️ Created: <code>{created_date}</code>\n\n"
                "🔗 Link: <code>{ref_link}</code>"
            )
        },
        "REFERRAL_WAITING_TOKEN": {
            "ru": "Жду ввод токена бота...",
            "en": "Waiting for bot token..."
        },
        "REFERRAL_WELCOME": {
            "ru": (
                "👋 <b>Добро пожаловать!</b>\n\n"
                "Ты присоединился через реф-ссылку от пользователя.\n"
                "Спасибо за регистрацию! 🎁\n\n"
                "Начни играть и получай награды!"
            ),
            "en": (
                "👋 <b>Welcome!</b>\n\n"
                "You joined through a referral link.\n"
                "Thanks for registering! 🎁\n\n"
                "Start playing and earn rewards!"
            )
        }
    }
    ADMIN_PANEL = {
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
        }
    }

    TEXT = {
        # ═════════════════ Регистрация ═════════════════
        **REGISTRATION,

        # ═════════════════ Главное меню ════════════════
        **MAIN_MENU,

        # ═════════════════ Пользователь ════════════════
        **USERINFO,

        # ════════════════════ Баланс ═══════════════════
        **BALANCE,

        # ═══════════════════ Рефералка ═════════════════
        **REFERRAL_MESSAGES,

        # ═════════════════ Админ-панель ════════════════
        **ADMIN_PANEL
    }
