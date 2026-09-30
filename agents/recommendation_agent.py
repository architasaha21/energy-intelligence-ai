import json

from groq import Groq

from config import GROQ_API_KEY, GROQ_MODEL
from schemas.analysis import EnergyAnalysis
from schemas.recommendation import RecommendationResponse


class RecommendationAgent:
    """
    AI agent responsible for converting energy analysis
    into practical interventions.
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

    async def recommend(
        self,
        analysis: EnergyAnalysis,
        optimization_results: dict,
        decision: dict
    ) -> RecommendationResponse:
        """
        Generate actionable recommendations based on
        the Energy Analyst's findings.
        """

        context = {
            "analysis": analysis.model_dump(),
            "decision": decision,
            "optimization": {
                "status": optimization_results.get("status"),
                "date": optimization_results.get("date"),
                "savings": optimization_results.get("savings", {}),
                "interventions": optimization_results.get("interventions", []),
                "all_constraints_satisfied": optimization_results.get(
                    "all_constraints_satisfied",
                    False
                ),
                "robustness": optimization_results.get("robustness", {})
            }
        }
        prompt = f"""
You are a Recommendation Agent in an AI Climate and
Energy Optimization system.

Your task is to convert the energy analysis into
specific and practical energy-saving interventions.

You are given:

- Energy Analyst findings
- Deterministic optimization results
- Decision Engine output

The Decision Engine is deterministic and must be respected.
Use its decision_type and priority when framing recommendations.
Do not override the Decision Engine with your own judgment.

Your recommendations must:

1. Address the identified energy issue.
2. Specify the target period when possible.
3. Explain why the recommendation is appropriate.
4. Assign a priority.
5. Use the simulation results when estimating impact.
6. Never invent savings that were not provided.
7. Never claim a simulation result is a guaranteed
   real-world saving.

Possible intervention types include:

- HVAC optimization
- shifting flexible operations
- reducing unnecessary lighting
- avoiding simultaneous high-load activities
- scheduling non-critical operations outside peak periods

Return ONLY valid JSON:

{{
    "recommendations": [
        {{
            "action": "string",
            "reason": "string",
            "priority": "high",
            "target_period": "string",
            "expected_impact": "string",
            "estimated_saving_percent": 0.0
        }}
    ],
    "overall_strategy": "string",
    "limitations": []
}}

Context:

{json.dumps(context, indent=2)}
"""

        # Send the recommendation request to Groq
        response = self.client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an energy optimization "
                        "assistant. Return only valid JSON."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_completion_tokens=1000,
            reasoning_effort="low",
            include_reasoning=False,
            response_format={"type": "json_object"}
        )

        # Extract the model response
        text = response.choices[0].message.content.strip()

        # Remove markdown code fences if present
        if text.startswith("```"):
            text = text.replace("```json", "")
            text = text.replace("```", "")
            text = text.strip()

        # Convert the response into structured JSON
        result = json.loads(text)

        # Fill required fields if the model omits them
        result.setdefault(
            "overall_strategy",
            "Apply the feasible optimization interventions identified "
            "by the optimizer while respecting operational constraints."
        )

        result.setdefault(
            "limitations",
            [
                "Savings are model-based estimates and are not guaranteed "
                "in real-world operation.",
                "Recommendations depend on the forecast, optimizer "
                "assumptions, and available historical data."
            ]
        )

        # Validate the response using our Pydantic schema
        return RecommendationResponse(**result)