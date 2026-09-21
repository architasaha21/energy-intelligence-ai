from fastapi import FastAPI

from api.routes import router


app = FastAPI(
    title="AI Energy Intelligence API",
    description=(
        "AI agents for energy analysis, "
        "optimization and recommendations."
    ),
    version="1.0.0"
)


# Register all agent endpoints
app.include_router(router)


@app.get("/")
def root():
    """
    Basic health check.
    """

    return {
        "message": "AI Energy Intelligence API is running"
    }