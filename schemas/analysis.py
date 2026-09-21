from typing import List, Optional

from pydantic import BaseModel


class EvidenceItem(BaseModel):
    """
    Represents one evidence-backed factor
    contributing to the energy analysis.
    """

    factor: str

    evidence: str

    impact: str


class EnergyAnalysis(BaseModel):
    """
    Structured output produced by the Energy Analyst Agent.
    """

    # Overall explanation of the energy situation
    analysis_summary: str

    # Forecast information
    peak_period: str
    peak_consumption: float

    # Historical comparison
    comparable_hour: str
    historical_comparable_average: float
    difference_kwh: float
    difference_percent: float

    # Statistical anomaly information
    historical_standard_deviation: Optional[float] = None
    z_score: Optional[float] = None
    anomaly_status: str

    # Whether the forecast should be treated as unusual
    anomaly_detected: bool

    anomaly_reason: Optional[str] = None

    # Factors supported by historical evidence
    likely_factors: List[EvidenceItem]

    # Periods that deserve attention
    affected_periods: List[str]

    # Overall severity
    severity: str

    # Raw evidence used by the agent
    evidence: List[str]

    # ML forecast reliability
    forecast_confidence: float

    # Confidence of the analytical interpretation
    analysis_confidence: str