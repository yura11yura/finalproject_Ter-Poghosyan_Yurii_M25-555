# valutatrade_hub/parser_service/storage.py

import json
import os
from typing import Dict

from ..infra.settings import SettingsLoader


class HistoryStorage:
    """
    Класс, реализующий запись истории курсов валют
    """
    def __init__(self):
        self.settings = SettingsLoader()
        self.filepath = self.settings.get("HISTORY_FILE_PATH", \
            "data/exchange_rates.json")
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """
        Функция проверки существования файла
        """
        if not os.path.exists(self.filepath):
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def save_history(self, new_rates: Dict[str, float], timestamp: str):
        """
        Функция для сохранения записи об обновлении в историю

        Параметры:
            new_rates - словарь, содержит обновленные курсы валют
            timestamp - строка, содержит дату и время обновления
        """
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                try:
                    history = json.load(f)
                    if not isinstance(history, list):
                        history = []
                except json.JSONDecodeError:
                    history = []

            for pair, rate in new_rates.items():
                record_id = f"{pair}_{timestamp}"
                
                record = {
                    "id": record_id,
                    "pair": pair,
                    "rate": rate,
                    "timestamp": timestamp,
                }
                history.append(record)

            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Ошибка сохранения истории: {e}")