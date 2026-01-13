# valutatrade_hub/parser_service/api_clients.py

from abc import ABC, abstractmethod
from typing import Dict

import requests

from ..core.exceptions import ApiRequestError
from .config import ParserConfig


class BaseApiClient(ABC):
    @abstractmethod
    def fetch_rates(self) -> Dict[str, float]:
        pass

class CoinGeckoClient(BaseApiClient):
    """
    Класс для работы с CoinGecko
    """
    def fetch_rates(self) -> Dict[str, float]:
        """
        Функция для запроса курсов валют по API
        """
        ids = list(ParserConfig.CRYPTO_ID_MAP.values())
        ids_str = ",".join(ids)
        params = {
            "ids": ids_str,
            "vs_currencies": ParserConfig.BASE_CURRENCY.lower()
        }
        try:
            response = requests.get(
                ParserConfig.COINGECKO_URL, 
                params=params, 
                timeout=ParserConfig.REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            rates = {}
            id_to_ticker = {v: k for k, v in ParserConfig.CRYPTO_ID_MAP.items()}
            
            for coin_id, prices in data.items():
                if coin_id in id_to_ticker:
                    ticker = id_to_ticker[coin_id]
                    price = prices.get(ParserConfig.BASE_CURRENCY.lower())
                    if price:
                        pair_name = f"{ticker}_{ParserConfig.BASE_CURRENCY}"
                        rates[pair_name] = float(price)
            return rates
        except requests.RequestException as e:
            raise ApiRequestError(f"CoinGecko error: {e}")

class ExchangeRateApiClient(BaseApiClient):
    """
    Класс для работы с ExchangeRate
    """
    def fetch_rates(self) -> Dict[str, float]:
        """
        Функция для запроса курсов валют по API
        """
        key = ParserConfig.EXCHANGERATE_API_KEY
        if not key:
            return {}
            
        url = (f"{ParserConfig.EXCHANGERATE_API_URL}/{key}/latest/"
            f"{ParserConfig.BASE_CURRENCY}")

        try:
            response = requests.get(url, timeout=ParserConfig.REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            if data.get("result") != "success":
                raise ApiRequestError(f"API Error: {data.get('error-type')}")
                
            rates = {}
            api_rates = data.get("conversion_rates", {})

            for code in ParserConfig.FIAT_CURRENCIES:
                if code in api_rates:
                    pair_name = f"{code}_{ParserConfig.BASE_CURRENCY}"
                    val = float(api_rates[code])
                    if val != 0:
                        rates[pair_name] = 1.0 / val
            return rates
        except requests.RequestException as e:
            raise ApiRequestError(f"ExchangeRate-API error: {e}")