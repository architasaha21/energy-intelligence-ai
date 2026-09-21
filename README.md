# AI Energy Intelligence

AI agent layer for the larger AI Climate and Energy Optimization project.

This service consumes forecasts from an external machine-learning API,
compares those forecasts with historical
building data, asks Groq to explain the evidence, and produces structured
energy recommendations.

The project deliberately separates deterministic calculations from language
model reasoning. Python calculates the measurements; the agents interpret
those measurements and turn them into readable analysis and actions.

## Responsibilities

The current component provides:

- A client for the 24-hour and seven-day forecast endpoints.
- Historical hourly and zone-level energy summaries.
- Comparable-period analysis for the forecast peak hour.
- Difference, percentage difference, standard deviation, and z-score values.
- Deterministic anomaly classification.
- Evidence-backed Energy Analyst output validated with Pydantic.
- Evidence-backed Recommendation Agent output validated with Pydantic.
- A FastAPI endpoint that orchestrates the complete pipeline.

The current optimization service is a temporary simulation used to exercise
the agent workflow. It is not the final optimization engine and should be
replaced when a production optimization implementation is available.

## Architecture

```text
External Forecasting API
                      |
                      v
       ForecastClient
                      |
                      +----------------------+
                      |                      |
                      v                      v
 HistoricalEnergyData   Forecast context
                      |                      |
                      +----------+-----------+
                                                 v
                      EnergyAnalysisCalculator
                                                 |
                                                 v
                      Energy Analyst Agent
                             (Groq interpretation)
                                                 |
                                                 v
               Temporary optimization simulation
                                                 |
                                                 v
                Recommendation Agent (Groq)
                                                 |
                                                 v
                             FastAPI response
```

### Data flow

1. `ForecastClient` requests the current and weekly forecast from the
       configured forecasting API.
2. `HistoricalEnergyData` loads `energy_data.csv` and aggregates zone-level
       readings into hourly building totals.
3. `EnergyAnalysisCalculator` selects historical observations matching the
       forecast peak hour and weekday/weekend pattern.
4. Python calculates the historical comparison, z-score, and anomaly status.
5. `EnergyAnalystAgent` receives the supplied evidence and explains it. It is
       instructed not to recalculate statistics or invent values.
6. The temporary optimizer produces simulation results.
7. `RecommendationAgent` converts the analysis and simulation results into
       structured interventions and limitations.

## Anomaly classification

The deterministic analysis uses the absolute z-score of the forecast against
the comparable historical distribution:

| Absolute z-score | Status | `anomaly_detected` |
| --- | --- | --- |
| `< 1` | Normal | `false` |
| `>= 1` and `< 2` | Elevated | `false` |
| `>= 2` | Anomalous | `true` |

If there is not enough historical variation to calculate a meaningful z-score,
the result is `Unknown` and the system does not mark it as anomalous.

## Repository layout

```text
energy-intelligence-ai/
├── agents/
│   ├── energy_analyst.py       # Groq-backed evidence interpretation
│   └── recommendation_agent.py # Groq-backed interventions
├── api/
│   └── routes.py               # End-to-end FastAPI orchestration
├── schemas/
│   ├── analysis.py              # Analyst response models
│   ├── forecast.py              # Forecast API response models
│   └── recommendation.py        # Recommendation response models
├── services/
│   ├── energy_analysis.py       # Deterministic comparisons and z-scores
│   ├── forecast_client.py       # Forecast API client
│   ├── historical_data.py       # CSV loading and aggregation
│   └── optimization.py          # Temporary simulation only
├── energy_data.csv              # Historical building dataset
├── config.py                    # Environment-backed configuration
├── main.py                      # FastAPI application entry point
├── requirements.txt             # Python dependencies
└── .env.example                 # Configuration template
```

## Requirements

- Python 3.10 or newer.
- A working virtual environment. The project currently uses `venv/`.
- Access to a deployed forecasting API or a compatible local API.
- A Groq API key with access to the configured model.

## Local setup

From the repository root, create or activate the existing virtual environment:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies into that environment:

```powershell
python -m pip install -r requirements.txt
```

Create `.env` from `.env.example` and set the local values:

```dotenv
GROQ_API_KEY=your_groq_api_key_here
ML_API_URL=https://your-forecast-service.example
```

`.env` contains secrets and must never be committed. The repository's
`.gitignore` excludes `.env`, virtual environments, Python caches, editor
files, and temporary manual connection probes.

## Run the API

Start the development server on the project's configured port:

```powershell
.\venv\Scripts\python.exe -m uvicorn main:app --reload --port 8001
```

Useful local URLs:

- Health check: `http://127.0.0.1:8001/`
- Swagger UI: `http://127.0.0.1:8001/docs`
- Energy intelligence pipeline: `http://127.0.0.1:8001/energy-intelligence`

The `/energy-intelligence` endpoint performs external API and Groq calls, so
it requires valid configuration and reachable upstream services.

## Validation workflow

Run syntax validation before starting the application:

```powershell
.\venv\Scripts\python.exe -m compileall -q agents api schemas services config.py main.py
```

The repository also contains temporary manual probes for local development.
They are intentionally ignored by Git:

```powershell
.\venv\Scripts\python.exe test_connection.py
.\venv\Scripts\python.exe test_groq.py
.\venv\Scripts\python.exe test_history.py
```

These checks verify, independently:

- The configured forecasting API's `/forecast` connection.
- Groq credentials and model access.
- Historical CSV loading and summary generation.

When debugging an end-to-end failure, run the checks in that order. A failure
in an upstream service should be reported as an integration failure rather
than hidden by changing the local analysis code.

## Configuration

| Variable | Required | Purpose |
| --- | --- | --- |
| `GROQ_API_KEY` | Yes | Authenticates the Energy Analyst and Recommendation Agent. |
| `ML_API_URL` | Yes for remote integration | Base URL for the forecasting API. |

The current Groq model is configured in `config.py` as
`openai/gpt-oss-120b`. Change it only after confirming that the target Groq
account has access to the replacement model.

## Development principles

- Keep numerical calculations in deterministic Python services.
- Pass calculated evidence to agents instead of asking agents to recompute it.
- Validate external and agent responses with the schemas in `schemas/`.
- Treat recommendations as evidence-based suggestions, not guaranteed savings.
- Keep temporary optimization behavior clearly labeled until a production
       optimization engine is integrated.
- Never commit `.env`, API keys, credentials, virtual environments, caches, or
  generated editor files.
- Add or update a focused validation check when changing a service contract.
- Use small conventional commits that describe one logical development stage.

## Integration boundaries

- The forecasting API is an external dependency accessed through
       `ForecastClient`.
- Historical analysis, agent reasoning, recommendation output, and FastAPI
       orchestration are maintained in this repository.
- The optimizer is currently a replaceable simulation boundary.

Changes across these boundaries should preserve the API and schema contracts
before implementation.