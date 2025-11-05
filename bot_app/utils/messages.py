class Messages:
    REGISTRATION = {
        "REGISTRATION": {
            "ru": "📧 Регистрация\n\nПожалуйста, введите вашу электронную почту. На этот адрес мы будем отправлять квитанции о всех ваших операциях.",
            "en": "📧 Registration\n\nPlease enter your email address. We will send all receipts and transaction confirmations to this address."
        },
        "CHANGE_EMAIL": {
            "ru": "✏️ Изменение адреса электронной почты\n\nУкажите новый адрес электронной почты, на который мы будем отправлять ваши квитанции.",
            "en": "✏️ Change Email Address\n\nEnter your new email address where we will send your receipts."
        },
        "REGISTRATION_ERROR_EMAIL": {
            "ru": "❌ Ошибка\n\nАдрес электронной почты некорректен. Пожалуйста, проверьте формат и попробуйте снова.",
            "en": "❌ Error\n\nThe email address is invalid. Please check the format and try again."
        },
        "REGISTRATION_ERROR_CODE": {
            "ru": "❌ Ошибка подтверждения\n\nКод подтверждения неверен. Пожалуйста, проверьте код и попробуйте ещё раз.",
            "en": "❌ Verification Error\n\nThe confirmation code is incorrect. Please check the code and try again."
        },
        "REGISTRATION_STEP_TWO": {
            "ru": "✉️ Подтверждение почты\n\nМы отправили 6-значный код на указанный адрес. Пожалуйста, введите его ниже:",
            "en": "✉️ Email Verification\n\nWe've sent a 6-digit code to your email. Please enter it below:"
        },
        "REGISTRATION_COMPLETED": {
            "ru": "✅ Поздравляем!\n\nРегистрация успешно завершена. Ваш адрес электронной почты: {email}",
            "en": "✅ Congratulations!\n\nRegistration completed successfully. Your email address: {email}"
        }
    }

    MAIN_MENU = {
        "MAIN_MENU": {
            "ru": "👋 Добро пожаловать в наш бот!\n\nЧто вы хотели бы сделать? Выберите нужный раздел из меню ниже.",
            "en": "👋 Welcome!\n\nWhat would you like to do? Select the section you need from the menu below."
        },
        "SETTINGS": {
            "ru": "⚙️ Ваши настройки\n\nВыбранная игра: {selected_game}\n📧 Почта: {email}",
            "en": "⚙️ Your Settings\n\nSelected game: {selected_game}\n📧 Email: {email}"
        },
        "CHANGE_LANGUAGE": {
            "ru": "🌐 Выбор языка\n\nПожалуйста, выберите предпочитаемый язык интерфейса:",
            "en": "🌐 Language Selection\n\nPlease choose your preferred interface language:"
        }
    }

    USERINFO = {
        "NO_EMAIL": {
            "ru": "❌ Почта не указана",
            "en": "❌ Email not specified"
        },
        "PROFILE": {
            "ru": (
                "👤 Ваш профиль\n\n"
                "👤 Имя пользователя: username\n"
                "💰 Баланс: {balance}₽\n"
                "🏆 Выигрыши: {winnings}₽\n"
                "📅 Дата регистрации: {registered_at}"
            ),
            "en": (
                "👤 Your Profile\n\n"
                "👤 Username: username\n"
                "💰 Balance: {balance}₽\n"
                "🏆 Winnings: {winnings}₽\n"
                "📅 Registration date: {registered_at}"
            )
        },
        "USERINFO": {
            "ru": (
                "👤 Профиль пользователя\n\n"
                "👤 Имя: username\n"
                "💰 Баланс: {balance}₽\n"
                "🏆 Выигрыши: {winnings}₽\n"
                "📅 Регистрация: {registered_at}"
            ),
            "en": (
                "👤 User Profile\n\n"
                "👤 Username: username\n"
                "💰 Balance: {balance}₽\n"
                "🏆 Winnings: {winnings}₽\n"
                "📅 Registration: {registered_at}"
            )
        },
        "USERINFO_ADMIN": {
            "ru": (
                "👤 Профиль пользователя\n\n"
                "🆔 ID: {user_id}\n"
                "👤 Имя: username\n"
                "🔐 Хэш имени: {hashed_username}\n"
                "💰 Баланс: {balance}₽\n"
                "🏆 Выигрыши: {winnings}₽\n"
                "📧 Почта: {email} ({email_verified})\n"
                "🎮 Выбранная игра: {selected_game}\n"
                "🌐 Язык: {language}\n"
                "📅 Регистрация: {registered_at}"
            ),
            "en": (
                "👤 User Profile\n\n"
                "🆔 ID: {user_id}\n"
                "👤 Username: username\n"
                "🔐 Hashed username: {hashed_username}\n"
                "💰 Balance: {balance}₽\n"
                "🏆 Winnings: {winnings}₽\n"
                "📧 Email: {email} ({email_verified})\n"
                "🎮 Selected game: {selected_game}\n"
                "🌐 Language: {language}\n"
                "📅 Registration: {registered_at}"
            )
        },
        "USERINFO_NO_GAMES": {
            "ru": "📊 Пока нет истории игр.",
            "en": "📊 No game history yet."
        },
        "USERINFO_FOFAVORITE_GAME": {
            "ru": "⭐ Любимая игра: {favorite_game_name}, {favorite_play_times} раз(а)",
            "en": "⭐ Favorite game: {favorite_game_name}, {favorite_play_times} time(s)"
        },
        "USERINFO_GAMES_LIST": {
            "ru": "🎮 {game_name}: {count} раз(а)",
            "en": "🎮 {game_name}: {count} time(s)"
        },
        "USERINFO_GAMES_LIST_TITLE": {
            "ru": "📈 Всего игр сыграно",
            "en": "📈 Total Games Played"
        }
    }

    BALANCE = {
        "BALANCE": {
            "ru": "💰 Ваш текущий баланс: {balance} ₽",
            "en": "💰 Your current balance: {balance} ₽"
        }
    }

    REFERRAL_MESSAGES = {
        "REFERRAL_MENU": {
            "ru": (
                "💰 <b>Реферальная программа</b>\n\n"
                "Приглашайте друзей через свой уникальный бот-клон и получайте щедрые награды!\n\n"
                "📊 <b>Как это работает:</b>\n"
                "1️⃣ Создайте своего персонального бота через @BotFather\n"
                "2️⃣ Отправьте токен нашему боту\n"
                "3️⃣ Получите личную реферальную ссылку\n"
                "4️⃣ Делитесь ссылкой с друзьями и знакомыми\n"
                "5️⃣ Зарабатывайте награды за каждого нового пользователя\n\n"
                "<i>✨ Каждый ваш бот работает полностью независимо 24/7</i>"
            ),
            "en": (
                "💰 <b>Referral Program</b>\n\n"
                "Invite friends through your personal bot clone and earn generous rewards!\n\n"
                "📊 <b>How it works:</b>\n"
                "1️⃣ Create your personal bot in @BotFather\n"
                "2️⃣ Send the token to our bot\n"
                "3️⃣ Get your personal referral link\n"
                "4️⃣ Share the link with friends\n"
                "5️⃣ Earn rewards for each new user\n\n"
                "<i>✨ Each of your bots works independently 24/7</i>"
            )
        },
        "REFERRAL_CLONE_BOT_STEP1": {
            "ru": (
                "🤖 <b>Создание вашего персонального бота</b>\n\n"
                "Я помогу вам создать уникальный бот за несколько простых шагов:\n\n"
                "<b>Шаг 1:</b> Откройте @BotFather в Telegram\n"
                "<b>Шаг 2:</b> Напишите команду <code>/newbot</code>\n"
                "<b>Шаг 3:</b> Дайте боту название (например, <code>Casino_YourName</code>)\n"
                "<b>Шаг 4:</b> Дайте боту юзернейм (должен заканчиваться на <code>_bot</code>)\n"
                "<b>Шаг 5:</b> BotFather отправит вам токен доступа\n"
                "<b>Шаг 6:</b> Скопируйте токен и отправьте его сюда\n\n"
                "⚠️ <i>Важно: Никогда не делитесь токеном с другими людьми!</i>"
            ),
            "en": (
                "🤖 <b>Create Your Personal Bot</b>\n\n"
                "I'll help you create a unique bot in just a few simple steps:\n\n"
                "<b>Step 1:</b> Open @BotFather in Telegram\n"
                "<b>Step 2:</b> Send the command <code>/newbot</code>\n"
                "<b>Step 3:</b> Give your bot a name (for example, <code>Casino_YourName</code>)\n"
                "<b>Step 4:</b> Give your bot a username (must end with <code>_bot</code>)\n"
                "<b>Step 5:</b> BotFather will send you an access token\n"
                "<b>Step 6:</b> Copy the token and send it here\n\n"
                "⚠️ <i>Important: Never share your token with others!</i>"
            )
        },
        "REFERRAL_CLONE_BOT_STEP2": {
            "ru": "⏳ Проверяем токен и создаём вашего бота...",
            "en": "⏳ Verifying token and creating your bot..."
        },
        "REFERRAL_CLONE_BOT_SUCCESS": {
            "ru": (
                "✅ <b>Отлично! Ваш бот успешно создан!</b>\n\n"
                "🤖 <b>Имя вашего бота:</b> {bot_name}\n\n"
                "📊 <b>Как вы зарабатываете:</b>\n"
                "💰 <code>5%</code> от каждой ставки ваших рефералов\n"
                "💎 <code>10%</code> от каждого пополнения баланса\n"
                "🏆 <code>2%</code> от каждого выигрыша\n\n"
                "<i>🔄 Ваш бот работает автоматически и привлекает пользователей круглосуточно</i>"
            ),
            "en": (
                "✅ <b>Perfect! Your bot has been created successfully!</b>\n\n"
                "🤖 <b>Your bot name:</b> {bot_name}\n\n"
                "📊 <b>Your earnings:</b>\n"
                "💰 <code>5%</code> from each bet of your referrals\n"
                "💎 <code>10%</code> from each deposit\n"
                "🏆 <code>2%</code> from each win\n\n"
                "<i>🔄 Your bot works automatically and attracts users 24/7</i>"
            )
        },
        "REFERRAL_INVALID_TOKEN": {
            "ru": (
                "❌ <b>Токен не прошёл проверку</b>\n\n"
                "Пожалуйста, проверьте следующие моменты:\n"
                "• ✓ Токен скопирован полностью и без пробелов\n"
                "• ✓ Токен содержит двоеточие (:)\n"
                "• ✓ Боту присвоен юзернейм\n"
                "• ✓ Токен вообще ещё не использовался\n\n"
                "🔄 Попробуйте ещё раз или создайте новый бот"
            ),
            "en": (
                "❌ <b>Token verification failed</b>\n\n"
                "Please check the following:\n"
                "• ✓ Token is copied completely without spaces\n"
                "• ✓ Token contains a colon (:)\n"
                "• ✓ Bot has been assigned a username\n"
                "• ✓ Token has not been used before\n\n"
                "🔄 Try again or create a new bot"
            )
        },
        "REFERRAL_BOT_CREATION_ERROR": {
            "ru": (
                "❌ <b>Ошибка при создании бота</b>\n\n"
                "Возможные причины:\n"
                "• Токен уже использован для другого бота\n"
                "• Временная ошибка на сервере Telegram\n"
                "• Проблема с подключением к интернету\n\n"
                "🔄 Пожалуйста, попробуйте ещё раз позже"
            ),
            "en": (
                "❌ <b>Error creating bot</b>\n\n"
                "Possible reasons:\n"
                "• Token is already used for another bot\n"
                "• Temporary Telegram server error\n"
                "• Internet connection issue\n\n"
                "🔄 Please try again later"
            )
        },
        "REFERRAL_MY_REFERRALS": {
            "ru": (
                "👥 <b>Ваши рефералы</b>\n\n"
                "📊 <b>Общая статистика:</b>\n"
                "👤 Всего привлечено: <code>{total_referrals}</code>\n"
                "✅ Активных прямо сейчас: <code>{active_referrals}</code>\n"
                "💰 Получено наград: <code>{total_rewards} ⚡</code>\n\n"
                "📈 <b>Лучшие боты:</b>\n"
                "{top_bots}\n\n"
                "<i>⏱️ Обновлено: только что</i>"
            ),
            "en": (
                "👥 <b>Your Referrals</b>\n\n"
                "📊 <b>Overall Statistics:</b>\n"
                "👤 Total attracted: <code>{total_referrals}</code>\n"
                "✅ Active right now: <code>{active_referrals}</code>\n"
                "💰 Rewards earned: <code>{total_rewards} ⚡</code>\n\n"
                "📈 <b>Top bots:</b>\n"
                "{top_bots}\n\n"
                "<i>⏱️ Updated: just now</i>"
            )
        },
        "REFERRAL_MY_BOTS": {
            "ru": (
                "🤖 <b>Ваши боты-клоны</b>\n\n"
                "✨ <b>Активные боты: {active_count}</b>\n\n"
                "{bots_list}\n\n"
                "💡 <i>Совет: Создайте несколько ботов для разных групп друзей и знакомых!</i>"
            ),
            "en": (
                "🤖 <b>Your Bot Clones</b>\n\n"
                "✨ <b>Active bots: {active_count}</b>\n\n"
                "{bots_list}\n\n"
                "💡 <i>Tip: Create multiple bots for different groups of friends!</i>"
            )
        },
        "REFERRAL_BOT_DISABLED": {
            "ru": "⚠️ <b>Этот бот отключен</b>\n\nВы всё ещё получаете награды за существующих рефералов, однако новые пользователи больше не могут присоединиться через эту ссылку.",
            "en": "⚠️ <b>This bot is disabled</b>\n\nYou still receive rewards for existing referrals, but new users cannot join through this link."
        },
        "REFERRAL_REWARD_NOTIFICATION": {
            "ru": (
                "🎉 <b>Поздравляем! Новый реферал!</b>\n\n"
                "👤 Пользователь присоединился через вашего бота <code>{bot_name}</code>\n"
                "💰 Вы получили награду: <code>+100 ⚡</code>\n\n"
                "💼 Новый баланс: <code>{new_balance} ⚡</code>"
            ),
            "en": (
                "🎉 <b>Congratulations! New Referral!</b>\n\n"
                "👤 A user joined through your bot <code>{bot_name}</code>\n"
                "💰 You earned: <code>+100 ⚡</code>\n\n"
                "💼 New balance: <code>{new_balance} ⚡</code>"
            )
        },
        "REFERRAL_COPY_LINK": {
            "ru": (
                "🔗 <b>Ваша реф-ссылка скопирована в буфер обмена!</b>\n\n"
                "📱 Теперь вы можете поделиться ей в:\n"
                "💬 Telegram чатах и группах\n"
                "📱 WhatsApp\n"
                "📧 Email\n"
                "🌍 Социальные сети\n\n"
                "<i>📊 Статистика переходов обновляется в реальном времени</i>"
            ),
            "en": (
                "🔗 <b>Your referral link has been copied!</b>\n\n"
                "📱 You can now share it in:\n"
                "💬 Telegram chats and groups\n"
                "📱 WhatsApp\n"
                "📧 Email\n"
                "🌍 Social networks\n\n"
                "<i>📊 Click statistics update in real-time</i>"
            )
        },
        "REFERRAL_STATS_BOT": {
            "ru": (
                "📊 <b>Статистика бота @{bot_name}</b>\n\n"
                "👥 Привлечено рефералов: <code>{referrals_count}</code>\n"
                "✅ Активных пользователей: <code>{active_count}</code>\n"
                "💰 Всего заработано: <code>{total_reward} ⚡</code>\n"
                "📈 Рейтинг CTR: <code>{ctr}%</code>\n"
                "📅 Дата создания: <code>{created_date}</code>\n\n"
                "🔗 Ваша ссылка: <code>{ref_link}</code>"
            ),
            "en": (
                "📊 <b>Bot @{bot_name} Statistics</b>\n\n"
                "👥 Referrals attracted: <code>{referrals_count}</code>\n"
                "✅ Active users: <code>{active_count}</code>\n"
                "💰 Total earned: <code>{total_reward} ⚡</code>\n"
                "📈 CTR rating: <code>{ctr}%</code>\n"
                "📅 Creation date: <code>{created_date}</code>\n\n"
                "🔗 Your link: <code>{ref_link}</code>"
            )
        },
        "REFERRAL_WAITING_TOKEN": {
            "ru": "⏳ Ожидаю ввод токена вашего бота...",
            "en": "⏳ Waiting for your bot token..."
        },
        "REFERRAL_WELCOME": {
            "ru": (
                "👋 <b>Добро пожаловать в наш бот!</b>\n\n"
                "🎁 Вы присоединились по реферальной ссылке.\n"
                "Спасибо за регистрацию! Вам полагается приветственный бонус.\n\n"
                "🎮 Начните играть прямо сейчас и зарабатывайте награды!"
            ),
            "en": (
                "👋 <b>Welcome to our bot!</b>\n\n"
                "🎁 You joined through a referral link.\n"
                "Thanks for registering! You qualify for a welcome bonus.\n\n"
                "🎮 Start playing now and earn rewards!"
            )
        }
    }

    ADMIN_PANEL = {
        "ADMIN_PANEL": {
            "ru": "🛠️ Админ-панель:",
            "en": "🛠️ Admin panel:"
        },
        "ADMIN_SUMMARY_COUNT": {
            "ru": "👥 Количество активных игроков",
            "en": "👥 Number of active players"
        },
        "ADMIN_SUMMARY_NEEDED": {
            "ru": "💰 Общая сумма на счетах всех пользователей",
            "en": "💰 Total balance across all accounts"
        },
        "ADMIN_SUMMARY_AVG_BALANCE": {
            "ru": "📊 Средний баланс на одного игрока",
            "en": "📊 Average balance per player"
        },
        "ADMIN_SUMMARY_MAX_BALANCE": {
            "ru": "🔼 Максимальный баланс",
            "en": "🔼 Highest balance"
        },
        "ADMIN_SUMMARY_MIN_BALANCE": {
            "ru": "🔽 Минимальный баланс",
            "en": "🔽 Lowest balance"
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
