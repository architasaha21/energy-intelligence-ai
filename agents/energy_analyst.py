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

            "weekly_forecast": weekly_forecast,

            "historical_summary": historical_summary,

            "statistical_analysis": statistical_analysis,

            "zone_evidence": zone_evidence
        }

        prompt = f"""
You are the Energy Analyst Agent in an AI-based
Climate and Energy Optimization system.

Your job is to interpret energy data and explain
what is happening in the building.

IMPORTANT ARCHITECTURE RULE:

Python has already performed the numerical calculations.

You must NOT recalculate statistics.

You must NOT invent numbers.

You must interpret the supplied evidence.

Your analysis should follow this reasoning:

Forecast
    ↓
Historical comparable period
    ↓
Difference
    ↓
Statistical status
    ↓
Evidence-based explanation

You must identify:

1. The predicted peak period.

2. The historical average for the comparable hour.

3. The difference between forecast and historical average.

4. Whether consumption is Normal, Elevated or Anomalous.
   Use the supplied anomaly_status.

5. Possible contributing factors.

6. Evidence supporting every important factor.

7. Which periods deserve attention.

8. Overall severity.

9. Forecast confidence.

10. Analysis confidence.

IMPORTANT:

- Do not claim causation without evidence.
- If HVAC has the highest historical average consumption,
  describe it as a likely contributor rather than claiming
  that it definitely caused the peak.
- Do not invent temperature values.
- Do not invent occupancy values.
- Do not invent financial savings.
- Do not modify the supplied z-score.
- Do not change the supplied anomaly classification.
- Do not invent historical values.

For likely factors, use this structure:

[
    {{
        "factor": "HVAC",
        "evidence": "HVAC has the highest historical average consumption.",
        "impact": "high"
    }}
]

Analysis confidence should describe confidence in the
interpretation based on the quality and amount of evidence.

Use:

"high" when multiple strong pieces of evidence agree.

"medium" when evidence exists but some information
is missing.

"low" when there is insufficient evidence.

Return ONLY valid JSON.

Required structure:

{{
    "analysis_summary": "string",

    "peak_period": "string",

    "peak_consumption": 0.0,

    "comparable_hour": "string",

    "historical_comparable_average": 0.0,

    "difference_kwh": 0.0,

    "difference_percent": 0.0,

    "historical_standard_deviation": 0.0,

    "z_score": 0.0,

    "anomaly_status": "Normal",

    "anomaly_detected": false,

    "anomaly_reason": "string",

    "likely_factors": [
        {{
            "factor": "string",
            "evidence": "string",
            "impact": "low"
        }}
    ],

    "affected_periods": [],

    "severity": "low",

    "evidence": [],

    "forecast_confidence": 0.0,

    "analysis_confidence": "medium"
}}

Context:

{json.dumps(context, indent=2)}
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
            temperature=0.2
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

        # Validate against our schema
        return EnergyAnalysis(**result)