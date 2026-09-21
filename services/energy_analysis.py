from datetime import datetime
from typing import Optional

import math

from services.historical_data import (
    HistoricalEnergyData
)


class EnergyAnalysisCalculator:
    """
    Performs deterministic calculations before the
    information is sent to the AI Analyst Agent.
    """

    def __init__(
        self,
        historical_data: HistoricalEnergyData
    ):
        self.historical_data = historical_data

    def calculate_difference(
        self,
        forecast_consumption: float,
        historical_average: float
    ) -> dict:
        """
        Calculate the absolute and percentage difference
        between forecasted and historical consumption.
        """

        difference = (
            forecast_consumption
            - historical_average
        )

        if historical_average == 0:
            difference_percent = 0.0
        else:
            difference_percent = (
                difference
                / historical_average
            ) * 100

        return {
            "difference_kwh": round(
                difference,
                2
            ),

            "difference_percent": round(
                difference_percent,
                2
            )
        }

    def calculate_z_score(
        self,
        forecast_consumption: float,
        historical_average: float,
        historical_std: float
    ) -> Optional[float]:
        """
        Calculate the z-score of the forecast against
        the historical comparable distribution.
        """

        # Cannot calculate a meaningful z-score
        # when there is no historical variation.
        if historical_std is None:
            return None

        if historical_std == 0:
            return None

        z_score = (
            forecast_consumption
            - historical_average
        ) / historical_std

        return round(
            float(z_score),
            3
        )

    def classify_consumption(
        self,
        z_score: Optional[float]
    ) -> dict:
        """
        Classify the forecast using the calculated z-score.

        Thresholds:

        |z| < 1       -> Normal
        1 <= |z| < 2 -> Elevated
        |z| >= 2      -> Anomalous
        """

        if z_score is None:
            return {
                "status": "Unknown",
                "anomaly_detected": False,
                "reason": (
                    "Insufficient historical variation "
                    "to calculate a z-score."
                )
            }

        absolute_z = abs(z_score)

        if absolute_z >= 2:
            return {
                "status": "Anomalous",
                "anomaly_detected": True,
                "reason": (
                    "The forecast is at least two "
                    "standard deviations away from the "
                    "historical comparable average."
                )
            }

        if absolute_z >= 1:
            return {
                "status": "Elevated",
                "anomaly_detected": False,
                "reason": (
                    "The forecast is above the normal "
                    "historical range but is not strongly "
                    "anomalous."
                )
            }

        return {
            "status": "Normal",
            "anomaly_detected": False,
            "reason": (
                "The forecast falls within the normal "
                "historical range."
            )
        }

    def build_forecast_context(
        self,
        forecast: dict
    ) -> dict:
        """
        Combine ML forecast data with deterministic
        historical statistics.
        """

        peak_hour_text = forecast[
            "predicted_peak_hour"
        ]

        peak_hour = int(
            peak_hour_text.split(":")[0]
        )

        peak_consumption = float(
            forecast["peak_consumption"]
        )

        forecast_date = datetime.strptime(
            forecast["date"],
            "%Y-%m-%d"
        )

        is_weekend = (
            forecast_date.weekday() >= 5
        )

        historical = (
            self.historical_data
            .get_comparable_hour_statistics(
                hour=peak_hour,
                is_weekend=is_weekend
            )
        )

        if not historical.get("available"):
            return {
                "available": False,
                "peak_hour": peak_hour_text,
                "peak_consumption": peak_consumption,
                "forecast_confidence": float(
                    forecast["confidence"]
                )
            }

        difference = self.calculate_difference(
            forecast_consumption=peak_consumption,
            historical_average=historical["mean"]
        )

        z_score = self.calculate_z_score(
            forecast_consumption=peak_consumption,
            historical_average=historical["mean"],
            historical_std=historical["std"]
        )

        classification = (
            self.classify_consumption(
                z_score
            )
        )

        return {
            "available": True,

            "peak_hour": peak_hour_text,

            "peak_consumption": peak_consumption,

            "historical_comparable_average": (
                historical["mean"]
            ),

            "historical_comparable_std": (
                historical["std"]
            ),

            "historical_comparable_min": (
                historical["minimum"]
            ),

            "historical_comparable_max": (
                historical["maximum"]
            ),

            "sample_count": (
                historical["sample_count"]
            ),

            "difference_kwh": (
                difference["difference_kwh"]
            ),

            "difference_percent": (
                difference["difference_percent"]
            ),

            "z_score": z_score,

            "anomaly_status": (
                classification["status"]
            ),

            "anomaly_detected": (
                classification["anomaly_detected"]
            ),

            "anomaly_reason": (
                classification["reason"]
            ),

            "forecast_confidence": float(
                forecast["confidence"]
            )
        }