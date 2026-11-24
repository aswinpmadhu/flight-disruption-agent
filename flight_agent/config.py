"""Application settings (docs/03 section 10, NFR-06, FR-37).

Two sources, kept strictly apart:

* ``config/settings.toml`` holds the non-secret settings. Unknown keys are
  rejected, so a typo or a pasted secret fails loudly.
* The Anthropic API key comes **only** from the ``ANTHROPIC_API_KEY``
  environment variable and is held as a ``SecretStr``.
"""

import os
import tomllib
from collections.abc import Mapping
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, SecretStr

# Resolved from this file's location, so it does not depend on the current
# working directory. This assumes the package runs from the repository
# checkout (editable install or running from the repository root).
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "settings.toml"
API_KEY_ENV_VAR = "ANTHROPIC_API_KEY"


class _StrictModel(BaseModel):
    """Base for settings models: unknown fields are errors, instances are read-only.

    ``hide_input_in_errors`` keeps rejected values out of the error text, so a
    secret pasted into the TOML file is not echoed into a traceback or log.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        hide_input_in_errors=True,
    )


class AgentSettings(_StrictModel):
    max_tool_rounds: int = Field(gt=0)
    temperature: float = Field(ge=0.0, le=0.2)


class SessionSettings(_StrictModel):
    idle_timeout_minutes: int = Field(gt=0)


class SearchSettings(_StrictModel):
    mct_minutes: int = Field(ge=0)
    window_hours: int = Field(gt=0)
    same_cabin_only: bool
    max_options: int = Field(gt=0)


class RetrievalSettings(_StrictModel):
    top_k: int = Field(gt=0)


class ReplyFilterSettings(_StrictModel):
    max_chars: int = Field(gt=0)


class FileSettings(_StrictModel):
    """Exactly what ``settings.toml`` may contain. It has no API key field."""

    agent: AgentSettings
    session: SessionSettings
    search: SearchSettings
    retrieval: RetrievalSettings
    reply_filter: ReplyFilterSettings


class Settings(FileSettings):
    """File settings plus the optional API key from the environment.

    The key is a ``SecretStr`` (masked in ``str``/``repr``/JSON) and is excluded
    from ``repr`` entirely. It is optional in Phase 1: the app must start and
    serve ``/health`` without it.
    """

    anthropic_api_key: SecretStr | None = Field(default=None, repr=False)


def load_settings(
    config_path: Path | None = None,
    environ: Mapping[str, str] | None = None,
) -> Settings:
    """Load settings from the TOML file and the environment.

    ``config_path`` and ``environ`` exist so tests can supply their own values.
    """
    path = Path(config_path) if config_path is not None else DEFAULT_CONFIG_PATH
    env = os.environ if environ is None else environ

    with path.open("rb") as handle:
        raw = tomllib.load(handle)

    # Validated against FileSettings first, so an API key (or any unknown key)
    # written into the TOML file is rejected rather than silently accepted.
    file_settings = FileSettings.model_validate(raw)

    api_key = env.get(API_KEY_ENV_VAR, "").strip()
    return Settings(
        **dict(file_settings),
        anthropic_api_key=SecretStr(api_key) if api_key else None,
    )
