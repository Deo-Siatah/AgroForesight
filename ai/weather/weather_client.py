import httpx

class WeatherClient:
    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    async def get_weather(
        self,
        latitude: float,
        longitude: float,
    ) -> dict:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": [
                "temperature_2m",
                "relative_humidity_2m",
                "wind_speed_10m",
            ],
            "daily": [
                "precipitation_sum",
            ],
            "timezone": "auto",
        }

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                self.BASE_URL,
                params=params,
            )

            response.raise_for_status()

            data = response.json()

        current = data.get("current", {})
        daily = data.get("daily", {})

        return {
            "rainfall_mm": (
                daily.get("precipitation_sum", [0])[0]
                if daily.get("precipitation_sum")
                else 0
            ),
            "temperature_c": current.get(
                "temperature_2m"
            ),
            "humidity_percent": current.get(
                "relative_humidity_2m"
            ),
            "wind_speed_kmh": current.get(
                "wind_speed_10m"
            ),
            "source": "open-meteo",
        }