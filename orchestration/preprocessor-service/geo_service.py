import logging
import requests

logger = logging.getLogger(__name__)


class GeoService:
    def __init__(self):
        self.base_url = "https://nominatim.openstreetmap.org/search"
        self.headers = {"User-Agent": "cityreport/1.0"}

    def GetCoordinatesFromAddress(self, address: str) -> tuple[float, float]:
        params = {"q": address, "format": "json", "limit": 1}
        response = requests.get(self.base_url, params=params, headers=self.headers)
        response.raise_for_status()
        result = response.json()[0]
        lat = float(result["lat"])
        lon = float(result["lon"])
        logger.info("Geocoded address '%s' to (%f, %f)", address, lat, lon)
        return lat, lon
