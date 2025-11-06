import os

RETURN_URL = os.getenv("RETURN_URL")

YOOKASSA_SHOP_ID = os.getenv("YOOKASSA_SHOP_ID")
YOOKASSA_SECRET_KEY = os.getenv("YOOKASSA_SECRET_KEY")
YOOKASSA_WEBHOOK_URL =  os.getenv("YOOKASSA_WEBHOOK_URL")

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
