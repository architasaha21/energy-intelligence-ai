from fastapi import APIRouter, HTTPException

from agents.energy_analyst import EnergyAnalystAgent
from agents.recommendation_agent import RecommendationAgent
from services.energy_analysis import EnergyAnalysisCalculator
from services.forecast_client import ForecastClient
from services.historical_data import HistoricalEnergyData
from services.optimization import EnergyOptimizer


router = APIRouter()


forecast_client = ForecastClient()
historical_data = HistoricalEnergyData("energy_data.csv")
analysis_calculator = EnergyAnalysisCalculator(historical_data)
optimizer = EnergyOptimizer()
energy_analyst = EnergyAnalystAgent()
recommendation_agent = RecommendationAgent()


@router.get("/energy-intelligence")
async def get_energy_intelligence():
    """Run the complete AI energy intelligence pipeline."""
    try:
        forecast = await forecast_client.get_forecast()
        weekly_forecast = await forecast_client.get_weekly_forecast()

        historical_summary = historical_data.get_summary()
        statistical_analysis = analysis_calculator.build_forecast_context(
            forecast.model_dump()
        )
        zone_evidence = historical_data.get_peak_zone_evidence()

        analysis = await energy_analyst.analyze(
            forecast=forecast.model_dump(),
            weekly_forecast=weekly_forecast.model_dump(),
            historical_summary=historical_summary,
            statistical_analysis=statistical_analysis,
            zone_evidence=zone_evidence,
        )

        optimization_results = optimizer.compare_strategies(
            peak_consumption=forecast.peak_consumption
        )
        recommendations = await recommendation_agent.recommend(
            analysis=analysis,
            optimization_results=optimization_results,
        )

        return {
            "forecast": forecast.model_dump(),
            "weekly_forecast": weekly_forecast.model_dump(),
            "statistical_analysis": statistical_analysis,
            "analysis": analysis.model_dump(),
            "optimization": optimization_results,
            "recommendations": recommendations.model_dump(),
        }

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
