# valutatrade_hub/core/exceptions.py

class InsufficientFundsError(Exception):
    """
    Исключение на недостаток средств
    """
    def __init__(self, available: float, required: float, code: str):
        self.message = (f"Недостаточно средств: доступно {available:.4f} "
            f"{code}, требуется {required:.4f} {code}")
        super().__init__(self.message)
    def __str__(self): return self.message

class CurrencyNotFoundError(Exception):
    """
    Исключение на ошибку поиска валюты
    """
    def __init__(self, code: str):
        self.message = f"Неизвестная валюта '{code}'"
        super().__init__(self.message)
    def __str__(self): return self.message

class ApiRequestError(Exception):
    """
    Исключение на ошибку, связанную с API
    """
    def __init__(self, reason: str):
        self.message = f"Ошибка при обращении к внешнему API: {reason}"
        super().__init__(self.message)
    def __str__(self): return self.message

class UserNotFoundError(Exception):
    """
    Исключение на ошибку поиска пользователя
    """
    def __init__(self, message="Пользователь не найден"):
        self.message = message
        super().__init__(self.message)
    def __str__(self): return self.message

class AuthenticationError(Exception):
    """
    Исключение на ошибку входа в аккаунт пользователя
    """
    def __init__(self, message="Ошибка аутентификации"):
        self.message = message
        super().__init__(self.message)
    def __str__(self): return self.message