import smtplib
import random
from enum import Enum
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email_validator import validate_email, EmailNotValidError


class Language(Enum):
    """Поддерживаемые языки"""
    RUSSIAN = "ru"
    ENGLISH = "en"


class EmailConfig:
    """Конфигурация для отправки email"""
    SMTP_SERVER = "connect.smtp.bz"
    SMTP_PORT = 2525
    FROM_EMAIL = "login@base-escape.ru"
    PASSWORD = "EXqwFGsx505!-"

    ACCENT_COLOR = "#00d9ff"
    ACCENT_DARK = "#00a8cc"
    BACKGROUND_COLOR = "#0a0e27"
    CARD_BACKGROUND = "#141829"
    CARD_BORDER = "#1f2937"
    TEXT_COLOR = "#ffffff"
    SECONDARY_TEXT_COLOR = "#8892b0"
    SUCCESS_COLOR = "#10b981"

    BOT_USERNAME = "plaza_support_BOT"


class EmailTexts:
    """Текстовые константы для разных языков"""
    MESSAGES = {
        Language.RUSSIAN: {
            "verification_code": "Код подтверждения",
            "enter_code": "Введите этот код для подтверждения email и завершения регистрации в Plaza",
            "open_bot": "Открыть бота",
            "subject": "Код подтверждения",
            "text_body_intro": "Код подтверждения:",
            "text_body_instruction": "Введите этот код для подтверждения email в Plaza.",
            "text_body_contact": "Есть вопросы? Напишите нам в Telegram:"
        },
        Language.ENGLISH: {
            "verification_code": "Verification Code",
            "enter_code": "Enter this code to verify your email and complete registration at Plaza",
            "open_bot": "Open Bot",
            "subject": "Verification Code",
            "text_body_intro": "Verification Code:",
            "text_body_instruction": "Enter this code to verify your email at Plaza.",
            "text_body_contact": "Questions? Message us on Telegram:"
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
        """Определяет язык по домену email (например, .ru для русского)

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
        """Генерирует HTML шаблон письма с улучшенным дизайном"""
        texts = {
            "verification_code": EmailTexts.get_text("verification_code", language),
            "enter_code": EmailTexts.get_text("enter_code", language),
            "open_bot": EmailTexts.get_text("open_bot", language),
        }

        return f"""
<!DOCTYPE html>
<html lang="{language.value}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{texts['verification_code']}</title>
    <style>
        @media (max-width: 600px) {{
            .card-padding {{ padding: 40px 20px !important; }}
            .code-display {{ font-size: 36px !important; letter-spacing: 6px !important; }}
        }}
    </style>
</head>
<body style="margin: 0; padding: 0; background: linear-gradient(135deg, {EmailConfig.BACKGROUND_COLOR} 0%, #0f1229 
100%); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif; min-height: 
100vh;">

    <!-- Main Container -->
    <table width="100%" cellpadding="0" cellspacing="0" style="background: linear-gradient(135deg, 
{EmailConfig.BACKGROUND_COLOR} 0%, #0f1229 100%); padding: 60px 20px;">
        <tr>
            <td align="center">
                <table width="100%" cellpadding="0" cellspacing="0" style="max-width: 520px;">

                    <!-- Logo/Header Section -->
                    <tr>
                        <td style="padding-bottom: 30px; text-align: center;">
                            <div style="font-size: 24px; font-weight: 700; color: 
{EmailConfig.ACCENT_COLOR}; letter-spacing: 2px;">
                                PLAZA
                            </div>
                        </td>
                    </tr>

                    <!-- Main Card with Border -->
                    <tr>
                        <td style="background-color: {EmailConfig.CARD_BACKGROUND}; border: 1px solid 
{EmailConfig.CARD_BORDER}; border-radius: 24px; padding: 70px 50px; text-align: center; 
box-shadow: 0 20px 60px rgba(0, 217, 255, 0.05);" class="card-padding">

                            <!-- Welcome Message -->
                            <div style="margin-bottom: 50px;">
                                <div style="font-size: 16px; color: 
{EmailConfig.TEXT_COLOR}; font-weight: 600; margin-bottom: 12px;">
                                    {texts['verification_code']}
                                </div>
                            </div>

                            <!-- Code Display with Accent Background -->
                            <div style="background: rgba(0, 217, 255, 0.08); 
                            border: 2px solid rgba(0, 217, 255, 0.2); border-radius: 16px; 
                            padding: 40px; margin-bottom: 50px;">
                                <div style="font-size: 14px; color: {EmailConfig.SECONDARY_TEXT_COLOR}; 
                                margin-bottom: 16px; text-transform: uppercase; letter-spacing: 2px; 
                                font-weight: 500;">
                                    {texts['verification_code']}
                                </div>
                                <div style="font-size: 52px; font-weight: 800; letter-spacing: 14px; 
                                color: {EmailConfig.ACCENT_COLOR}; 
                                font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 
                                monospace; word-break: break-all; line-height: 1.2;" class="code-display">
                                    {code}
                                </div>
                            </div>

                            <!-- Divider -->
                            <div style="height: 1px; 
                            background: linear-gradient(90deg, transparent, {EmailConfig.CARD_BORDER}, transparent);
                             margin: 40px 0;"></div>

                            <!-- Message -->
                            <div style="color: {EmailConfig.SECONDARY_TEXT_COLOR}; font-size: 15px; line-height: 1.7;
                             margin-bottom: 50px;">
                                {texts['enter_code']}
                            </div>

                            <!-- CTA Button -->
                            <table width="100%" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td align="center">
                                        <table cellpadding="0" cellspacing="0">
                                            <tr>
                                                <td style="background: linear-gradient(135deg, 
{EmailConfig.ACCENT_COLOR} 0%, {EmailConfig.ACCENT_DARK} 100%); border-radius: 12px; 
padding: 16px 48px; box-shadow: 0 10px 30px rgba(0, 217, 255, 0.2);">
                                                    <a href="https://t.me/{EmailConfig.BOT_USERNAME}" style="color: 
{EmailConfig.BACKGROUND_COLOR}; text-decoration: none; font-weight: 700; font-size: 15px; display: block;
 letter-spacing: 0.5px;">
                                                        → {texts['open_bot']}
                                                    </a>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>

                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="padding-top: 40px; text-align: center;">
                            <div style="font-size: 12px; color: {EmailConfig.SECONDARY_TEXT_COLOR}; line-height: 1.6;">
                                <p style="margin: 0 0 8px 0;">© 2025 Plaza. All rights reserved.</p>
                                <p style="margin: 0; opacity: 0.6;">This is an automated message. 
                                Please don't reply to this email.</p>
                            </div>
                        </td>
                    </tr>

                </table>
            </td>
        </tr>
    </table>

</body>
</html>
        """

    @staticmethod
    def send_email(to_email: str, code: str, language: Language):
        """Отправляет email с кодом подтверждения

        Args:
            to_email: Email адрес получателя
            code: Код подтверждения
            language: Язык письма
        """
        msg = MIMEMultipart("alternative")
        msg["From"] = EmailConfig.FROM_EMAIL
        msg["To"] = to_email
        msg["Subject"] = EmailTexts.get_text("subject", language)
        msg["Content-Language"] = language.value

        text_body = f"""
{EmailTexts.get_text('text_body_intro', language)} {code}

{EmailTexts.get_text('text_body_instruction', language)}

{EmailTexts.get_text('text_body_contact', language)} @{EmailConfig.BOT_USERNAME}
        """

        html_body = Email._get_html_template(code, language)

        part1 = MIMEText(text_body, "plain", "utf-8")
        part2 = MIMEText(html_body, "html", "utf-8")

        msg.attach(part1)
        msg.attach(part2)

        try:
            with smtplib.SMTP(EmailConfig.SMTP_SERVER, EmailConfig.SMTP_PORT) as server:
                server.starttls()
                server.login(EmailConfig.FROM_EMAIL, EmailConfig.PASSWORD)
                server.sendmail(EmailConfig.FROM_EMAIL, to_email, msg.as_string())
            print(f"✓ Email sent successfully to {to_email} [{language.value.upper()}]")
            return True
        except Exception as e:
            print(f"✗ Error sending email: {e}")
            raise

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Проверяет валидность email адреса"""
        try:
            validate_email(email)
            return True
        except EmailNotValidError:
            return False

    @staticmethod
    def get_email_code() -> str:
        """Генерирует 6-значный код подтверждения"""
        return ''.join(str(random.randint(0, 9)) for _ in range(6))
