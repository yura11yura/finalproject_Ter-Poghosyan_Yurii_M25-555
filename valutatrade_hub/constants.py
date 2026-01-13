# valutatrade_hub/constants.py

from datetime import datetime

DEFAULT_FILES = {
    'users.json': [],
    'portfolios.json': [],
    'rates.json': {
        "pairs": {
            "BTC_USD": {"rate": 59337.21, "updated_at": datetime.now().isoformat()},
            "ETH_USD": {"rate": 3720.00, "updated_at": datetime.now().isoformat()},
            "EUR_USD": {"rate": 1.0786, "updated_at": datetime.now().isoformat()},
            "GBP_USD": {"rate": 1.25, "updated_at": datetime.now().isoformat()},
            "RUB_USD": {"rate": 0.011, "updated_at": datetime.now().isoformat()},
            "USD_USD": {"rate": 1.0, "updated_at": datetime.now().isoformat()}
        },
        "last_refresh": datetime.now().isoformat()
    }
}