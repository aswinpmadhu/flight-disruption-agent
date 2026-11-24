"""Health endpoint tests (run through FastAPI's TestClient, which uses HTTPX)."""

import logging

import pytest
from fastapi.testclient import TestClient

from flight_agent.config import API_KEY_ENV_VAR, load_settings
from flight_agent.main import create_app

FAKE_KEY = "sk-ant-test-0123456789"


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_works_without_an_api_key(client: TestClient) -> None:
    # The `client` fixture is built from settings with no ANTHROPIC_API_KEY.
    assert client.app.state.settings.anthropic_api_key is None
    assert client.get("/health").status_code == 200


def test_health_never_reveals_the_api_key() -> None:
    settings = load_settings(environ={API_KEY_ENV_VAR: FAKE_KEY})
    with TestClient(create_app(settings)) as keyed_client:
        response = keyed_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert FAKE_KEY not in response.text
    assert FAKE_KEY not in str(response.headers)


def test_api_key_never_appears_in_openapi_docs_or_logs(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    # The key comes from the real environment path, as it does under uvicorn.
    monkeypatch.setenv(API_KEY_ENV_VAR, FAKE_KEY)
    caplog.set_level(logging.DEBUG)
    with TestClient(create_app()) as keyed_client:
        responses = [
            keyed_client.get("/health"),
            keyed_client.get("/openapi.json"),
            keyed_client.get("/docs"),
        ]
    for response in responses:
        assert response.status_code == 200
        assert FAKE_KEY not in response.text
        assert FAKE_KEY not in str(response.headers)
    assert FAKE_KEY not in caplog.text


def test_unknown_route_returns_404(client: TestClient) -> None:
    assert client.get("/does-not-exist").status_code == 404


def test_health_rejects_post(client: TestClient) -> None:
    assert client.post("/health").status_code == 405
