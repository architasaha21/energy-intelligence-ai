from typing import List


class EnergyOptimizer:
    """
    Performs simple deterministic intervention simulations.

    The LLM decides which interventions are sensible.
    This class performs the numerical simulation.
    """

    def simulate_hvac_reduction(
        self,
        peak_consumption: float,
        reduction_percent: float = 10.0
    ) -> dict:
        """
        Simulate a percentage reduction in energy consumption.
        """

        reduction = peak_consumption * (
            reduction_percent / 100
        )

        optimized_consumption = (
            peak_consumption - reduction
        )

        return {
            "baseline_consumption": round(
                peak_consumption,
                2
            ),
            "estimated_reduction": round(
                reduction,
                2
            ),
            "optimized_consumption": round(
                optimized_consumption,
                2
            ),
            "reduction_percent": reduction_percent
        }

    def simulate_schedule_shift(
        self,
        peak_consumption: float,
        reduction_percent: float = 8.0
    ) -> dict:
        """
        Simulate moving a flexible activity outside
        the predicted peak period.
        """

        reduction = peak_consumption * (
            reduction_percent / 100
        )

        optimized_consumption = (
            peak_consumption - reduction
        )

        return {
            "baseline_consumption": round(
                peak_consumption,
                2
            ),
            "estimated_reduction": round(
                reduction,
                2
            ),
            "optimized_consumption": round(
                optimized_consumption,
                2
            ),
            "reduction_percent": reduction_percent
        }

    def compare_strategies(
        self,
        peak_consumption: float
    ) -> List[dict]:
        """
        Compare available intervention scenarios.
        """

        hvac = self.simulate_hvac_reduction(
            peak_consumption,
            reduction_percent=10.0
        )

        schedule = self.simulate_schedule_shift(
            peak_consumption,
            reduction_percent=8.0
        )

        return [
            {
                "strategy": "HVAC optimization",
                **hvac
            },
            {
                "strategy": "Schedule shifting",
                **schedule
            }
        ]