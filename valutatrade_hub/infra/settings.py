# valutatrade_hub/infra/settings.py

import os
from typing import Any

DEFAULT_CONFIG = {
    "data_dir": "data",
    "users_file": "data/users.json",
    "portfolios_file": "data/portfolios.json",
    "rates_file": "data/rates.json",
    "exchange_rates_file": "data/exchange_rates.json",
    "rates_ttl": 20,
    "base_currency": "USD",
    "log_level": "INFO",
    "HISTORY_FILE_PATH": "data/exchange_rates.json",
}

class SettingsLoader:
    _instance = None
    _config = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SettingsLoader, cls).__new__(cls)
            cls._instance._load()
        return cls._instance

    def _load(self):
        """
        Функция для загрузки конфигурации из json файла и переменной окружения
        """
        self._config = DEFAULT_CONFIG

    def get(self, key: str, default: Any = None) -> Any:
        """
        Функция для получения настройки по названию

        Параметры:
            key - строка, содержит название настройки
        """
        if key in self._config:
            return self._config[key]
        return os.environ.get(key, default)

    def reload(self):
        """
        Функция для перезагрузки настроек
        """
        self._load()