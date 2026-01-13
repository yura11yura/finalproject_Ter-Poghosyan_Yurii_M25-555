# !/usr/bin/env python3

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from valutatrade_hub.cli.interface import CLI
from valutatrade_hub.core.utils import check_data_files
from valutatrade_hub.infra.settings import SettingsLoader
from valutatrade_hub.logging_config import setup_logging


def main():
    """
    Функция для первичного запуска программы
    """
    SettingsLoader() 
    check_data_files()
    setup_logging()
    
    cli = CLI()
    cli.run()

if __name__ == "__main__":
    main()