import os
import logging
from api.routes import city_report_api

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

if __name__ == "__main__":
    port = int(os.getenv("APP_PORT"))
    city_report_api.run(host="0.0.0.0", port=port)
