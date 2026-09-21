from typing import Optional

from pydantic import BaseModel


class ForecastResponse(BaseModel):
    date: str

    predicted_peak_hour: str

    predicted_consumption: float

    peak_consumption: float

    confidence: float

    error: Optional[str] = None

    details: Optional[str] = None


class DailyForecast(BaseModel):
    date: str

    predicted_peak_hour: str

    predicted_consumption: float

    peak_consumption: float

    confidence: float


class WeeklyForecastResponse(BaseModel):
    forecast: list[DailyForecast]