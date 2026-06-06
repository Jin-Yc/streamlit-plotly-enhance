from __future__ import annotations

from typing import Any, Literal, NotRequired, TypedDict

SupportedEvent = Literal["click", "hover", "unhover", "relayout"]


class CellEventPoint(TypedDict):
    curve_number: int | None
    point_number: int | None
    point_numbers: list[int] | None
    row: int | None
    col: int | None
    x: Any
    y: Any
    z: Any
    value: Any
    customdata: Any
    text: Any
    trace_name: str | None
    trace_type: str | None


class CellEvent(TypedDict):
    event: str
    plotly_event: str
    trace_type: str | None
    points: list[CellEventPoint]
    relayout: dict[str, Any] | None
    raw: NotRequired[dict[str, Any]]
