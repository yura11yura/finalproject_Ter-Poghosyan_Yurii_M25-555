# valutatrade_hub/logging_config.py

import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging():
    """
    Функция для логирования в файл actions.log
    """
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "actions.log")

    logger = logging.getLogger("valutatrade")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = RotatingFileHandler(log_file, maxBytes=1_000_000, 
            backupCount=3, encoding='utf-8')
        
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%dT%H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

logger = setup_logging()