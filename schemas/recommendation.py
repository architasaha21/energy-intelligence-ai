from typing import List

from pydantic import BaseModel


class Recommendation(BaseModel):
	action: str
	reason: str
	priority: str
	target_period: str
	expected_impact: str
	estimated_saving_percent: float


class RecommendationResponse(BaseModel):
	recommendations: List[Recommendation]
	overall_strategy: str
	limitations: List[str]
