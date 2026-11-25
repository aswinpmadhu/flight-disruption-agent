"""Shared domain models and enums (docs/03 sections 4, 5.4, 5.6; issue B-01a).

These are the contract types every other component codes against. They are
validation-only: no business rules and no I/O.

* Pydantic v2, frozen, ``extra="forbid"``.
* Every datetime is timezone-aware and in UTC (T7).
* ``itinerary_key`` follows the approved key contract (DK10):
  ``<flight_number>:<YYYY-MM-DD>`` per segment, in travel order, joined with
  ``+``. The date is the **scheduled departure UTC date** of the segment, never
  the estimated departure.

Roles for ``itinerary_key``, exactly:

* This module defines the pure helper :func:`derive_itinerary_key` and the
  ``Itinerary`` validator.
* The validator uses the helper **only to verify** a supplied key: it compares
  the derived string with the supplied string and rejects a difference. It never
  parses a key and never replaces a supplied key.
* ``flight_agent/services/alternatives.py`` (B-08a) is the only production
  component that constructs a key. No other component constructs or parses one.

The delay and missed-connection enum values are dormant contract values: they
carry no behaviour here.
"""

from collections.abc import Sequence
from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated

from pydantic import (
    AfterValidator,
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


class DisruptionType(StrEnum):
    CANCELLATION = "CANCELLATION"
    MISSED_CONNECTION = "MISSED_CONNECTION"
    DELAY = "DELAY"
    NONE = "NONE"


class FlightStatusCode(StrEnum):
    ON_TIME = "ON_TIME"
    DELAYED = "DELAYED"
    CANCELLED = "CANCELLED"


def _require_utc(value: datetime) -> datetime:
    offset = value.utcoffset()
    if offset is None or offset.total_seconds() != 0:
        raise ValueError("datetime must be timezone-aware and in UTC (T7)")
    return value


UtcDatetime = Annotated[AwareDatetime, AfterValidator(_require_utc)]

FLIGHT_NUMBER_PATTERN = r"^MD[0-9]{3}$"
FlightNumber = Annotated[str, Field(pattern=FLIGHT_NUMBER_PATTERN)]


class _Frozen(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Segment(_Frozen):
    """One flight leg.

    ``scheduled_departure`` is a UTC datetime. Its UTC calendar date is the
    ``date`` used by ``get_flight_status(flight_number, date)`` and in the
    ``itinerary_key``. It is the scheduled date, never the estimated one.
    """

    flight_number: FlightNumber
    origin: str = Field(min_length=1)
    destination: str = Field(min_length=1)
    scheduled_departure: UtcDatetime
    scheduled_arrival: UtcDatetime


class Booking(_Frozen):
    pnr: str = Field(min_length=1)
    passenger_name: str = Field(min_length=1)
    cabin: str = Field(min_length=1)
    booking_status: str = Field(min_length=1)
    segments: tuple[Segment, ...] = Field(min_length=1)


class FlightStatus(_Frozen):
    """Status of one flight.

    The ``display`` time strings are produced by the B-16a handler and are not
    stored here.
    """

    status: FlightStatusCode
    scheduled_departure: UtcDatetime
    scheduled_arrival: UtcDatetime
    estimated_departure: UtcDatetime | None = None
    estimated_arrival: UtcDatetime | None = None
    delay_minutes: int = Field(default=0, ge=0)


def derive_itinerary_key(segments: Sequence[Segment]) -> str:
    """Return the DK10 key for ``segments``. Pure: no I/O, clock or randomness.

    Per segment: ``<flight_number>:<YYYY-MM-DD>`` using the scheduled departure
    UTC date; segments in the given (travel) order, joined with ``+``.
    """
    if not segments:
        raise ValueError("an itinerary needs at least one segment")
    return "+".join(
        f"{segment.flight_number}:"
        f"{segment.scheduled_departure.astimezone(UTC).date().isoformat()}"
        for segment in segments
    )


class Itinerary(_Frozen):
    """A complete alternative itinerary (no ``option_id``: the app's option map assigns it)."""

    itinerary_key: str
    segments: tuple[Segment, ...] = Field(min_length=1)
    departure: UtcDatetime
    arrival: UtcDatetime
    connections: int = Field(ge=0)
    seats_available: int = Field(ge=0)

    @model_validator(mode="after")
    def _verify_itinerary_key(self) -> "Itinerary":
        # Verification only: exact string comparison; the key is never parsed or replaced.
        if self.itinerary_key != derive_itinerary_key(self.segments):
            raise ValueError("itinerary_key does not match the key derived from the segments")
        return self


class PolicyPassage(_Frozen):
    policy_id: str = Field(min_length=1)
    section_id: str = Field(min_length=1)
    section_title: str = Field(min_length=1)
    citation: str = Field(min_length=1)
    text: str
    score: float


class PolicySearchResult(_Frozen):
    passages: tuple[PolicyPassage, ...] = Field(max_length=3)
    no_relevant_policy: bool
