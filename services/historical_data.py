from pathlib import Path
from typing import Optional

import pandas as pd


class HistoricalEnergyData:
    """
    Loads historical building energy data and calculates
    statistics used by the Energy Analyst Agent.
    """

    def __init__(self, csv_path: str = "energy_data.csv"):
        self.csv_path = Path(csv_path)

        # Store the dataframe if the file exists
        if not self.csv_path.exists():
            self.data = None
            return

        self.data = pd.read_csv(
            self.csv_path,
            parse_dates=["timestamp"]
        )

        # Create useful time-based columns
        self.data["hour"] = (
            self.data["timestamp"].dt.hour
        )

        self.data["day_of_week"] = (
            self.data["timestamp"].dt.dayofweek
        )

    def is_available(self) -> bool:
        """
        Check whether historical data was loaded successfully.
        """

        return (
            self.data is not None
            and not self.data.empty
        )

    def get_hourly_consumption(self) -> pd.DataFrame:
        """
        Aggregate zone-level consumption into
        total building consumption for every timestamp.
        """

        if not self.is_available():
            return pd.DataFrame()

        hourly = (
            self.data
            .groupby("timestamp")
            .agg(
                consumption_kwh=(
                    "consumption_kwh",
                    "sum"
                ),
                temperature=(
                    "temperature",
                    "mean"
                ),
                occupancy=(
                    "occupancy",
                    "mean"
                )
            )
            .reset_index()
        )

        hourly["hour"] = (
            hourly["timestamp"].dt.hour
        )

        hourly["day_of_week"] = (
            hourly["timestamp"].dt.dayofweek
        )

        hourly["is_weekend"] = (
            hourly["day_of_week"] >= 5
        )

        return hourly

    def get_comparable_hour_statistics(
        self,
        hour: int,
        is_weekend: Optional[bool] = None
    ) -> dict:
        """
        Calculate historical statistics for the same
        hour of the day.

        If weekend information is provided, only comparable
        weekday/weekend observations are used.
        """

        hourly = self.get_hourly_consumption()

        if hourly.empty:
            return {
                "available": False
            }

        comparable = hourly[
            hourly["hour"] == hour
        ].copy()

        # Match weekday/weekend pattern when available
        if is_weekend is not None:
            comparable = comparable[
                comparable["is_weekend"] == is_weekend
            ]

        if comparable.empty:
            return {
                "available": False
            }

        consumption = (
            comparable["consumption_kwh"]
        )

        return {
            "available": True,

            "hour": hour,

            "sample_count": int(
                len(consumption)
            ),

            "mean": round(
                float(consumption.mean()),
                2
            ),

            "median": round(
                float(consumption.median()),
                2
            ),

            "std": round(
                float(consumption.std()),
                2
            ) if len(consumption) > 1 else 0.0,

            "minimum": round(
                float(consumption.min()),
                2
            ),

            "maximum": round(
                float(consumption.max()),
                2
            )
        }

    def get_summary(self) -> dict:
        """
        Generate an overall summary of historical
        building energy behaviour.
        """

        if not self.is_available():
            return {
                "available": False,
                "message": (
                    "Historical energy data "
                    "is not available."
                )
            }

        hourly = self.get_hourly_consumption()

        hourly_average = float(
            hourly["consumption_kwh"].mean()
        )

        peak_usage = float(
            hourly["consumption_kwh"].max()
        )

        peak_row = hourly.loc[
            hourly["consumption_kwh"].idxmax()
        ]

        peak_hour = int(
            peak_row["hour"]
        )

        hourly_profile = (
            hourly
            .groupby("hour")["consumption_kwh"]
            .mean()
            .sort_values(
                ascending=False
            )
        )

        top_hours = [
            int(hour)
            for hour in hourly_profile.head(5).index
        ]

        zone_summary = (
            self.data
            .groupby("zone")["consumption_kwh"]
            .mean()
            .sort_values(
                ascending=False
            )
        )

        return {
            "available": True,

            "average_hourly_consumption": round(
                hourly_average,
                2
            ),

            "maximum_hourly_consumption": round(
                peak_usage,
                2
            ),

            "historical_peak_hour": (
                f"{peak_hour:02d}:00"
            ),

            "highest_average_consumption_hours": [
                f"{hour:02d}:00"
                for hour in top_hours
            ],

            "zone_average_consumption": {
                str(zone): round(
                    float(value),
                    2
                )
                for zone, value
                in zone_summary.items()
            }
        }

    def get_peak_zone_evidence(self) -> list:
        """
        Identify zones with the highest historical
        average energy consumption.

        This is evidence for the LLM rather than an
        assumption about causality.
        """

        if not self.is_available():
            return []

        zone_summary = (
            self.data
            .groupby("zone")["consumption_kwh"]
            .mean()
            .sort_values(
                ascending=False
            )
        )

        results = []

        for zone, value in zone_summary.items():
            results.append({
                "zone": str(zone),
                "average_consumption": round(
                    float(value),
                    2
                )
            })

        return results