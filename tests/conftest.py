"""Shared test fixtures."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from flight_agent.config import Settings, load_settings
from flight_agent.main import create_app


@pytest.fixture
def settings_without_key() -> Settings:
    """Real settings.toml, with an empty environment (no API key)."""
    return load_settings(environ={})


@pytest.fixture
def client(settings_without_key: Settings) -> Iterator[TestClient]:
    with TestClient(create_app(settings_without_key)) as test_client:
        yield test_client
