import httpx

from config import ML_API_URL
from schemas.forecast import (
    ForecastResponse,
    WeeklyForecastResponse
)


class ForecastClient:
    """
    Client responsible for communicating with the external
    Energy Forecasting API.
    """

    def __init__(self, base_url: str = ML_API_URL):
        self.base_url = base_url.rstrip("/")

    async def get_forecast(self) -> ForecastResponse:
        """
        Get the next 24-hour forecast summary from the ML API.
        """

        url = f"{self.base_url}/forecast"

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url)

        response.raise_for_status()

        data = response.json()

        return ForecastResponse(**data)

    async def get_weekly_forecast(self) -> WeeklyForecastResponse:
        """
        Get the seven-day forecast from the ML API.
        """

        url = f"{self.base_url}/forecast/weekly"

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url)

        response.raise_for_status()

        data = response.json()

        return WeeklyForecastResponse(**data)