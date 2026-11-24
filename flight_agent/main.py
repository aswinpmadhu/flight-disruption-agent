"""FastAPI application factory.

Run with a single worker and no auto-reload, because sessions will be held in
memory (docs/03 R10):

    uvicorn flight_agent.main:create_app --factory --port 8000
"""

from fastapi import FastAPI

from flight_agent import __version__
from flight_agent.api.routes import router
from flight_agent.config import Settings, load_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build the application. Pass ``settings`` in tests; otherwise load them."""
    app = FastAPI(
        title="AI Flight Disruption Recovery Agent",
        version=__version__,
    )
    app.state.settings = settings if settings is not None else load_settings()
    app.include_router(router)
    return app
