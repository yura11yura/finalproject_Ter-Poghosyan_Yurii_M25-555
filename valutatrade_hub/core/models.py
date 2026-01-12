# valutatrade_hub/core/models.py

import hashlib
import secrets
from datetime import datetime
from typing import Dict

EXCHANGE_RATES = {
    'USD': 1.0,
    'EUR': 0.851,
    'BTC': 0.000011,
    'ETH': 0.00034, 
    'RUB': 78.23,
}

class User:
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
        return self._user_id
    
    @property
    def username(self) -> str:
        return self._username
    
    @username.setter
    def username(self, value: str):
        if not value or not value.strip():
            raise ValueError("Имя пользователя не может быть пустым")
        self._username = value.strip()
    
    @property
    def salt(self) -> str:
        return self._salt
    
    @salt.setter
    def salt(self, value: str):
        self._salt = value
    
    @property
    def registration_date(self) -> datetime:
        return self._registration_date
    
    def _generate_salt(self, length: int = 8) -> str:
        return secrets.token_hex(length // 2)
    
    def _hash_password(self, password: str, salt: str) -> str:
        if len(password) < 4:
            raise ValueError("Пароль должен быть не короче 4 символов")
        
        return hashlib.sha256((password+salt).encode()).hexdigest()
    
    def get_user_info(self) -> dict:
        return {
            "user_id": self._user_id,
            "username": self._username,
            "registration_date": self._registration_date.isoformat()
        }
    
    def change_password(self, new_password: str) -> None:
        new_hashed_password = self._hash_password(new_password, self._salt)
        
        self._hashed_password = new_hashed_password
    
    def verify_password(self, password: str) -> bool:
        return hashlib.sha256((password + self._salt).encode()).hexdigest() == self._hashed_password
    
    def to_dict(self) -> dict:
        return {
            "user_id": self._user_id,
            "username": self._username,
            "hashed_password": self._hashed_password,
            "salt": self._salt,
            "registration_date": self._registration_date.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        return cls(
            user_id=data["user_id"],
            username=data["username"],
            hashed_password=data["hashed_password"],
            salt=data["salt"],
            registration_date=datetime.fromisoformat(data["registration_date"])
        )
    
class Wallet:
    def __init__(self, currency_code: str, balance: float = 0.0):
        self.currency_code = currency_code
        self._balance = float(balance)
    
    @property
    def currency_code(self) -> str:
        return self._currency_code
    
    @currency_code.setter
    def currency_code(self, value: str):
        if not value or not isinstance(value, str):
            raise ValueError("Код валюты должен быть непустой строкой")
        if len(value.strip()) == 0:
            raise ValueError("Код валюты не может быть пустым")
        self._currency_code = value.strip().upper()
    
    @property
    def balance(self) -> float:
        return self._balance
    
    @balance.setter
    def balance(self, value: float):
        try:
            float_value = float(value)
        except (ValueError, TypeError):
            raise ValueError("Баланс должен быть числом")
        
        if float_value < 0:
            raise ValueError("Баланс не может быть отрицательным")
        
        self._balance = float_value
    
    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Сумма пополнения должна быть положительной")
        try:
            amount_float = float(amount)
        except (ValueError, TypeError):
            raise ValueError("Сумма должна быть числом")
        
        self.balance = self._balance + amount_float
    
    def withdraw(self, amount: float) -> bool:
        if amount <= 0:
            raise ValueError("Сумма снятия должна быть положительной")
        
        try:
            amount_float = float(amount)
        except (ValueError, TypeError):
            raise ValueError("Сумма должна быть числом")
        
        if amount_float > self._balance:
            raise ValueError("Недостаточно средств на счету")
        
        self.balance = self._balance - amount_float
    
    def get_balance_info(self) -> str:
        return f"Кошелёк {self._currency_code}: {self._balance:.2f}"
    
    def to_dict(self) -> dict:
        return {
            "currency_code": self._currency_code,
            "balance": self._balance
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Wallet':
        return cls(
            currency_code=data["currency_code"],
            balance=data["balance"]
        )

class Portfolio:
    def __init__(self, user_id: int, wallets: Dict[str, Wallet] = None):
        self._user_id = user_id
        self._wallets = wallets if wallets is not None else {}
    
    @property
    def user(self):
        return self._user_id
    
    @property
    def wallets(self) -> Dict[str, Wallet]:
        return self._wallets.copy()
    
    def add_currency(self, currency_code: str) -> None:
        currency_code = currency_code.strip().upper()
        
        if currency_code in self._wallets:
            raise ValueError(f"Кошелёк с валютой '{currency_code}' уже существует в портфеле")
        
        self._wallets[currency_code] = Wallet(currency_code, 0.0)
    
    def get_total_value(self, base_currency: str = 'USD') -> float:
        
        if base_currency not in EXCHANGE_RATES:
            raise ValueError(f"Неизвестная базовая валюта '{base_currency}'")
        
        total_value = 0.0
        
        for currency_code, wallet in self._wallets.items():
            if currency_code == base_currency:
                total_value += wallet.balance
                continue
            
            if currency_code not in EXCHANGE_RATES:
                print(f"Курс валюты '{currency_code}' не найден.")
                continue
            
            if base_currency == 'USD':
                rate_to_usd = 1 / EXCHANGE_RATES[currency_code]
                value_in_base = wallet.balance * rate_to_usd
            else:
                rate_to_usd = 1 / EXCHANGE_RATES[currency_code]
                value_in_usd = wallet.balance * rate_to_usd
                value_in_base = value_in_usd * EXCHANGE_RATES[base_currency]
            
            total_value += value_in_base
        
        return total_value
    
    def get_wallet(self, currency_code: str) -> Wallet:
        currency_code = currency_code.strip().upper()
        
        if currency_code not in self._wallets:
            raise KeyError(f"Кошелёк с валютой '{currency_code}' не найден в портфеле")
        
        return self._wallets[currency_code]
    
    def to_dict(self) -> dict:
        return {
            "user_id": self._user_id,
            "wallets": {currency: wallet.to_dict() for currency, wallet in self._wallets.items()}
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Portfolio':
        wallets = {}
        
        for currency_code, wallet_data in data.get("wallets", {}).items():
            wallets[currency_code] = Wallet.from_dict(wallet_data)
        
        return cls(
            user_id=data["user_id"],
            wallets=wallets
        )