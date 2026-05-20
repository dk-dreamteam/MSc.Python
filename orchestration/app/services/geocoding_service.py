import requests


class GeocodingService:
    BASE_URL = 'https://nominatim.openstreetmap.org/reverse'

    def reverse_geocode(self, latitude, longitude):
        try:
            params = {
                'lat': latitude,
                'lon': longitude,
                'format': 'json',
                'addressdetails': 1
            }
            headers = {'User-Agent': 'CityReport/1.0'}
            response = requests.get(
                self.BASE_URL,
                params=params,
                headers=headers,
                timeout=5
            )
            data = response.json()
            return data.get('display_name', '')
        except requests.RequestException:
            return ''
