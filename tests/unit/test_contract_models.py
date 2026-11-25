"""Contract model tests (issue B-01a): immutability, strictness, UTC, flight numbers, DK10 key."""

from datetime import UTC, datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from flight_agent.domain.models import (
    Booking,
    DisruptionType,
    FlightStatus,
    FlightStatusCode,
    Itinerary,
    PolicyPassage,
    PolicySearchResult,
    Segment,
    derive_itinerary_key,
)


def _dt(day: int, hour: int = 8, minute: int = 0) -> datetime:
    return datetime(2026, 12, day, hour, minute, tzinfo=UTC)


def _segment(number: str = "MD101", day: int = 1, hour: int = 8, **overrides) -> Segment:
    data = {
        "flight_number": number,
        "origin": "LHR",
        "destination": "AMS",
        "scheduled_departure": _dt(day, hour),
        "scheduled_arrival": _dt(day, hour) + timedelta(hours=1),
    }
    data.update(overrides)
    return Segment(**data)


def _itinerary(segments, key=None, **overrides) -> Itinerary:
    data = {
        "itinerary_key": derive_itinerary_key(segments) if key is None else key,
        "segments": segments,
        "departure": segments[0].scheduled_departure,
        "arrival": segments[-1].scheduled_arrival,
        "connections": len(segments) - 1,
        "seats_available": 4,
    }
    data.update(overrides)
    return Itinerary(**data)


def test_contract_models_enums_have_the_agreed_members() -> None:
    assert {m.name for m in DisruptionType} == {"CANCELLATION", "MISSED_CONNECTION", "DELAY", "NONE"}
    assert {m.name for m in FlightStatusCode} == {"ON_TIME", "DELAYED", "CANCELLED"}


def test_contract_models_are_immutable() -> None:
    segment = _segment()
    with pytest.raises(ValidationError):
        segment.origin = "FRA"  # type: ignore[misc]


@pytest.mark.parametrize(
    "build",
    [
        lambda: _segment(unknown="x"),
        lambda: Booking(
            pnr="ABC123", passenger_name="Test Passenger", cabin="Economy",
            booking_status="CONFIRMED", segments=[_segment()], extra_field=1,  # type: ignore[call-arg]
        ),
        lambda: FlightStatus(
            status="ON_TIME", scheduled_departure=_dt(1), scheduled_arrival=_dt(1, 9), extra=1,  # type: ignore[call-arg]
        ),
        lambda: PolicyPassage(
            policy_id="POL-CANCEL-01", section_id="s1", section_title="t", citation="POL-CANCEL-01 §1",
            text="x", score=1.0, extra=1,  # type: ignore[call-arg]
        ),
        lambda: PolicySearchResult(passages=[], no_relevant_policy=True, extra=1),  # type: ignore[call-arg]
    ],
)
def test_contract_models_reject_unknown_fields(build) -> None:
    with pytest.raises(ValidationError):
        build()


def test_contract_models_reject_option_id_on_itinerary() -> None:
    segments = (_segment(),)
    with pytest.raises(ValidationError):
        _itinerary(segments, option_id="OPT-1")


def test_contract_models_reject_naive_datetimes() -> None:
    with pytest.raises(ValidationError):
        _segment(scheduled_departure=datetime(2026, 12, 1, 8, 0))
    with pytest.raises(ValidationError):
        FlightStatus(status="ON_TIME", scheduled_departure=_dt(1), scheduled_arrival=datetime(2026, 12, 1, 9))


def test_contract_models_reject_non_utc_datetimes() -> None:
    plus_one = timezone(timedelta(hours=1))
    with pytest.raises(ValidationError):
        _segment(scheduled_departure=datetime(2026, 12, 1, 8, 0, tzinfo=plus_one))


@pytest.mark.parametrize("bad", ["md101", "MD1011", "MD10", "XX101", "MD10A", " MD101", "MD101 ", ""])
def test_contract_models_reject_bad_flight_numbers(bad: str) -> None:
    with pytest.raises(ValidationError):
        _segment(number=bad)


def test_contract_models_accept_a_valid_flight_number() -> None:
    assert _segment(number="MD999").flight_number == "MD999"


def test_contract_models_booking_needs_segments_and_stores_a_tuple() -> None:
    booking = Booking(
        pnr="ABC123", passenger_name="Test Passenger", cabin="Economy",
        booking_status="CONFIRMED", segments=[_segment()],
    )
    assert isinstance(booking.segments, tuple)
    with pytest.raises(ValidationError):
        Booking(pnr="ABC123", passenger_name="x", cabin="Economy", booking_status="CONFIRMED", segments=[])


def test_contract_models_flight_status_accepts_cancelled_without_estimates() -> None:
    status = FlightStatus(status="CANCELLED", scheduled_departure=_dt(1), scheduled_arrival=_dt(1, 9))
    assert status.estimated_departure is None and status.delay_minutes == 0
    with pytest.raises(ValidationError):
        FlightStatus(status="DELAYED", scheduled_departure=_dt(1), scheduled_arrival=_dt(1, 9), delay_minutes=-1)


def test_contract_models_policy_result_flag_matches_passages() -> None:
    passage = PolicyPassage(
        policy_id="POL-CANCEL-01", section_id="s2", section_title="Rebooking",
        citation="POL-CANCEL-01 §2", text="text", score=1.5,
    )
    assert PolicySearchResult(passages=[], no_relevant_policy=True).no_relevant_policy
    assert not PolicySearchResult(passages=[passage], no_relevant_policy=False).no_relevant_policy
    with pytest.raises(ValidationError):
        PolicySearchResult(passages=[], no_relevant_policy=False)
    with pytest.raises(ValidationError):
        PolicySearchResult(passages=[passage], no_relevant_policy=True)


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
def test_contract_models_passage_score_must_be_finite(bad: float) -> None:
    with pytest.raises(ValidationError):
        PolicyPassage(
            policy_id="POL-CANCEL-01", section_id="s2", section_title="Rebooking",
            citation="POL-CANCEL-01 §2", text="text", score=bad,
        )


def test_contract_models_policy_result_holds_at_most_three_passages() -> None:
    passage = PolicyPassage(
        policy_id="POL-CANCEL-01", section_id="s2", section_title="Rebooking",
        citation="POL-CANCEL-01 §2", text="text", score=1.5,
    )
    assert len(PolicySearchResult(passages=[passage] * 3, no_relevant_policy=False).passages) == 3
    with pytest.raises(ValidationError):
        PolicySearchResult(passages=[passage] * 4, no_relevant_policy=False)


# ---- DK10 itinerary_key -----------------------------------------------------------------


def test_contract_models_key_one_segment() -> None:
    assert derive_itinerary_key([_segment("MD101", day=1)]) == "MD101:2026-12-01"


def test_contract_models_key_two_segments_same_date() -> None:
    segments = [_segment("MD101", day=1, hour=6), _segment("MD205", day=1, hour=12)]
    assert derive_itinerary_key(segments) == "MD101:2026-12-01+MD205:2026-12-01"


def test_contract_models_key_two_segments_across_midnight() -> None:
    segments = [_segment("MD101", day=1, hour=22), _segment("MD205", day=2, hour=6)]
    assert derive_itinerary_key(segments) == "MD101:2026-12-01+MD205:2026-12-02"


def test_contract_models_key_depends_only_on_flight_number_and_scheduled_departure_date() -> None:
    base = _segment("MD101", day=1, hour=23)
    # Same flight, same scheduled departure date: arrival (next UTC day), airports and time of day do not matter.
    other = _segment(
        "MD101", day=1, hour=2, origin="JFK", destination="FRA",
        scheduled_arrival=_dt(2, 5),
    )
    assert derive_itinerary_key([base]) == derive_itinerary_key([other]) == "MD101:2026-12-01"
    # A different scheduled departure date or flight number changes the key.
    assert derive_itinerary_key([_segment("MD101", day=2)]) == "MD101:2026-12-02"
    assert derive_itinerary_key([_segment("MD102", day=1)]) == "MD102:2026-12-01"


def test_contract_models_key_is_pure_and_deterministic() -> None:
    segments = (_segment("MD101"), _segment("MD205", day=2))
    assert derive_itinerary_key(segments) == derive_itinerary_key(list(segments))


def test_contract_models_key_needs_at_least_one_segment() -> None:
    with pytest.raises(ValueError):
        derive_itinerary_key([])


def test_contract_models_itinerary_accepts_the_derived_key() -> None:
    segments = (_segment("MD101", day=1, hour=22), _segment("MD205", day=2, hour=6))
    itinerary = _itinerary(segments)
    assert itinerary.itinerary_key == "MD101:2026-12-01+MD205:2026-12-02"
    assert itinerary.connections == 1


@pytest.mark.parametrize(
    "wrong",
    ["MD101:2026-12-02", "MD102:2026-12-01", "md101:2026-12-01", "MD101:2026-12-01+MD205:2026-12-01", ""],
)
def test_contract_models_mismatched_key_is_rejected(wrong: str) -> None:
    segments = (_segment("MD101", day=1),)
    with pytest.raises(ValidationError):
        _itinerary(segments, key=wrong)


def test_contract_models_validator_never_replaces_a_supplied_key() -> None:
    segments = (_segment("MD101", day=1),)
    itinerary = _itinerary(segments)
    assert itinerary.itinerary_key == "MD101:2026-12-01"
    with pytest.raises(ValidationError):
        _itinerary(segments, key="MD101:2026-12-01 ")  # not repaired or trimmed
