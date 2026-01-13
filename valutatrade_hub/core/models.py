# valutatrade_hub/core/models.py

import hashlib
import secrets
from datetime import datetime
from typing import Dict

from .exceptions import InsufficientFundsError


class User:
    """
    Класс Пользователь
    """
    def __init__(self, user_id: int, username: str, password: str = None, 
                 hashed_password: str = None, salt: str = None, 
                 registration_date: datetime = None):
        self._user_id = user_id
        self.username = username
        if password:
            self.salt = self._generate_salt()
            self._hashed_password = self._hash_password(password, self.salt)
        elif hashed_password and salt:
            self._hashed_password = hashed_password
            self._salt = salt
        self._registration_date = registration_date or datetime.now()
    
    @property
    def user_id(self) -> int:
        """Геттер для id пользователя"""
        return self._user_id
    
    @property
    def username(self) -> str:
        """Геттер для username"""
        return self._username   
    
    @username.setter
    def username(self, value: str):
        """Сеттер для username с проверкой"""
        if not value or not value.strip():
            raise ValueError("Имя пользователя не может быть пустым")
        self._username = value.strip()    
    
    @property
    def salt(self) -> str:
        """Геттер для salt"""
        return self._salt   
    
    @salt.setter
    def salt(self, value: str):
        """Сеттер для salt"""
        self._salt = value
        
    @property
    def registration_date(self) -> datetime:
        """Геттер для registration_date"""
        return self._registration_date

    def _generate_salt(self, length: int = 8) -> str:
        """
        Функция для генерации случайной соли
        
        Параметры:
            length - целое число, содержит длину соли
        """
        return secrets.token_hex(length // 2)

    def _hash_password(self, password: str, salt: str) -> str:
        """
        Функция для хеширования пароля с солью
        
        Параметры:
            password - строка, содержит пароль пользователя
            salt - строка, содержит соль
        """
        if len(password) < 4:
            raise ValueError("Пароль должен быть не короче 4 символов")
        return hashlib.sha256((password+salt).encode()).hexdigest()

    def get_user_info(self) -> dict:
        """Возвращает информацию о пользователе"""
        return {
            "user_id": self._user_id,
            "username": self._username,
            "registration_date": self._registration_date.isoformat()
        }

    def change_password(self, new_password: str) -> None:
        """
        Функция для смены пароля пользователя
        
        Параметры:
            new_password - строка, содержит новый пароль пользователя
        """
        new_hashed_password = self._hash_password(new_password, self._salt)
        self._hashed_password = new_hashed_password
    
    def verify_password(self, password: str) -> bool:
        """
        Функция для проверки введенного пользователем пароля
        
        Параметры:
            password - строка, содержит пароль пользователя
        """
        return hashlib.sha256((password + self._salt).encode()).hexdigest() == \
             self._hashed_password
    
    def to_dict(self) -> dict:
        """Возвращает информацию о пользвателе в виде словаря"""
        return {
            "user_id": self._user_id,
            "username": self._username,
            "hashed_password": self._hashed_password,
            "salt": self._salt,
            "registration_date": self._registration_date.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """
        Преобразует словарь в элемент класса
        
        Параметры:
            data - словарь, содержит информацию о пользователе
        """
        return cls(
            user_id=data["user_id"],
            username=data["username"],
            hashed_password=data["hashed_password"],
            salt=data["salt"],
            registration_date=datetime.fromisoformat(data["registration_date"])
        )

class Wallet:
    """
    Класс Кошелек
    """
    def __init__(self, currency_code: str, balance: float = 0.0):
        self.currency_code = currency_code
        self.balance = balance

    @property
    def balance(self) -> float:
        """Геттер для баланса"""
        return self._balance

    @balance.setter
    def balance(self, value: float):
        """
        Сеттер для баланса
        
        Параметры:
            value - вещественное число, содержит сумму баланса
        """
        if not isinstance(value, (int, float)):
            raise ValueError("Баланс должен быть числом")
        if value < 0:
            raise ValueError("Баланс не может быть отрицательным")
        self._balance = float(value)

    def deposit(self, amount: float):
        """
        Функция для внесения средств на кошелек
        
        Параметры:
            amount - вещественное число, содержит сумму пополнения
        """
        if amount <= 0:
            raise ValueError("Сумма пополнения должна быть положительной")
        self.balance += amount

    def withdraw(self, amount: float):
        """
        Функция для снятия средств с кошелька
        
        Параметры:
            amount - вещественное число, содержит сумму снятия
        """
        if amount <= 0:
            raise ValueError("Сумма снятия должна быть положительной")
        if amount > self.balance:
            raise InsufficientFundsError(self.balance, amount, self.currency_code)
        self.balance -= amount

    def get_balance_info(self) -> str:
        """Возвращает информацию о балансе кошелька"""
        return f"{self.currency_code}: {self.balance:.4f}"

    def to_dict(self) -> dict:
        """Преобразует информацию о кошельке в словарь"""
        return {"currency_code": self.currency_code, "balance": self.balance}

    @classmethod
    def from_dict(cls, data: dict) -> 'Wallet':
        """Преобразует словарь в элемент класса"""
        return cls(currency_code=data["currency_code"], balance=data["balance"])

class Portfolio:
    """
    Класс Портфель
    """
    def __init__(self, user_id: int, wallets: Dict[str, Wallet] = None):
        self._user_id = user_id
        self._wallets = wallets if wallets else {}

    @property
    def user_id(self) -> int:
        """Геттер для id пользователя"""
        return self._user_id

    @property
    def wallets(self) -> Dict[str, Wallet]:
        """Геттер для кошельков пользователя"""
        return self._wallets.copy()

    def add_currency(self, currency_code: str) -> None:
        """
        Функция добавления кошелька в портфель

        Параметры:
            currency_code - строка, содержит валюту создаваемого кошелька
        """
        if currency_code in self._wallets:
            return
        self._wallets[currency_code] = Wallet(currency_code)

    def get_wallet(self, currency_code: str) -> Wallet:
        """
        Возвращает кошелек по коду валюты

        Параметры:
            currency_code - строка, содержит код валюты
        """
        return self._wallets.get(currency_code)

    def get_total_value(self, rates_data: dict, base_currency: str = 'USD') -> float:
        """
        Функция для получения общей суммы портфеля

        Параметры:
            rates_data - словарь, содержит информацию о курсах валют
            base_currency - строка, содержит валюту, в которой будет произведен расчет
        """
        total = 0.0
        
        for code, wallet in self._wallets.items():
            amount = wallet.balance
            
            if code == base_currency:
                total += amount
                continue
            
            direct_pair = f"{code}_{base_currency}"
            if direct_pair in rates_data:
                total += amount * rates_data[direct_pair]['rate']
                continue

            reverse_pair = f"{base_currency}_{code}"
            if reverse_pair in rates_data:
                total += amount * (1.0 / rates_data[reverse_pair]['rate'])
                continue

            pair_src_usd = f"{code}_USD"
            pair_dst_usd = f"{base_currency}_USD"
            
            if pair_src_usd in rates_data and pair_dst_usd in rates_data:
                rate_src = rates_data[pair_src_usd]['rate']
                rate_dst = rates_data[pair_dst_usd]['rate']
                if rate_dst != 0:
                    cross_rate = rate_src / rate_dst
                    total += amount * cross_rate
                continue
        return total

    def to_dict(self) -> dict:
        """Возвращает элемент класса в виде словаря"""
        return {
            "user_id": self._user_id,
            "wallets": {k: v.to_dict() for k, v in self._wallets.items()}
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Portfolio':
        """Преобразует словарь в элемент класса"""
        wallets = {k: Wallet.from_dict(v) for k, v in data["wallets"].items()}
        return cls(user_id=data["user_id"], wallets=wallets)