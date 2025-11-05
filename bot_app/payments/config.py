RETURN_URL = "https://t.me/PlazaCasinoBOT"

YOOKASSA_SHOP_ID = "423276"
YOOKASSA_SECRET_KEY = "live_0UTHY-O3nKsspMU0weMF7go_XpBpcp9xa8exJ2PPBC0"
YOOKASSA_WEBHOOK_URL = "https://njui7w-195-128-153-209.ru.tuna.am/payment/yookassa/webhook"

CONFIG = {
    "yookassa": {
        "enabled": True,
        "account_id": YOOKASSA_SHOP_ID,
        "secret_key": YOOKASSA_SECRET_KEY,
        "return_url": RETURN_URL,
        "webhook_url": YOOKASSA_WEBHOOK_URL,
        "receipt_vat_code": 1
    },
    # TODO: Добавить конфигурацию для других провайдеров
}
