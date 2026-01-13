# valutatrade_hub/infra/database.py

import json
import os
from typing import Any, Dict, List

from valutatrade_hub.core.models import Portfolio, User

from .settings import SettingsLoader


class DatabaseManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance.settings = SettingsLoader()
        return cls._instance

    def _read_json(self, path: str) -> Any:
        """
        Функция для чтения json файла

        Параметры:
            path - строка, содержит путь к файлу
        """
        if not os.path.exists(path):
            return [] if "users" in path or "portfolios" in path else {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []

    def _write_json(self, path: str, data: Any):
        """
        Функция для записи данных в json файл

        Параметры:
            path - строка, содержит путь к файлу
            data - содержит данные для записи
        """
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_users(self) -> List[User]:
        """
        Функция для выгрузки данных о пользователях из json файла
        """
        data = self._read_json(self.settings.get("users_file"))
        return [User.from_dict(d) for d in data]

    def save_user(self, user: User):
        """
        Функция для загрузки данных о пользователе в json файл
        """
        users = self.load_users()
        users.append(user)
        self._write_json(self.settings.get("users_file"), [u.to_dict() for u in users])

    def get_user_by_username(self, username: str) -> User:
        """
        Функция для поиска пользователя по имени

        Параметры:
            username - строка, содержит имя пользователя
        """
        users = self.load_users()
        for u in users:
            if u.username == username:
                return u
        return None
    
    def get_max_user_id(self) -> int:
        """
        Функция для получения максимального id пользователя
        """
        users = self.load_users()
        if not users:
            return 0
        return max(u.user_id for u in users)

    def load_portfolios(self) -> List[Portfolio]:
        """
        Функция для выгрузки информации о портфелях из json файла
        """
        data = self._read_json(self.settings.get("portfolios_file"))
        return [Portfolio.from_dict(d) for d in data]

    def get_portfolio(self, user_id: int) -> Portfolio:
        """
        Функция для поиска портфеля по id пользователя

        Параметры:
            user_id - целое число, id пользователя
        """
        portfolios = self.load_portfolios()
        for p in portfolios:
            if p.user_id == user_id:
                return p
        return None

    def save_portfolio(self, portfolio: Portfolio):
        """
        Функция для загрузки информации о портфеле в json файла
        """
        portfolios = self.load_portfolios()
        for i, p in enumerate(portfolios):
            if p.user_id == portfolio.user_id:
                portfolios[i] = portfolio
                break
        else:
            portfolios.append(portfolio)
        
        self._write_json(self.settings.get("portfolios_file"), \
            [p.to_dict() for p in portfolios])

    def load_rates(self) -> Dict:
        """
        Функция для выгрузки информации о курсах валют из json файла
        """
        data = self._read_json(self.settings.get("rates_file"))
        return data.get("pairs", {}) if isinstance(data, dict) else {}
    
    def load_full_rates_data(self) -> Dict:
        """
        Функция для выгрузки полной информации о курсах валют из json файла
        """
        return self._read_json(self.settings.get("rates_file")) or {}

    def save_rates(self, data: Dict):
        """
        Функция для загрузки информации о курсе валюты в json файл
        """
        self._write_json(self.settings.get("rates_file"), data)