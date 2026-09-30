import json

from groq import Groq

from config import GROQ_API_KEY, GROQ_MODEL
from schemas.analysis import (
    EnergyAnalysis
)


class EnergyAnalystAgent:
    """
    AI agent responsible for interpreting energy forecasts,
    historical patterns and deterministic statistical analysis.
    """

    def __init__(self):
        if not GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY is not configured."
            )

        # Initialize the Groq client
        self.client = Groq(
            api_key=GROQ_API_KEY
        )

    async def analyze(
        self,
        forecast: dict,
        weekly_forecast: dict,
        historical_summary: dict,
        statistical_analysis: dict,
        zone_evidence: list
    ) -> EnergyAnalysis:
        """
        Interpret the objective statistical calculations
        and convert them into human-readable reasoning.
        """

        context = {
            "forecast": forecast,
            "statistical_analysis": statistical_analysis,
            "zone_evidence": zone_evidence[:5]
        }

        prompt = f"""
You are an Energy Analyst.

Interpret the supplied energy evidence.

Do not calculate or modify numerical values.
Do not invent facts or causes.
Treat high-consumption zones as possible contributors, not proven causes.

Return ONLY JSON with these fields:

{{
    "analysis_summary": "string",
    "anomaly_reason": "string",
    "likely_factors": [
        {{
            "factor": "string",
            "evidence": "string",
            "impact": "low"
        }}
    ],
    "affected_periods": ["string"],
    "evidence": ["string"],
    "analysis_confidence": "low"
}}

Context:
{json.dumps(context, separators=(",", ":"))}
"""

        # Ask Groq to interpret the supplied evidence
        response = self.client.chat.completions.create(
            model=GROQ_MODEL,

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a precise energy analytics "
                        "assistant. Interpret supplied data "
                        "without inventing facts. Return "
                        "only valid JSON."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            # Low temperature gives more consistent
            # analytical responses.
            temperature=0.2,
            reasoning_effort="low",
            include_reasoning=False,
            max_completion_tokens=500,
            response_format={"type": "json_object"}
        )

        # Extract the model's response
        text = (
            response
            .choices[0]
            .message
            .content
            .strip()
        )

        # Remove markdown fences if the model adds them
        if text.startswith("```"):
            text = text.replace(
                "```json",
                ""
            )

            text = text.replace(
                "```",
                ""
            )

            text = text.strip()

        # Parse the JSON response
        result = json.loads(text)

        # Merge deterministic values calculated by Python
        result["peak_period"] = forecast.get(
            "predicted_peak_hour",
            "unknown"
        )

        result["peak_consumption"] = statistical_analysis.get(
            "peak_consumption",
            forecast.get("peak_consumption", 0.0)
        )

        result["comparable_hour"] = statistical_analysis.get(
            "peak_hour",
            result["peak_period"]
        )

        result["historical_comparable_average"] = statistical_analysis.get(
            "historical_comparable_average",
            0.0
        )

        result["difference_kwh"] = statistical_analysis.get(
            "difference_kwh",
            0.0
        )

        result["difference_percent"] = statistical_analysis.get(
            "difference_percent",
            0.0
        )

        result["historical_standard_deviation"] = statistical_analysis.get(
            "historical_comparable_std",
            0.0
        )

        result["z_score"] = statistical_analysis.get(
            "z_score",
            0.0
        )

        result["anomaly_status"] = statistical_analysis.get(
            "anomaly_status",
            "Unknown"
        )

        result["anomaly_detected"] = statistical_analysis.get(
            "anomaly_detected",
            False
        )

        if isinstance(result.get("analysis_confidence"), (int, float)):
            confidence = result["analysis_confidence"]
            result["analysis_confidence"] = (
                "high" if confidence >= 0.8
                else "medium" if confidence >= 0.5
                else "low"
            )

        # Fill fields that can be determined safely from Python data
        result.setdefault(
            "affected_periods",
            [forecast.get("predicted_peak_hour", "unknown")]
        )

        result.setdefault(
            "severity",
            "high"
            if statistical_analysis.get("anomaly_status") == "Anomalous"
            else "medium"
            if statistical_analysis.get("anomaly_status") == "Elevated"
            else "low"
        )

        result.setdefault(
            "evidence",
            [
                f"Predicted peak consumption: "
                f"{forecast.get('peak_consumption', 0)} kWh.",
                f"Comparable historical average: "
                f"{statistical_analysis.get('historical_comparable_average', 0)} kWh.",
                f"Anomaly status: "
                f"{statistical_analysis.get('anomaly_status', 'Unknown')}."
            ]
        )

        result.setdefault(
            "forecast_confidence",
            forecast.get("confidence", 0.0)
        )

        result.setdefault(
            "analysis_confidence",
            "medium"
        )

        # Validate against our schema
        return EnergyAnalysis(**result)