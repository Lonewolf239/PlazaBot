class TransactionStatus:
    # Пополнения
    PENDING_PAYMENT_INIT = "pending_payment_init"
    PENDING_PAYMENT_CONFIRMATION = "pending_payment_confirmation"
    DEPOSIT_SUCCEEDED = "deposit_succeeded"
    DEPOSIT_FAILED = "deposit_failed"
    DEPOSIT_CANCELED = "deposit_canceled"
    DEPOSIT_REFUNDED = "deposit_refunded"
    PAYMENT_CANCELED = "payment_canceled"

    # Выводы
    PENDING_WITHDRAWAL_INIT = "pending_withdrawal_init"
    PENDING_WITHDRAWAL_REVIEW = "pending_withdrawal_review"
    WITHDRAWAL_SUCCEEDED = "withdrawal_succeeded"
    WITHDRAWAL_FAILED = "withdrawal_failed"
    WITHDRAWAL_CANCELED = "withdrawal_canceled"

    # Статусы для внутренних транзакций (не зависят от провайдера)
    INTERNAL_PENDING = "internal_pending"
    INTERNAL_COMPLETED = "internal_completed"
    INTERNAL_FAILED = "internal_failed"
    INTERNAL_ERROR = "internal_error"
