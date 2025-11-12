class Messages:
    REGISTRATION = {
        "REGISTRATION": {
            "ru": "📧 Регистрация\n\n"
                  "Пожалуйста, введите вашу электронную почту. На этот "
                  "адрес мы будем отправлять квитанции о всех ваших операциях.",
            "en": "📧 Registration\n\n"
                  "Please enter your email address. We will send all "
                  "receipts and transaction confirmations to this address."
        },
        "CHANGE_EMAIL": {
            "ru": "✏️ Изменение адреса электронной почты\n\n"
                  "Укажите новый адрес электронной почты, на который мы будем отправлять ваши квитанции.",
            "en": "✏️ Change Email Address\n\nEnter your new email address where we will send your receipts."
        },
        "REGISTRATION_ERROR_EMAIL": {
            "ru": "❌ Ошибка\n\nАдрес электронной почты некорректен. Пожалуйста, проверьте формат и попробуйте снова.",
            "en": "❌ Error\n\nThe email address is invalid. Please check the format and try again."
        },
        "REGISTRATION_ERROR_CODE": {
            "ru": "❌ Ошибка подтверждения\n\n"
                  "Код подтверждения неверен. Пожалуйста, проверьте код и попробуйте ещё раз.",
            "en": "❌ Verification Error\n\n"
                  "The confirmation code is incorrect. Please check the code and try again."
        },
        "REGISTRATION_STEP_TWO": {
            "ru": "✉️ Подтверждение почты\n\n"
                  "Мы отправили 6-значный код на указанный адрес. Пожалуйста, введите его ниже:",
            "en": "✉️ Email Verification\n\nWe've sent a 6-digit code to your email. Please enter it below:"
        },
        "REGISTRATION_COMPLETED": {
            "ru": "✅ Поздравляем!\n\nРегистрация успешно завершена. Ваш адрес электронной почты: {email}",
            "en": "✅ Congratulations!\n\nRegistration completed successfully. Your email address: {email}"
        }
    }

    MAIN_MENU = {
        "MAIN_MENU": {
            "ru": "🎰 Добро пожаловать в наш элитный игровой клуб!\n\n"
                  "🚀 Испытайте удачу, крутите барабаны и сорвите свой крупный выигрыш прямо сейчас!\n\n"
                  "<b>🎉 Сегодня ваш день! Не теряйте шанс выиграть больше!</b>",
            "en": "🎰 Welcome to our elite gaming club!\n\n"
                  "🚀 Feel the thrill, spin the reels, and hit your big win right now!\n\n"
                  "<b>🎉 Today is your day! Don't miss your chance to win even more!</b>"
        },
        "SETTINGS": {
            "ru": "⚙️ Ваши настройки\n\nВыбранная игра: {selected_game}\n",
                  # "📧 Почта: {email}",
            "en": "⚙️ Your Settings\n\nSelected game: {selected_game}\n"
                  # "📧 Email: {email}"
        },
        "CHANGE_GAME": {
            "ru": "🎮 Выберите игру:",
            "en": "🎮 Select a game:"
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
                "👤 Имя: username\n"
                "💰 Баланс: {balance}$\n"
                "🏆 Выигрыши: {winnings}$\n"
                "📅 Дата регистрации: {registered_at}"
            ),
            "en": (
                "👤 Your Profile\n\n"
                "👤 Username: username\n"
                "💰 Balance: {balance}$\n"
                "🏆 Winnings: {winnings}$\n"
                "📅 Registration date: {registered_at}"
            )
        },
        "USERINFO": {
            "ru": (
                "👤 Профиль пользователя\n\n"
                "👤 Имя: username\n"
                "💰 Баланс: {balance}$\n"
                "🏆 Выигрыши: {winnings}$\n"
                "📅 Регистрация: {registered_at}"
            ),
            "en": (
                "👤 User Profile\n\n"
                "👤 Username: username\n"
                "💰 Balance: {balance}$\n"
                "🏆 Winnings: {winnings}$\n"
                "📅 Registration: {registered_at}"
            )
        },
        "USERINFO_ADMIN": {
            "ru": (
                "👤 Профиль пользователя\n\n"
                "🆔 ID: {user_id}\n"
                "👤 Имя: username\n"
                "🔐 Хэш имени: {hashed_username}\n"
                "💰 Баланс: {balance}$\n"
                "🏆 Выигрыши: {winnings}$\n"
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
                "💰 Balance: {balance}$\n"
                "🏆 Winnings: {winnings}$\n"
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
            "ru": "⭐ Любимая игра: favorite_game_name, favorite_play_times раз(а)",
            "en": "⭐ Favorite game: favorite_game_name, favorite_play_times time(s)"
        },
        "USERINFO_GAMES_LIST": {
            "ru": "game_name: count раз(а)",
            "en": "game_name: count time(s)"
        },
        "USERINFO_GAMES_LIST_TITLE": {
            "ru": "📈 Всего игр сыграно",
            "en": "📈 Total Games Played"
        }
    }

    BALANCE = {
        "BALANCE": {
            "ru": "💰 Ваш текущий баланс: {balance}$",
            "en": "💰 Your current balance: {balance}$"
        },
        "SELECT_CURRENCY": {
            "ru": "💱 Выберите валюту для операции:",
            "en": "💱 Select currency for operation:"
        },
        "SELECT_AMOUNT": {
            "ru": "💰 Выберите сумму:",
            "en": "💰 Select amount:"
        },
        "CURRENCY_NOT_AVAILABLE": {
            "ru": "❌ Данная валюта временно недоступна. Попробуйте позже.",
            "en": "❌ This currency is temporarily unavailable. Please try later."
        },
        "PAYMENT_LINK": {
            "ru": "💳 Ссылка для оплаты создана. Нажмите кнопку ниже для пополнения:",
            "en": "💳 Payment link created. Click the button below to deposit:"
        },
        "DEPOSIT_SUCCESS": {
            "ru": "✅ Платеж успешно получен! Баланс пополнен.",
            "en": "✅ Payment received successfully! Balance updated."
        },
        "DEPOSIT_FAILED": {
            "ru": "❌ Платеж не обнаружен или еще обрабатывается.",
            "en": "❌ Payment not found or still processing."
        },
        "CANCEL_DEPOSIT_CONFIRM": {
            "ru": "⚠️ Вы уверены, что хотите отменить платёж?",
            "en": "⚠️ Are you sure you want to cancel the payment?"
        },
        "DEPOSIT_CANCELLED": {
            "ru": "✅ Платеж успешно отменен.",
            "en": "✅ Payment cancelled successfully."
        },
        "DEPOSIT_CANCEL_FAILED": {
            "ru": "❌ Не удалось отменить платеж. Возможно, он уже обработан.",
            "en": "❌ Failed to cancel payment. It may have been processed already."
        },
        "WITHDRAW_SUCCESS": {
            "ru": "✅ Средства отправлены!\n\n"
                  "💰 Сумма: <code>{amount} {currency}</code>\n"
                  "⏳ Статус: В процессе доставки\n\n"
                  "Обычно средства поступают в течение нескольких минут.",
            "en": "✅ Withdrawal completed!\n\n"
                  "💰 Amount: <code>{amount} {currency}</code>\n"
                  "⏳ Status: In transit\n\n"
                  "Funds usually arrive within a few minutes."
        },
        "EMPTY_BALANCE_FOR_WITHDRAW": {
            "ru": "❌ Невозможно вывести средства\n\n"
                  "💰 Ваш баланс пуст. Сначала пополните счет.\n"
                  "📝 Выберите пополнение в главном меню.",
            "en": "❌ Unable to withdraw funds\n\n"
                  "💰 Your balance is empty. Please deposit funds first.\n"
                  "📝 Select deposit from the main menu."
        },
        "WITHDRAW_ERROR": {
            "ru": "❌ Ошибка при создании заявки на вывод.\n\n"
                  "🔍 Возможные причины:\n"
                  "• Недостаточно средств\n"
                  "• Минимальная сумма вывода не достигнута\n"
                  "• Временный сбой системы\n\n"
                  "Попробуйте позже или обратитесь в поддержку.",
            "en": "❌ Error creating withdrawal request.\n\n"
                  "🔍 Possible reasons:\n"
                  "• Insufficient balance\n"
                  "• Minimum withdrawal amount not reached\n"
                  "• Temporary system error\n\n"
                  "Please try again later or contact support."
        }
    }

    REFERRAL_MESSAGES = {
        "REFERRAL_MENU": {
            "ru": (
                "💰 <b>Реферальная программа</b>\n\n"
                "Зовите друзей в своего бота — получайте щедрые награды за каждого приглашённого!\n\n"
                "📊 <b>Как это работает:</b>\n"
                "1️⃣ Создайте своего персонального бота через @BotFather\n"
                "2️⃣ Отправьте токен нашему боту\n"
                "3️⃣ Получите личную реферальную ссылку\n"
                "4️⃣ Делитесь ссылкой с друзьями и знакомыми\n"
                "5️⃣ Зарабатывайте награды за каждого нового пользователя\n\n"
                "<i>✨ Ваш бот работает автономно 24/7</i>"
            ),
            "en": (
                "💰 <b>Referral Program</b>\n\n"
                "Invite your friends to your bot — earn generous rewards for each one!\n\n"
                "📊 <b>How it works:</b>\n"
                "1️⃣ Create your personal bot in @BotFather\n"
                "2️⃣ Send the token to our bot\n"
                "3️⃣ Get your personal referral link\n"
                "4️⃣ Share the link with friends\n"
                "5️⃣ Earn rewards for each new user\n\n"
                "<i>✨ Your bot works autonomously 24/7</i>"
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
                "<b>Шаг 6:</b> Скопируйте токен (пример токена: "
                "<code>123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11</code>) "
                "и отправьте его сюда\n\n"
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
                "<b>Step 6:</b> Copy the token (token example: <code>123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11</code>) "
                "and send it here\n\n"
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
                "🏆 <code>2%</code> от каждого выигрыша"
            ),
            "en": (
                "✅ <b>Perfect! Your bot has been created successfully!</b>\n\n"
                "🤖 <b>Your bot name:</b> {bot_name}\n\n"
                "📊 <b>Your earnings:</b>\n"
                "💰 <code>5%</code> from each bet of your referrals\n"
                "🏆 <code>2%</code> from each win"
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
                "👤 Всего привлечено: <code>{total_refs}</code>\n"
                "💰 Получено наград: <code>{rewarded}$</code>"
            ),
            "en": (
                "👥 <b>Your Referrals</b>\n\n"
                "📊 <b>Overall Statistics:</b>\n"
                "👤 Total attracted: <code>{total_refs}</code>\n"
                "💰 Rewards earned: <code>{rewarded}$</code>"
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
        "REFERRAL_REWARD_NOTIFICATION": {
            "ru": (
                "🎉 <b>Поздравляем! Новый реферал!</b>\n\n"
                "👤 Пользователь присоединился через вашего бота <code>{bot_name}</code>"
            ),
            "en": (
                "🎉 <b>Congratulations! New Referral!</b>\n\n"
                "👤 A user joined through your bot <code>{bot_name}</code>"
            )
        },
        "REFERRAL_WAITING_TOKEN": {
            "ru": "⏳ Ожидаю ввод токена вашего бота...",
            "en": "⏳ Waiting for your bot token..."
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
        },
        "ADMIN_TABLES_LIST": {
            "ru": "📊 Таблицы базы данных:",
            "en": "📊 Database tables:"
        },
        "ADMIN_BALANCE_ISSUED": {
            "ru": "✅ Баланс успешно выдан пользователю.",
            "en": "✅ Balance successfully issued to user."
        },
        "ADMIN_BALANCE_RESET": {
            "ru": "✅ Баланс пользователя успешно сброшен.",
            "en": "✅ User balance successfully reset."
        },
        "GAME_SETTINGS": {
            "ru": "⚙️ Выберите игру для настройки:",
            "en": "⚙️ Select a game to configure:"
        },
        "GAME_CONFIG_SELECT": {
            "ru": "⚙️ Выберите игру для просмотра конфигурации:",
            "en": "⚙️ Select a game to view configuration:"
        },
        "GAME_INFO": {
            "ru": "{game_icon} {game_name}",
            "en": "{game_icon} {game_name}"
        },
        "MAX_BET_CONFIG": {
            "ru": (
                "⚙️ Макс. ставка\n\n"
                "💰 Текущее значение: {max_bet}$\n"
                "📊 (1% от баланса казино)"
            ),
            "en": (
                "⚙️ Max bet\n\n"
                "💰 Current value: {max_bet}$\n"
                "📊 (1% of casino balance)"
            )
        }
    }

    GAMES = {
        "USER_ALREADY_PLAYING": {
            "ru": "❌ Вы уже участвуете в игре!",
            "en": "❌ You are already playing!"
        },
        "SELECT_BET": {
            "ru": "💰 Выберите размер ставки:",
            "en": "💰 Select your bet:"
        },
        "EMPTY_BALANCE_FOR_BET": {
            "ru": "❌ Невозможно сделать ставку\n\n"
                  "💰 Ваш баланс пуст. Пополните счет, чтобы начать играть.\n"
                  "📝 Выберите пополнение в главном меню.",
            "en": "❌ Unable to place a bet\n\n"
                  "💰 Your balance is empty. Deposit funds to start playing.\n"
                  "📝 Select deposit from the main menu."
        },
        "INSUFFICIENT_BALANCE": {
            "ru": "❌ Недостаточно средств",
            "en": "❌ Insufficient balance"
        },
        "GAME_STARTING": {
            "ru": "🎮 Игра начинается...",
            "en": "🎮 Game starting..."
        },
        "GAME_WIN": {
            "ru": "<b>🎉 Поздравляем, вам улыбнулась удача!</b>\n\n{icon} Результат: {final_result}\n"
                  "#🎲 Ваша ставка: {user_bet}\n#"
                  "💵 Ваш большой выигрыш: {amount}$\n"
                  "Ваш шанс сделать это снова растет! Не остановитесь на достигнутом! 🚀",
            "en": "<b>🎉 Congratulations, luck is on your side!</b>\n\n{icon} Result: {final_result}\n"
                  "#🎲 Your bet: {user_bet}\n#"
                  "💵 Your big prize: {amount}$\n"
                  "Your chance to do it again is growing! Don't stop now! 🚀"
        },
        "GAME_LOSE": {
            "ru": "😢 К сожалению, в этот раз не повезло\n\n{icon} Результат: {final_result}\n"
                  "#🎲 Ваша ставка: {user_bet}\n#"
                  "Не сдавайтесь — следующий раунд может изменить всё! <b>Попробуйте снова! 🔥</b>",
            "en": "😢 Unfortunately, not your lucky round\n\n{icon} Result: {final_result}\n"
                  "#🎲 Your bet: {user_bet}\n#"
                  "Don't give up — the next round might change everything! <b>Try again! 🔥</b>"
        },
        "GAME_WIN_ANNOUNCEMENT": {
            "ru": "<b>🔥 Внимание!</b>\n\nИгрок {username} <b>только что выиграл {amount}$</b>!\n"
                  "#🎲 Ставка: {user_bet}\n#"
                  "{icon} Результат: {final_result}\n\n"
                  "Удача на вашей стороне — присоединяйтесь к игре и попробуйте выиграть сами! 🚀\n\n\n"
                  "<b>🔥 Attention!</b>\n\nPlayer {username} <b>just won {amount}$</b>!\n"
                  "#🎲 Bet: {user_bet}\n#"
                  "{icon} Result: {final_result}\n\n"
                  "Luck is on your side — join the game and try to win yourself! 🚀",
            "en": "<b>🔥 Внимание!</b>\n\nИгрок {username} <b>только что выиграл {amount}$</b>!\n"
                  "#🎲 Ставка: {user_bet}\n#"
                  "{icon} Результат: {final_result}\n\n"
                  "Удача на вашей стороне — присоединяйтесь к игре и попробуйте выиграть сами! 🚀\n\n\n"
                  "<b>🔥 Attention!</b>\n\nPlayer {username} <b>just won {amount}$</b>!\n"
                  "#🎲 Bet: {user_bet}\n#"
                  "{icon} Result: {final_result}\n\n"
                  "Luck is on your side — join the game and try to win yourself! 🚀"
        }
    }

    INTERACTIVE_GAMES = {
        "INTERACTIVE_GAME_NOT_FOUND": {
            "ru": "❌ Игра не найдена",
            "en": "❌ Game not found"
        },
        "ERROR_IN_MOVE": {
            "ru": "❌ Ошибка хода",
            "en": "❌ Error in movement"
        },
        "SESSION_EXPIRED": {
            "ru": "❌ Сессия истекла",
            "en": "❌ Session expired"
        }
    }

    HILO_MESSAGES = {
        "HILO_ROUND_STATE": {
            "ru": "{icon} Текущая карта: {card_display}\n"
                  "🔥 <b>Серия:</b> {streak}\n"
                  "💰 <b>Множитель:</b> ×{multiplier:.2f}\n",
            "en": "{icon} Current card: {card_display}\n"
                  "🔥 <b>Streak:</b> {streak}\n"
                  "💰 <b>Multiplier:</b> ×{multiplier:.2f}\n"
        },
        "HILO_FINAL_RESULT": {
            "ru": "\n{icon} Последняя карта: {last_card}\n"
                  "🔥 Финальная серия: {streak}\n"
                  "💰 Финальный множитель: ×{multiplier:.2f}\n",
            "en": "\n{icon} The last card: {last_card}\n"
                  "🔥 Final streak: {streak}\n"
                  "💰 Final multiplier: ×{multiplier:.2f}\n"
        }
    }

    MINES_MESSAGES = {
        "MINES_ROUND_STATE": {
            "ru": "{icon} МИНЫ\n\n"
                  "📊 Открыто ячеек: {opened_count}\n"
                  "💰 Множитель: ×{multiplier}\n"
                  "🎯 Потенциальный выигрыш: {potential_win}$\n"
                  "💡 Выберите ячейку или заберите выигрыш!",
            "en": "{icon} MINES\n\n"
                  "📊 Cells opened: {opened_count}\n"
                  "💰 Multiplier: ×{multiplier}\n"
                  "🎯 Potential win: {potential_win}$\n"
                  "💡 Choose a cell or cash out!"
        },
        "MINES_LOST": {
            "ru": "\n{icon} <b>БУМ! Вы подорвались!</b>\n💥 Открыто ячеек: {opened_count}\n",
            "en": "\n{icon} <b>BOOM! You hit a bomb!</b>\n💥 Cells opened: {opened_count}\n"
        },
        "MINES_WIN": {
            "ru": "\n✅ Открыто ячеек: {opened_count}\n💰 Множитель: ×{multiplier}\n🏆 Выигрыш: {win_amount}$\n",
            "en": "\n✅ Cells opened: {opened_count}\n💰 Multiplier: ×{multiplier}\n🏆 Win: {win_amount}$\n"
        }
    }

    CHANNEL_CONFIG = {
        "BOT_START_IN_CHAT": {
            "en": "❌ Этот бот работает только в личных сообщениях!\n"
                  "Пожалуйста, напишите мне в личку для запуска.\n\n\n"
                  "❌ This bot only works in private messages!\n"
                  "Please message me privately to launch it."
        },
        "BOT_CONFIG": {
            "ru": (
                "⚙️ Настройка бота для уведомлений\n\n"
                "📢 Здесь вы можете подключить бота к каналу\n"
                "для автоматической публикации уведомлений о выигрышах\n\n"
                "📌 Подключённый канал: {channel_username}\n"
                "📌 Подключённый новостной канал: {news_channel_username}"
            ),
            "en": (
                "⚙️ Bot notification setup\n\n"
                "📢 Here you can connect the bot to a channel\n"
                "for automatic win announcements\n\n"
                "📌 Connected channel: {channel_username}\n"
                "📌 Connected news channel: {news_channel_username}"
            )
        },
        "BOT_CONFIG_ENTER_ID": {
            "ru": (
                "📝 Введите ID канала или чата\n\n"
                "💡 Как получить ID:\n"
                "1️⃣ Перешлите сообщение из канала/чата боту @userinfobot\n"
                "2️⃣ Вы получите ID в ответе (пример: <code>-10***********</code>)\n"
                "3️⃣ Скопируйте ID и пришлите его сюда\n\n"
                "⚠️ Убедитесь, что бот добавлен в канал/чат как администратор!"
            ),
            "en": (
                "📝 Enter channel or chat ID\n\n"
                "💡 How to get ID:\n"
                "1️⃣ Forward a message from the channel/chat to @userinfobot\n"
                "2️⃣ You will receive the ID in the response (example: <code>-10***********</code>)\n"
                "3️⃣ Copy the ID and send it here\n\n"
                "⚠️ Make sure the bot is added to the channel/chat as an administrator!"
            )
        },
        "CHANNEL_CONFIG_ERROR": {
            "ru": (
                "❌ Ошибка настройки канала\n\n"
                "🔍 Возможные причины:\n"
                "• Неверный ID канала или чата\n"
                "• Бот не добавлен в канал как администратор\n"
                "• Канал является приватным\n\n"
                "📝 Убедитесь, что:\n"
                "1️⃣ ID канала указан правильно\n"
                "2️⃣ Бот добавлен в канал с правами администратора\n"
                "3️⃣ Канал доступен для бота"
            ),
            "en": (
                "❌ Channel configuration error\n\n"
                "🔍 Possible reasons:\n"
                "• Invalid channel or chat ID\n"
                "• Bot not added to channel as administrator\n"
                "• Channel is private\n\n"
                "📝 Make sure that:\n"
                "1️⃣ Channel ID is correct\n"
                "2️⃣ Bot is added to channel with admin rights\n"
                "3️⃣ Channel is accessible to bot"
            )
        },
        "CHANNEL_TEST_MESSAGE": {
            "ru": (
                "✅ Тестовое сообщение\n\n"
                "🤖 Бот успешно подключен к каналу!\n"
                "Все сообщения будут публиковаться здесь."
            ),
            "en": (
                "✅ Test message\n\n"
                "🤖 Bot successfully connected to channel!\n"
                "All messages will be posted here."
            )
        },
        "CHANNEL_CONFIG_SUCCESS": {
            "ru": (
                "✅ Канал успешно настроен!\n\n"
                "📢 Тестовое сообщение отправлено в канал.\n"
                "Если вы его видите — настройка завершена успешно!\n\n"
                "🎉 Теперь все объявления о выигрышах будут публиковаться в указанном канале."
            ),
            "en": (
                "✅ Channel configured successfully!\n\n"
                "📢 Test message sent to channel.\n"
                "If you can see it — configuration completed successfully!\n\n"
                "🎉 Now all win announcements will be posted to the specified channel."
            )
        }
    }

    NEWS_MESSAGE_SEND = {
        "NEWS_CHANNEL_NOT_CONNECTED": {
            "ru": (
                "⚠️ Новостной канал не подключён\n\n"
                "📰 Новостной канал не настроен для отправки уведомлений.\n"
                "Подключите его в административной панели для автоматической публикации новостей.\n\n"
                "🔧 Как подключить:\n"
                "1️⃣ Откройте админ панель\n"
                "2️⃣ Перейдите в раздел настройки каналов\n"
                "3️⃣ Укажите ID новостного канала\n"
                "4️⃣ Убедитесь, что бот добавлен как администратор"
            ),
            "en": (
                "⚠️ News channel not connected\n\n"
                "📰 News channel is not configured for sending notifications.\n"
                "Connect it in the admin panel for automatic news publication.\n\n"
                "🔧 How to connect:\n"
                "1️⃣ Open admin panel\n"
                "2️⃣ Go to channel settings section\n"
                "3️⃣ Specify the news channel ID\n"
                "4️⃣ Make sure bot is added as administrator"
            )
        },
        "NEWS_CHANNEL_SEND_ERROR": {
            "ru": (
                "❌ Не удалось отправить сообщение в новостной канал\n\n"
                "🔍 Возможные причины ошибки:\n"
                "• Неверный ID новостного канала\n"
                "• Бот не добавлен в новостной канал как администратор\n"
                "• Канал недоступен или удалён\n"
                "• Бот не имеет прав на публикацию сообщений\n\n"
                "📝 Для решения проблемы:\n"
                "1️⃣ Проверьте, что ID канала указан правильно\n"
                "2️⃣ Убедитесь, что бот добавлен в канал с правами администратора\n"
                "3️⃣ Дайте боту права на отправку сообщений\n"
                "4️⃣ Попробуйте заново настроить новостной канал в админ панели"
            ),
            "en": (
                "❌ Failed to send message to news channel\n\n"
                "🔍 Possible error causes:\n"
                "• Invalid news channel ID\n"
                "• Bot not added to news channel as administrator\n"
                "• Channel is unavailable or deleted\n"
                "• Bot does not have permission to post messages\n\n"
                "📝 To resolve the issue:\n"
                "1️⃣ Check that the channel ID is correct\n"
                "2️⃣ Make sure bot is added to channel with admin rights\n"
                "3️⃣ Grant bot permissions to send messages\n"
                "4️⃣ Try reconfiguring the news channel in admin panel"
            )
        },
        "NEWS_CHANNEL_SEND_SUCCESS": {
            "ru": "✅ Сообщение успешно отправлено!",
            "en": "✅ Message sent successfully!"
        },
        "SEND_MESSAGE_TYPE_CHOICE": {
            "ru": (
                "📤 Выберите тип отправляемого сообщения\n\n"
                "🚀 Стартовое — приветственное сообщение для новых пользователей\n"
                "📝 Кастомное — ваше собственное сообщение"
            ),
            "en": (
                "📤 Select the type of message to send\n\n"
                "🚀 Startup — greeting message for new users\n"
                "📝 Custom — your own message"
            )
        },
        "ENTER_MESSAGE_TEXT": {
            "ru": (
                "📝 Введите текст сообщения для отправки\n\n"
                "💡 Вы можете использовать HTML-форматирование:\n"
                "<code>&lt;b&gt;жирный текст&lt;/b&gt;</code>\n"
                "<code>&lt;i&gt;курсив&lt;/i&gt;</code>\n"
                "<code>&lt;u&gt;подчёркивание&lt;/u&gt;</code>\n"
                "<code>&lt;a href=\"URL\"&gt;ссылка&lt;/a&gt;</code>"
            ),
            "en": (
                "📝 Enter the message text to send\n\n"
                "💡 You can use HTML formatting:\n"
                "<code>&lt;b&gt;bold text&lt;/b&gt;</code>\n"
                "<code>&lt;i&gt;italic&lt;/i&gt;</code>\n"
                "<code>&lt;u&gt;underline&lt;/u&gt;</code>\n"
                "<code>&lt;a href=\"URL\"&gt;link&lt;/a&gt;</code>"
            )
        },
        "ENTER_MESSAGE_BUTTONS": {
            "ru": (
                "🔘 Введите кнопки для сообщения (опционально)\n\n"
                "📋 Формат: <code>Название кнопки|URL</code>\n"
                "Каждая кнопка на новой строке.\n\n"
                "📌 Пример:\n"
                "<code>Перейти на сайт|https://example.com</code>\n"
                "<code>Поддержка|https://t.me/support</code>\n\n"
                "⚠️ Отправьте <code>[NONE]</code>, если кнопки не требуются"
            ),
            "en": (
                "🔘 Enter buttons for the message (optional)\n\n"
                "📋 Format: <code>Button Name | URL</code>\n"
                "Each button on a new line.\n\n"
                "📌 Example:\n"
                "<code>Visit Website | https://example.com</code>\n"
                "<code>Support | https://t.me/support</code>\n\n"
                "⚠️ Send <code>[NONE]</code> if buttons are not needed"
            )
        },
        "CUSTOM_MESSAGE_CANCELLED": {
            "ru": (
                "❌ Отправка кастомного сообщения отменена\n\n"
                "📨 Операция была прервана.\n"
                "Вы можете повторить попытку позже или выбрать другое действие."
            ),
            "en": (
                "❌ Custom message sending cancelled\n\n"
                "📨 The operation has been interrupted.\n"
                "You can try again later or select another action."
            )
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
        **ADMIN_PANEL,

        # ═════════════════════ Игры ════════════════════
        **GAMES,
        **INTERACTIVE_GAMES,
        **HILO_MESSAGES,
        **MINES_MESSAGES,

        # ════════════════ Настройка канала ═════════════
        **CHANNEL_CONFIG,

        # ══════════════ Отправка новостей ══════════════
        **NEWS_MESSAGE_SEND
    }
