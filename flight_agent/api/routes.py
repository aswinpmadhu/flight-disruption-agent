"""API routes. Phase 1 has only the health check; /v1/chat comes with the agent."""

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Liveness check. It reports nothing about configuration or secrets."""
    return HealthResponse()
