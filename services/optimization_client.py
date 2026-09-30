import httpx

from config import OPTIMIZER_API_URL


class OptimizationClient:
    def __init__(self, base_url: str = OPTIMIZER_API_URL):
        self.base_url = base_url.rstrip("/")

    async def optimize(self, forecast: dict) -> dict:
        url = f"{self.base_url}/optimize"

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=forecast)

        response.raise_for_status()
        return response.json()

    async def optimize_week(self, forecasts: list[dict]) -> dict:
        url = f"{self.base_url}/optimize/week"

        payload = {
            "forecast": forecasts
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=payload)

        response.raise_for_status()
        return response.json()