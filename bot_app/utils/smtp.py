import smtplib
import random
from enum import Enum
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from email_validator import validate_email, EmailNotValidError


class Language(Enum):
    """Поддерживаемые языки"""
    RUSSIAN = "ru"
    ENGLISH = "en"


class EmailConfig:
    """Конфигурация для отправки email"""
    SMTP_SERVER = ""
    SMTP_PORT = 2525
    FROM_EMAIL = ""
    PASSWORD = ""

    PRIMARY_COLOR = "#c41e3a"
    DARK_BG = "#000000"
    LIGHT_BG = "#ffffff"
    TEXT_COLOR = "#000000"
    LIGHT_TEXT = "#666666"

    BOT_USERNAME = "plaza_support_BOT"


class EmailTexts:
    """Текстовые константы для разных языков"""
    MESSAGES = {
        Language.RUSSIAN: {
            "verification_code": "Код подтверждения",
            "enter_code": "Для завершения регистрации введите этот код подтверждения в приложение",
            "open_bot": "Открыть бота",
            "subject": "🎰 Ваш код подтверждения Plaza",
            "text_body_intro": "Код подтверждения:",
            "text_body_instruction": "Введите этот код для подтверждения email в Plaza.",
            "text_body_contact": "Если у вас возникли вопросы, напишите нам:",
            "greeting": "Здравствуйте!",
            "ignore_message": "Если вы не запрашивали регистрацию, проигнорируйте это письмо.",
            "expiry": "Действителен 10 минут",
        },
        Language.ENGLISH: {
            "verification_code": "Verification Code",
            "enter_code": "Enter this code to verify your email and complete registration at Plaza",
            "open_bot": "Open Bot",
            "subject": "🎰 Your Plaza Verification Code",
            "text_body_intro": "Verification Code:",
            "text_body_instruction": "Enter this code to verify your email at Plaza.",
            "text_body_contact": "Questions? Message us on Telegram:",
            "greeting": "Hello!",
            "ignore_message": "If you did not request registration, please ignore this email.",
            "expiry": "Valid for 10 minutes",
        }
    }

    @staticmethod
    def get_text(key: str, language: Language) -> str:
        """Получить текст на нужном языке"""
        return EmailTexts.MESSAGES[language].get(key, "")


class Email:
    """Класс для работы с email отправками"""

    @staticmethod
    def _detect_language_from_email(email: str) -> Language:
        """
        Определяет язык по домену email (например, .ru для русского)

        Логика определения:
        - Домены .ru, .бел, .укр → RUSSIAN
        - Остальные → ENGLISH

        :param email: Email адрес пользователя
        :return: Language: Определенный язык
        """
        email_lower = email.lower()
        russian_domains = ['.ru', '.бел', '.укр', '.рф']
        for domain in russian_domains:
            if email_lower.endswith(domain):
                return Language.RUSSIAN
        return Language.ENGLISH

    @staticmethod
    def _get_html_template(code: str, language: Language) -> str:
        """Генерирует HTML шаблон письма в минималистичном стиле Plaza"""
        texts = {
            "greeting": EmailTexts.get_text("greeting", language),
            "verification_code": EmailTexts.get_text("verification_code", language),
            "enter_code": EmailTexts.get_text("enter_code", language),
            "expiry": EmailTexts.get_text("expiry", language),
            "ignore_message": EmailTexts.get_text("ignore_message", language),
            "contact": EmailTexts.get_text("text_body_contact", language),
        }

        config = EmailConfig

        return f"""
        <!DOCTYPE html>
        <html lang="{'ru' if language == Language.RUSSIAN else 'en'}">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Plaza - {texts['verification_code']}</title>
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    background-color: {config.DARK_BG};
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                }}
                .email-container {{
                    max-width: 500px;
                    margin: 20px auto;
                    background-color: {config.LIGHT_BG};
                    border: 2px solid {config.DARK_BG};
                    border-radius: 2px;
                }}
                .header {{
                    background-color: {config.DARK_BG};
                    border-bottom: 3px solid {config.PRIMARY_COLOR};
                    padding: 30px;
                    text-align: center;
                }}
                .logo-text {{
                    color: {config.LIGHT_BG};
                    font-size: 32px;
                    font-weight: 900;
                    letter-spacing: 3px;
                    margin: 0;
                }}
                .content {{
                    padding: 40px 30px;
                }}
                .greeting {{
                    color: {config.TEXT_COLOR};
                    font-size: 16px;
                    line-height: 1.6;
                    margin: 0 0 30px 0;
                }}
                .code-section {{
                    background-color: #f5f5f5;
                    border-left: 4px solid {config.PRIMARY_COLOR};
                    padding: 25px;
                    margin: 30px 0;
                    text-align: center;
                }}
                .code-label {{
                    color: {config.LIGHT_TEXT};
                    font-size: 11px;
                    text-transform: uppercase;
                    letter-spacing: 1.5px;
                    margin-bottom: 12px;
                }}
                .verification-code {{
                    color: {config.TEXT_COLOR};
                    font-size: 48px;
                    font-weight: 900;
                    letter-spacing: 8px;
                    font-family: 'Courier New', monospace;
                    margin: 18px 0;
                }}
                .code-expiry {{
                    color: {config.PRIMARY_COLOR};
                    font-size: 11px;
                    margin-top: 12px;
                }}
                .instruction {{
                    color: {config.TEXT_COLOR};
                    font-size: 14px;
                    line-height: 1.7;
                    margin: 30px 0;
                }}
                .divider {{
                    color: {config.PRIMARY_COLOR};
                    text-align: center;
                    margin: 20px 0;
                    font-size: 14px;
                    letter-spacing: 2px;
                }}
                .footer {{
                    border-top: 1px solid #e0e0e0;
                    padding: 20px 30px;
                    text-align: center;
                }}
                .footer-text {{
                    color: {config.LIGHT_TEXT};
                    font-size: 12px;
                    line-height: 1.6;
                    margin: 0 0 10px 0;
                }}
                .support-link {{
                    color: {config.PRIMARY_COLOR};
                    text-decoration: none;
                    font-weight: bold;
                }}
                @media only screen and (max-width: 600px) {{
                    .email-container {{
                        width: 100% !important;
                    }}
                    .verification-code {{
                        font-size: 36px;
                        letter-spacing: 4px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <!-- Header -->
                <div class="header">
                    <p class="logo-text">PLAZA</p>
                </div>

                <!-- Content -->
                <div class="content">
                    <p class="greeting">{texts['greeting']}</p>

                    <div class="divider">♠ ♥ ♦ ♣</div>

                    <p class="instruction">
                        {texts['enter_code']}
                    </p>

                    <!-- Code Section -->
                    <div class="code-section">
                        <p class="code-label">{texts['verification_code']}</p>
                        <p class="verification-code">{code}</p>
                        <p class="code-expiry">⏱ {texts['expiry']}</p>
                    </div>

                    <p class="instruction">
                        {texts['ignore_message']}
                    </p>

                    <div class="divider">♠ ♥ ♦ ♣</div>

                    <p class="footer-text">
                        {texts['contact']}<br>
                        <a href="https://t.me/plaza_support_BOT" class="support-link">@plaza_support_BOT</a>
                    </p>
                </div>

                <!-- Footer -->
                <div class="footer">
                    <p class="footer-text">
                        © 2025 Plaza. {'Все права защищены.' if language == Language.RUSSIAN else 'All rights reserved.'}
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

    @staticmethod
    def generate_verification_code() -> str:
        """Генерирует 6-значный код подтверждения"""
        return ''.join(str(random.randint(0, 9)) for _ in range(6))

    @staticmethod
    def validate_email_address(email: str) -> bool:
        """Проверяет валидность email адреса"""
        try:
            validate_email(email)
            return True
        except EmailNotValidError:
            return False

    @staticmethod
    def send_verification_email(recipient_email: str, verification_code: str, language: Optional[Language] = None) -> dict:
        """
        Отправляет письмо с кодом подтверждения

        :param recipient_email: Email адрес получателя
        :param verification_code: Код подтверждения (если None, генерируется автоматически)
        :param language: Язык письма (если None, определяется по домену)
        :return: dict со статусом отправки
        """
        if not Email.validate_email_address(recipient_email):
            return {"success": False, "error": "Invalid email address"}
        if language is None:
            language = Email._detect_language_from_email(recipient_email)
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = EmailTexts.get_text("subject", language)
            msg["From"] = EmailConfig.FROM_EMAIL
            msg["To"] = recipient_email
            text_body = f"""
            {EmailTexts.get_text('greeting', language)}

            {EmailTexts.get_text('text_body_instruction', language)}

            {EmailTexts.get_text('verification_code', language)}: {verification_code}

            {EmailTexts.get_text('text_body_contact', language)}
            @plaza_support_BOT
            """

            part1 = MIMEText(text_body, "plain")
            msg.attach(part1)

            html_body = Email._get_html_template(verification_code, language)
            part2 = MIMEText(html_body, "html")
            msg.attach(part2)

            with smtplib.SMTP(EmailConfig.SMTP_SERVER, EmailConfig.SMTP_PORT) as server:
                server.starttls()
                server.login(EmailConfig.FROM_EMAIL, EmailConfig.PASSWORD)
                server.sendmail(EmailConfig.FROM_EMAIL, recipient_email, msg.as_string())

            return {
                "success": True,
                "message": "Email sent successfully",
                "code": verification_code,
                "language": language.value
            }

        except smtplib.SMTPAuthenticationError:
            return {"success": False, "error": "SMTP authentication failed"}
        except smtplib.SMTPException as e:
            return {"success": False, "error": f"SMTP error: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}
