# valutatrade_hub/parser_service/updater.py

import datetime

from ..core.exceptions import ApiRequestError
from ..infra.database import DatabaseManager
from ..logging_config import logger
from .api_clients import CoinGeckoClient, ExchangeRateApiClient
from .storage import HistoryStorage


class RatesUpdater:
    """
    Класс реализующий обновление курсов валют
    """
    def __init__(self):
        self.clients = [
            CoinGeckoClient(),
            ExchangeRateApiClient()
        ]
        self.db = DatabaseManager()
        self.storage = HistoryStorage()

    def run_update(self) -> str:
        """
        Функция для запроса и обновления курсов валют
        """
        logger.info("Starting manual rates update...")
        all_rates = {}
        errors = []
        
        for client in self.clients:
            client_name = client.__class__.__name__
            try:
                rates = client.fetch_rates()
                all_rates.update(rates)
                logger.info(f"Fetched {len(rates)} rates from {client_name}")
            except ApiRequestError as e:
                msg = f"Failed to fetch from {client_name}: {e}"
                logger.error(msg)
                errors.append(msg)
            except Exception as e:
                msg = f"Unexpected error in {client_name}: {e}"
                logger.error(msg)
                errors.append(msg)

        if not all_rates:
            return "Не удалось обновить курсы. Ошибки:\n" + "\n".join(errors)
        
        now_iso = datetime.datetime.now().isoformat()
        
        self.storage.save_history(all_rates, now_iso)
            
        logger.info(f"Writing {len(all_rates)} rates to storage...")

        current_data = self.db.load_full_rates_data()
        pairs_data = current_data.get("pairs", {})

        count = 0
        for pair, rate_val in all_rates.items():
            pairs_data[pair] = {
                "rate": rate_val,
                "updated_at": now_iso}
            count += 1

        pairs_data["USD_USD"] = {"rate": 1.0, "updated_at": now_iso}
        final_data = {"pairs": pairs_data, "last_refresh": now_iso}

        self.db.save_rates(final_data)
        
        result_msg = f"Успешно обновлено {count} курсов."
        if errors:
            result_msg += "\nОшибки при обновлении некоторых источников (см. логи)."
        
        logger.info(result_msg)
        return result_msg