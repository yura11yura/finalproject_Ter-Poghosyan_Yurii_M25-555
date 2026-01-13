# valutatrade_hub/core/utils.py

import json
import os

from valutatrade_hub.constants import DEFAULT_FILES


def check_data_files():
    """
    Функция для проверки и создания файлов данных при первом запуске
    """
    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)
    
    for filename, default_data in DEFAULT_FILES.items():
        path = os.path.join(data_dir, filename)
        if not os.path.exists(path):
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, indent=4, ensure_ascii=False)