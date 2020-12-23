from dotenv import load_dotenv
import logging
import os


# make sure we have access to the env variables
load_dotenv()
LOG_LEVEL = os.getenv("LOG_LEVEL", logging.WARNING)
ALERT_THRESHOLD = os.getenv("ALERT_THRESHOLD", 3)
CRYPTO_METRICS = ["last", "high", "low", "volume", "vwap", "max_bid",
                  "min_ask", "best_bid", "best_ask"]
METRIC_URL = "https://api.livecoin.net/exchange/ticker"

# set up a base logger
format_str = '%(asctime)s %(name)s %(levelname)s %(message)s'
handler = logging.StreamHandler()
handler.setLevel(LOG_LEVEL)
formatter = logging.Formatter(format_str)
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(handler)
