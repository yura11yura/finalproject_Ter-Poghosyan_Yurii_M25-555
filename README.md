Выполнил: Тер-Погосян Юрий М25-555

# Платформа для отслеживания и симуляции торговли валютами

Это комплексная платформа, которая позволяет пользователям регистрироваться, управлять своим виртуальным портфелем фиатных и криптовалют, совершать сделки по покупке/продаже, а также отслеживать актуальные курсы в реальном времени. 

## Установочные операции

### Для запуска

Установка зависимостей - `make install`

Запуск проекта - `make project`

### Дополнительные операции

Активация виртуального окружения - `poetry shell`

Сборка пакета - `make build`

Тест публикации - `make publish`

Установка собранного пакета - `make package-install`

Проверка кода линтером - `make lint`

### (!) Для корректной работы введите API ключ в `config.py`

`os.environ['EXCHANGERATE_API_KEY'] = ""`

## Основные операции с системой

1. Регистрация нового пользователя - `register --username <name> --password <pass>`
2. Вход в аккаунт - `login --username <name> --password <pass>`
3. Выход из аккаунта - `logout`
4. Вывод данных о профиле - `show-portfolio [--base <currency>]`
5. Покупка валюты - `buy --currency <code> --amount <sum>`
6. Продажа валюты - `sell --currency <code> --amount <sum>`
7. Вывод курса валюты - `get-rate --from <code> --to <code>`
8. Обновление курсов валют - `update-rates`
9. Вывод справочной информации - `help`
10. Выход из программы - `exit`

## Используемые валюты

- USD
- RUB
- EUR
- GBP
- JPY
- CNY
- BTC
- SOL
- ETH

## Демонстрация работы

[![asciicast](https://asciinema.org/a/PqiADK1LAVJjcbDH.svg)](https://asciinema.org/a/PqiADK1LAVJjcbDH)