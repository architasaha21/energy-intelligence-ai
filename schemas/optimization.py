from typing import Any, List, Optional

from pydantic import BaseModel


class OptimizationSavings(BaseModel):
    energy_kwh: float = 0.0
    energy_percent: float = 0.0
    peak_reduction_kw: float = 0.0
    peak_reduction_percent: float = 0.0
    daily_cost_inr: float = 0.0
    daily_cost_percent: float = 0.0
    monthly_cost_inr: float = 0.0


class OptimizationIntervention(BaseModel):
    strategy: str
    lever: str
    target_period: str
    action: str
    comfort_impact: str

    baseline_consumption: float = 0.0
    estimated_reduction: float = 0.0
    optimized_consumption: float = 0.0
    reduction_percent: float = 0.0

    energy_saving_kwh: float = 0.0
    peak_reduction_kw: float = 0.0
    daily_cost_saving_inr: float = 0.0
    monthly_cost_saving_inr: float = 0.0
    saving_percent: float = 0.0


class OptimizationResponse(BaseModel):
    status: str
    date: str

    savings: OptimizationSavings

    interventions: List[OptimizationIntervention] = []

    all_constraints_satisfied: bool = False

    constraints: List[dict[str, Any]] = []

    robustness: Optional[dict[str, Any]] = None