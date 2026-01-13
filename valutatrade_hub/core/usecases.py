# valutatrade_hub/core/usecases.py

from datetime import datetime, timedelta
from typing import Tuple

from valutatrade_hub.decorators import log_action
from valutatrade_hub.infra.database import DatabaseManager
from valutatrade_hub.infra.settings import SettingsLoader
from valutatrade_hub.parser_service.updater import RatesUpdater

from .currencies import get_currency
from .exceptions import (
    ApiRequestError,
    AuthenticationError,
    CurrencyNotFoundError,
    InsufficientFundsError,
    UserNotFoundError,
)
from .models import Portfolio, User


class UseCases:
    def __init__(self):
        self.db = DatabaseManager()
        self.settings = SettingsLoader()
        self.current_user: User = None
        self.updater = RatesUpdater()

    def _check_auth(self):
        """
        Функция проверки, что был выполнен вход

        Возвращает элемент User
        """
        if not self.current_user:
            raise AuthenticationError("Сначала выполните login")
        return self.current_user

    @log_action
    def register(self, username: str, password: str) -> str:
        """
        Функция для регистрации пользователя

        Параметры:
            username - строка, содержит имя пользователя
            password - строка, содержит пароль пользователя

        Возвращает сообщение
        """
        if self.db.get_user_by_username(username):
            raise ValueError(f"Имя пользователя '{username}' уже занято")
        
        new_id = self.db.get_max_user_id() + 1
        user = User(user_id=new_id, username=username, password=password)
        
        self.db.save_user(user)
        
        portfolio = Portfolio(user_id=new_id)
        self.db.save_portfolio(portfolio)
        
        return (f"Пользователь '{username}' зарегистрирован (id={new_id}). "
            "Войдите в систему.")

    @log_action
    def login(self, username: str, password: str) -> str:
        """
        Функция для входа в аккаунт пользователя

        Параметры:
            username - строка, содержит имя пользователя
            password - строка, содержит пароль пользователя

        Возвращает сообщение
        """
        user = self.db.get_user_by_username(username)
        if not user:
            raise UserNotFoundError(f"Пользователь '{username}' не найден")
        
        if user.verify_password(password):
            self.current_user = user
            return f"Вы вошли как '{username}'"
        else:
            raise AuthenticationError("Неверный пароль")

    @log_action
    def logout(self) -> str:
        """
        Функция для выхода из аккаунта

        Возвращает сообщение
        """
        if self.current_user:
            name = self.current_user.username
            self.current_user = None
            return f"Пользователь '{name}' вышел из системы."
        return "Вы не были залогинены."

    def _get_rate_value(self, from_curr: str, to_curr: str) -> float:
        """
        Функция для получения курса валют

        Параметры:
            from_curr - строка, содержит валюту, из которой происходит перевод
            to_curr - строка, соедржит валюту, в которую происходит перевод

        Возвращает искомый курс
        """
        if from_curr == to_curr:
            return 1.0
        
        rates = self.db.load_rates()
        
        direct_pair = f"{from_curr}_{to_curr}"
        if direct_pair in rates:
            return rates[direct_pair]["rate"]
        
        reverse_pair = f"{to_curr}_{from_curr}"
        if reverse_pair in rates:
            return 1.0 / rates[reverse_pair]["rate"]
        
        pair_a_usd = f"{from_curr}_USD"
        pair_b_usd = f"{to_curr}_USD"
        
        if pair_a_usd in rates and pair_b_usd in rates:
            rate_a = rates[pair_a_usd]["rate"]
            rate_b = rates[pair_b_usd]["rate"]
            if rate_b == 0:
                raise ApiRequestError(f"Ошибка кросс-курса: курс {to_curr} равен 0")
            return rate_a / rate_b
            
        raise ApiRequestError(f"Нет данных о курсе {from_curr} -> {to_curr}")

    def get_rate(self, from_curr: str, to_curr: str) -> Tuple[bool, str]:
        """
        Функция для вывода перевода курсов валют

        Параметры:
            from_curr - строка, содержит валюту, из которой происходит перевод
            to_curr - строка, соедржит валюту, в которую происходит перевод

        Возвращает сообщение
        """
        try:
            get_currency(from_curr)
            get_currency(to_curr)
            
            rates_data = self.db.load_full_rates_data()
            last_refresh_str = rates_data.get("last_refresh")
            ttl = self.settings.get("rates_ttl", 300)

            is_stale = False
            updated_at_display = "N/A"
            
            if last_refresh_str:
                last_refresh = datetime.fromisoformat(last_refresh_str)
                updated_at_display = last_refresh_str
                if datetime.now() - last_refresh > timedelta(seconds=ttl):
                    is_stale = True
            else:
                is_stale = True
            
            warning_msg = ""
            if is_stale:
                warning_msg = " (!) Данные устарели, выполните update-rates"
            
            rate_val = self._get_rate_value(from_curr, to_curr)
            
            return True, (f"Курс {from_curr}→{to_curr}: {rate_val:.8f} (обновлено: "
                f"{updated_at_display}){warning_msg}")
        
        except CurrencyNotFoundError as e:
            return False, str(e)
        except ApiRequestError as e:
            return False, f"Курс не найден ({e})"
        except Exception as e:
            return False, f"Ошибка получения курса: {e}"

    @log_action
    def buy(self, currency_code: str, amount: float) -> str:
        """
        Функция для выполнения операции покупки валюты

        Параметры:
            currency_code - строка, содержит код валюты
            amount - вещественное число, соедржит сумму покупки

        Возвращает сообщение
        """
        user = self._check_auth()
        if amount <= 0:
            raise ValueError("Сумма должна быть положительной")
        
        curr_obj = get_currency(currency_code)
        code = curr_obj.code
        
        portfolio = self.db.get_portfolio(user.user_id)
        
        if code == "USD":
            if not portfolio.get_wallet("USD"):
                portfolio.add_currency("USD")
            
            usd_wallet = portfolio.get_wallet("USD")
            usd_wallet.deposit(amount)
            self.db.save_portfolio(portfolio)
            
            return (f"Баланс пополнен: +{amount:.2f} USD\n"
                    f"Текущий баланс USD: {usd_wallet.balance:.2f}")

        try:
            rate = self._get_rate_value(code, "USD") 
        except ApiRequestError:
            raise ApiRequestError(f"Невозможно купить {code}: нет курса к USD")

        total_cost_usd = amount * rate

        usd_wallet = portfolio.get_wallet("USD")
        if not usd_wallet:
            raise InsufficientFundsError(0, total_cost_usd, "USD")
        
        if usd_wallet.balance < total_cost_usd:
            raise InsufficientFundsError(usd_wallet.balance, total_cost_usd, "USD")

        if not portfolio.get_wallet(code):
            portfolio.add_currency(code)
        target_wallet = portfolio.get_wallet(code)

        usd_old = usd_wallet.balance
        target_old = target_wallet.balance

        usd_wallet.withdraw(total_cost_usd)
        target_wallet.deposit(amount)
        
        self.db.save_portfolio(portfolio)
        
        return (f"Покупка выполнена: {amount:.4f} {code} за "
            f"{total_cost_usd:.2f} USD\n"
                f"Курс сделки: {rate:.4f} USD/{code}\n"
                f"Изменения:\n"
                f"- USD: {usd_old:.2f} → {usd_wallet.balance:.2f}\n"
                f"- {code}: {target_old:.4f} → {target_wallet.balance:.4f}")

    @log_action
    def sell(self, currency_code: str, amount: float) -> str:
        """
        Функция для выполнения операции продажи валют

        Параметры:
            currency_code - строка, содержит код валюты
            amount - вещественное число, соедржит сумму покупки

        Возвращает сообщение
        """
        user = self._check_auth()
        if amount <= 0:
            raise ValueError("Сумма должна быть положительной")
        
        curr_obj = get_currency(currency_code)
        code = curr_obj.code
        
        portfolio = self.db.get_portfolio(user.user_id)
        
        if code == "USD":
            usd_wallet = portfolio.get_wallet("USD")
            if not usd_wallet:
                raise InsufficientFundsError(0, amount, "USD")
            usd_wallet.withdraw(amount)
            self.db.save_portfolio(portfolio)
            
            return (f"Средства выведены: -{amount:.2f} USD\n"
                    f"Текущий баланс USD: {usd_wallet.balance:.2f}")
        target_wallet = portfolio.get_wallet(code)
        if not target_wallet:
            raise InsufficientFundsError(0, amount, code)

        try:
            rate = self._get_rate_value(code, "USD")
        except ApiRequestError:
            raise ApiRequestError(f"Невозможно продать {code}: нет курса к USD")
            
        total_revenue_usd = amount * rate

        target_old = target_wallet.balance
        target_wallet.withdraw(amount)

        if not portfolio.get_wallet("USD"):
            portfolio.add_currency("USD")
        usd_wallet = portfolio.get_wallet("USD")
        
        usd_old = usd_wallet.balance
        usd_wallet.deposit(total_revenue_usd)
        
        self.db.save_portfolio(portfolio)
        return (f"Продажа выполнена: {amount:.4f} {code} за "
            f"{total_revenue_usd:.2f} USD\n"
                f"Курс сделки: {rate:.4f} USD/{code}\n"
                f"Изменения:\n"
                f"- {code}: {target_old:.4f} → {target_wallet.balance:.4f}\n"
                f"- USD: {usd_old:.2f} → {usd_wallet.balance:.2f}")

    def show_portfolio(self, base_currency: str = 'USD') -> str:
        """
        Функция для вывода информации о портфеле

        Параметры:
            base_currency - строка, содержит код базовой валюты

        Возвращает сообщение
        """
        user = self._check_auth()
        portfolio = self.db.get_portfolio(user.user_id)
        
        if not portfolio.wallets:
            return f"Портфель пользователя '{user.username}' пуст."
        
        lines = [f"Портфель пользователя '{user.username}' "
            f"(база: {base_currency}):"]
        total_val = 0.0
        for code, wallet in portfolio.wallets.items():
            val_in_base = 0.0
            
            try:
                rate = self._get_rate_value(code, base_currency)
                val_in_base = wallet.balance * rate
                
                lines.append(f"- {code}: {wallet.balance:.4f}  → "
                    f"{val_in_base:,.2f} {base_currency}")
                total_val += val_in_base
            except ApiRequestError:
                lines.append("Ошибка. Курс не найден")
            except Exception as e:
                lines.append(f"Ошибка ({e})")
            
        lines.append("---------------------------------")
        lines.append(f"ИТОГО: {total_val:,.2f} {base_currency}")
        
        return "\n".join(lines)

    @log_action
    def update_rates(self) -> str:
        """
        Функция для вызова обновления валют
        """
        return self.updater.run_update()