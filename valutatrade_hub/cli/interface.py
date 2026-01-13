# valutatrade_hub/cli/interface.py

import argparse
import shlex
from typing import List

from ..core.exceptions import (
    ApiRequestError,
    AuthenticationError,
    CurrencyNotFoundError,
    InsufficientFundsError,
    UserNotFoundError,
)
from ..core.usecases import UseCases


class CLI:
    def __init__(self):
        """
        Конструктор класса
        """
        self.usecases = UseCases()
        self.running = False

    def print_help(self):
        """
        Функция для вывода вспомогательной информации
        """
        print("\nДоступные команды:")
        print("register --username <name> --password <pass> - "
            "зарегистрировать пользователя")
        print("login --username <name> --password <pass> - войти в аккаунт")
        print("logout - выйти из аккаунта")
        print("show-portfolio [--base <currency>] - вывести данные о портфеле")
        print("buy --currency <code> --amount <sum> - купить валюту")
        print("sell --currency <code> --amount <sum> - продать валюту")
        print("get-rate --from <code> --to <code> - получить курс валюты")
        print("update-rates - обновление курсов валют")
        print("help - справочная информация")
        print("exit - выход из программы")
    
    def run(self):
        """
        Функция основного цикла программы
        """
        self.running = True
        print("\n***Платформа для отслеживания и симуляции торговли валютами***")
        self.print_help()
        while self.running:
            try:
                if self.usecases.current_user:
                    username = self.usecases.current_user.username
                else:
                    username = "guest"
                command_input = input(f"\n{username}> ")
                self.process_command(command_input)
            except KeyboardInterrupt:
                print("\nВыход...")
                self.running = False
            except Exception as e:
                print(f"Критическая ошибка: {e}")

    def process_command(self, command_input: str):
        """
        Функция для обработки введенной команды

        Параметры:
            command_input - строка, содержит введенную пользователем команду
        """
        parts = shlex.split(command_input)
        if not parts:
            return
        
        command = parts[0].lower()
        args = parts[1:]
        
        try:
            if command == "exit":
                self.running = False
                print("Выход.")
            elif command == "help":
                self.print_help()
            elif command == "register":
                self.handle_register(args)
            elif command == "login":
                self.handle_login(args)
            elif command == "logout":
                self.handle_logout()
            elif command == "show-portfolio":
                self.handle_show_portfolio(args)
            elif command == "buy":
                self.handle_buy(args)
            elif command == "sell":
                self.handle_sell(args)
            elif command == "get-rate":
                self.handle_get_rate(args)
            elif command == "update-rates":
                self.handle_update_rates()
            else:
                print(f"Неизвестная команда: {command}")
        
        except InsufficientFundsError as e:
            print(f"Ошибка: {str(e)}")
            print("Проверьте баланс и попробуйте снова.")

        except CurrencyNotFoundError as e:
            print(f"Ошибка: {str(e)}")
            print("Используйте команду 'help get-rate' для справки или проверьте "
                "список поддерживаемых валют.")

        except ApiRequestError as e:
            print(f"Ошибка API: {str(e)}")
            print("Пожалуйста, повторите попытку позже или проверьте "
                "подключение к сети.")

        except UserNotFoundError as e:
            print(f"Ошибка: {str(e)}")
            print("Проверьте правильность имени пользователя "
                "или зарегистрируйтесь.")

        except AuthenticationError as e:
            print(f"Ошибка аутентификации: {str(e)}")
            print("Пожалуйста, выполните вход с помощью команды login.")

        except ValueError as e:
            print(f"Ошибка ввода: {str(e)}")
        
        except Exception as e:
            print(f"Неожиданная ошибка: {str(e)}")

    def handle_register(self, args: List[str]):
        """
        Функция для обработки команды регистрации пользователя

        Параметры:
            args - список, содержит переданные аргументы
        """
        parser = argparse.ArgumentParser(prog='register', add_help=False)
        parser.add_argument('--username', required=True)
        parser.add_argument('--password', required=True)
        try:
            p_args = parser.parse_args(args)
            print(self.usecases.register(p_args.username, p_args.password))
        except SystemExit:
            print("Формат: register --username <name> --password <password>")

    def handle_login(self, args: List[str]):
        """
        Функция для обработки команды входа пользователя

        Параметры:
            args - список, содержит переданные аргументы
        """
        parser = argparse.ArgumentParser(prog='login', add_help=False)
        parser.add_argument('--username', required=True)
        parser.add_argument('--password', required=True)
        try:
            p_args = parser.parse_args(args)
            print(self.usecases.login(p_args.username, p_args.password))
        except SystemExit:
            print("Формат: login --username <name> --password <password>")

    def handle_logout(self):
        """
        Функция для обработки команды выхода пользователя
        """
        print(self.usecases.logout())

    def handle_show_portfolio(self, args: List[str]):
        """
        Функция для обработки команды вывода информации о портфеле

        Параметры:
            args - список, содержит переданные аргументы
        """
        parser = argparse.ArgumentParser(prog='show-portfolio', add_help=False)
        parser.add_argument('--base', default='USD')
        try:
            p_args = parser.parse_args(args)
            print(self.usecases.show_portfolio(p_args.base.upper()))
        except SystemExit:
            print("Формат: show-portfolio [--base USD]")

    def handle_buy(self, args: List[str]):
        """
        Функция для обработки команды покупки валюты

        Параметры:
            args - список, содержит переданные аргументы
        """
        parser = argparse.ArgumentParser(prog='buy', add_help=False)
        parser.add_argument('--currency', required=True)
        parser.add_argument('--amount', type=float, required=True)
        try:
            p_args = parser.parse_args(args)
            print(self.usecases.buy(p_args.currency.upper(), p_args.amount))
        except SystemExit:
            print("Формат: buy --currency <CODE> --amount <sum>")

    def handle_sell(self, args: List[str]):
        """
        Функция для обработки команды продажи валюты

        Параметры:
            args - список, содержит переданные аргументы
        """
        parser = argparse.ArgumentParser(prog='sell', add_help=False)
        parser.add_argument('--currency', required=True)
        parser.add_argument('--amount', type=float, required=True)
        try:
            p_args = parser.parse_args(args)
            print(self.usecases.sell(p_args.currency.upper(), p_args.amount))
        except SystemExit:
            print("Формат: sell --currency <CODE> --amount <sum>")
    
    def handle_get_rate(self, args: List[str]):
        """
        Функция для обработки команды вывода курса валют

        Параметры:
            args - список, содержит переданные аргументы
        """
        parser = argparse.ArgumentParser(prog='get-rate', add_help=False)
        parser.add_argument('--from', dest='from_currency', required=True, 
            help='Исходная валюта')
        parser.add_argument('--to', dest='to_currency', required=True, 
            help='Целевая валюта')
        
        try:
            parsed_args = parser.parse_args(args)
            success, message = self.usecases.get_rate(
                parsed_args.from_currency.upper(), 
                parsed_args.to_currency.upper()
            )
            print(message)
        except SystemExit:
            print("Формат: get-rate --from <CODE> --to <CODE>")
        except Exception as e:
            print(f"Ошибка: {str(e)}")

    def handle_update_rates(self):
        """
        Функция для обработки команды обновления курсов валют
        """
        print("Обновление курсов валют...")
        try:
            result = self.usecases.update_rates()
            print(result)
        except Exception as e:
            print(f"Ошибка при обновлении: {e}")