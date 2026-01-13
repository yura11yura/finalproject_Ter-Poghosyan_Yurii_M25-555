# valutatrade_hub/core/currencies.py

from abc import ABC, abstractmethod

from .exceptions import CurrencyNotFoundError


class Currency(ABC):
    def __init__(self, code: str, name: str):
        self.code = code
        self.name = name

    @abstractmethod
    def get_display_info(self) -> str:
        pass

class FiatCurrency(Currency):
    """
    Класс фиатной валюты
    """
    def __init__(self, code: str, name: str, issuing_country: str):
        super().__init__(code, name)
        self.issuing_country = issuing_country

    def get_display_info(self) -> str:
        """
        Функция для вывода элемента класса
        """
        return f"[FIAT] {self.code} — {self.name} (Issuing: {self.issuing_country})"

class CryptoCurrency(Currency):
    """
    Класс криптовалюты
    """
    def __init__(self, code: str, name: str, algorithm: str, market_cap: float = 0.0):
        super().__init__(code, name)
        self.algorithm = algorithm
        self.market_cap = market_cap

    def get_display_info(self) -> str:
        """
        Функция для вывода элемента класса
        """
        return (f"[CRYPTO] {self.code} — {self.name} (Algo: {self.algorithm}, "
            f"MCAP: {self.market_cap})")

_REGISTRY = {
    "USD": FiatCurrency("USD", "US Dollar", "United States"),
    "EUR": FiatCurrency("EUR", "Euro", "Eurozone"),
    "GBP": FiatCurrency("GBP", "British Pound", "United Kingdom"),
    "RUB": FiatCurrency("RUB", "Russian Ruble", "Russia"),
    "BTC": CryptoCurrency("BTC", "Bitcoin", "SHA-256", 1.12e12),
    "ETH": CryptoCurrency("ETH", "Ethereum", "Ethash", 400e9),
    "SOL": CryptoCurrency("SOL", "Solana", "PoH", 60e9)
}

def get_currency(code: str) -> Currency:
    """
    Функция для получения валюты по коду

    Параметры:
        code - строка, содержит код валюты
    """
    if not code or code.upper() not in _REGISTRY:
        raise CurrencyNotFoundError(code)
    return _REGISTRY[code.upper()]