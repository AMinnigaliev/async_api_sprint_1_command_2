class BaseServiceError(Exception):
    """Базовое исключение для всех ошибок сервиса."""
    pass


class TokenServiceError(BaseServiceError):
    """Исключение для ошибок, связанных с access-токен."""
    pass
