"""Settings tests: path resolution, strict validation and API key handling."""

import tomllib
from pathlib import Path

import pytest
from pydantic import SecretStr, ValidationError

import flight_agent
from flight_agent.config import (
    API_KEY_ENV_VAR,
    DEFAULT_CONFIG_PATH,
    PROJECT_ROOT,
    load_settings,
)
from flight_agent.main import create_app

FAKE_KEY = "sk-ant-test-0123456789"


def _write_config(
    tmp_path: Path, prefix: str = "", extra: str = "", agent_extra: str = ""
) -> Path:
    """Write a copy of the real settings file with optional additions.

    ``prefix`` is placed before the first table, so its keys are top-level.
    ``extra`` is appended at the end, ``agent_extra`` goes inside ``[agent]``.
    """
    text = DEFAULT_CONFIG_PATH.read_text(encoding="utf-8")
    text = text.replace("[agent]\n", f"[agent]\n{agent_extra}", 1)
    path = tmp_path / "settings.toml"
    path.write_text(prefix + text + extra, encoding="utf-8")
    return path


def test_default_config_path_is_absolute_and_exists() -> None:
    assert DEFAULT_CONFIG_PATH.is_absolute()
    assert DEFAULT_CONFIG_PATH.parent.name == "config"
    assert DEFAULT_CONFIG_PATH.is_file()


def test_settings_load_independent_of_working_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    settings = load_settings(environ={})
    assert settings.agent.max_tool_rounds == 8


def test_approved_values_are_loaded() -> None:
    settings = load_settings(environ={})
    assert settings.agent.max_tool_rounds == 8
    assert settings.agent.temperature == 0.2
    assert settings.session.idle_timeout_minutes == 30
    assert settings.search.mct_minutes == 60
    assert settings.search.window_hours == 24
    assert settings.search.same_cabin_only is True
    assert settings.search.max_options == 3
    assert settings.retrieval.top_k == 3
    assert settings.reply_filter.max_chars == 300


def _assert_single_error(
    exc_info: pytest.ExceptionInfo[ValidationError],
    expected_type: str,
    expected_loc: tuple[str, ...],
) -> None:
    """Check there is exactly one error, of the expected type and location."""
    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]["type"] == expected_type
    assert errors[0]["loc"] == expected_loc


def test_unmodified_copy_of_the_config_loads(tmp_path: Path) -> None:
    # Positive control: the helper's output is valid until something is added,
    # so the rejection tests below fail for the reason they claim to test.
    path = _write_config(tmp_path)
    assert load_settings(config_path=path, environ={}) == load_settings(environ={})


def test_unknown_field_in_a_section_is_rejected(tmp_path: Path) -> None:
    path = _write_config(tmp_path, agent_extra="unknown_setting = 1\n")
    with pytest.raises(ValidationError) as exc_info:
        load_settings(config_path=path, environ={})
    _assert_single_error(exc_info, "extra_forbidden", ("agent", "unknown_setting"))


def test_unknown_top_level_section_is_rejected(tmp_path: Path) -> None:
    path = _write_config(tmp_path, extra="\n[surprise]\nvalue = 1\n")
    with pytest.raises(ValidationError) as exc_info:
        load_settings(config_path=path, environ={})
    _assert_single_error(exc_info, "extra_forbidden", ("surprise",))


def test_api_key_in_the_toml_file_is_rejected(tmp_path: Path) -> None:
    path = _write_config(tmp_path, prefix=f'anthropic_api_key = "{FAKE_KEY}"\n')
    with pytest.raises(ValidationError) as exc_info:
        load_settings(config_path=path, environ={})
    _assert_single_error(exc_info, "extra_forbidden", ("anthropic_api_key",))


def test_rejected_api_key_is_not_echoed_in_the_error(tmp_path: Path) -> None:
    path = _write_config(tmp_path, prefix=f'anthropic_api_key = "{FAKE_KEY}"\n')
    with pytest.raises(ValidationError) as exc_info:
        load_settings(config_path=path, environ={})
    # str() and repr() are what end up in tracebacks and logs.
    assert FAKE_KEY not in str(exc_info.value)
    assert FAKE_KEY not in repr(exc_info.value)


def test_api_key_is_optional() -> None:
    assert load_settings(environ={}).anthropic_api_key is None


def test_blank_api_key_is_treated_as_missing() -> None:
    assert load_settings(environ={API_KEY_ENV_VAR: "   "}).anthropic_api_key is None


def test_api_key_comes_from_the_environment_as_secretstr() -> None:
    settings = load_settings(environ={API_KEY_ENV_VAR: FAKE_KEY})
    assert isinstance(settings.anthropic_api_key, SecretStr)
    assert settings.anthropic_api_key.get_secret_value() == FAKE_KEY


def test_os_environ_key_is_used_by_create_app(monkeypatch: pytest.MonkeyPatch) -> None:
    # No environ dict is passed anywhere: this is the path `uvicorn --factory` uses.
    monkeypatch.setenv(API_KEY_ENV_VAR, FAKE_KEY)
    api_key = create_app().state.settings.anthropic_api_key
    assert isinstance(api_key, SecretStr)
    assert api_key.get_secret_value() == FAKE_KEY


def test_os_environ_without_key_gives_none(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(API_KEY_ENV_VAR, raising=False)
    assert create_app().state.settings.anthropic_api_key is None


def test_load_settings_reads_os_environ_by_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(API_KEY_ENV_VAR, FAKE_KEY)
    assert load_settings().anthropic_api_key is not None
    monkeypatch.delenv(API_KEY_ENV_VAR)
    assert load_settings().anthropic_api_key is None


def test_api_key_never_appears_in_representations() -> None:
    settings = load_settings(environ={API_KEY_ENV_VAR: FAKE_KEY})
    assert FAKE_KEY not in repr(settings)
    assert FAKE_KEY not in str(settings)
    assert FAKE_KEY not in settings.model_dump_json()
    assert FAKE_KEY not in repr(settings.anthropic_api_key)
    assert FAKE_KEY not in str(settings.anthropic_api_key)


def test_settings_file_contains_no_secrets() -> None:
    text = DEFAULT_CONFIG_PATH.read_text(encoding="utf-8").lower()
    assert "sk-ant" not in text
    assert "anthropic_api_key" not in tomllib.loads(text)


def test_package_version_matches_pyproject() -> None:
    with (PROJECT_ROOT / "pyproject.toml").open("rb") as handle:
        pyproject = tomllib.load(handle)
    assert flight_agent.__version__ == pyproject["project"]["version"]
