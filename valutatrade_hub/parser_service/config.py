# valutatrade_hub/parser_service/config.py

import os
from dataclasses import dataclass


@dataclass
class ParserConfig:
    """
    Класс для параметров парсера
    """
    os.environ['EXCHANGERATE_API_KEY'] = ""
    EXCHANGERATE_API_KEY: str = os.getenv("EXCHANGERATE_API_KEY", "") 
    
    COINGECKO_URL: str = "https://api.coingecko.com/api/v3/simple/price"
    EXCHANGERATE_API_URL: str = "https://v6.exchangerate-api.com/v6"
    
    BASE_CURRENCY: str = "USD"
    FIAT_CURRENCIES = ["EUR", "GBP", "RUB", "JPY", "CNY"]
    CRYPTO_CURRENCIES = ["BTC", "ETH", "SOL"]

    CRYPTO_ID_MAP = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "SOL": "solana",
    }
    REQUEST_TIMEOUT: int = 10
    

    