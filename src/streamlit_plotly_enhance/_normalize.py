from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from streamlit_plotly_enhance._types import CellEvent

EVENT_TO_PLOTLY_EVENT = {
    "click": "plotly_click",
    "hover": "plotly_hover",
    "unhover": "plotly_unhover",
    "relayout": "plotly_relayout",
}

SUPPORTED_EVENTS = frozenset(EVENT_TO_PLOTLY_EVENT)


def validate_events(events: Sequence[str]) -> tuple[str, ...]:
    normalized = tuple(dict.fromkeys(str(event).strip().lower() for event in events))
    invalid = sorted(event for event in normalized if event not in SUPPORTED_EVENTS)
    if invalid:
        allowed = ", ".join(sorted(SUPPORTED_EVENTS))
        raise ValueError(f"Unsupported Plotly cell event(s): {invalid}. Allowed events: {allowed}.")
    if not normalized:
        raise ValueError("At least one event must be provided.")
    return normalized


def normalize_component_event(payload: Any, *, include_raw: bool = False) -> CellEvent | None:
    if not isinstance(payload, Mapping):
        return None

    event_name = _as_str(payload.get("event"))
    plotly_event = _as_str(payload.get("plotly_event"))
    relayout = payload.get("relayout")

    raw_points = payload.get("points")
    points = [_normalize_point(point) for point in raw_points] if isinstance(raw_points, list) else []
    trace_type = _first_trace_type(points)

    result: CellEvent = {
        "event": event_name or _event_from_plotly_event(plotly_event),
        "plotly_event": plotly_event,
        "trace_type": trace_type,
        "points": points,
        "relayout": dict(relayout) if isinstance(relayout, Mapping) else None,
    }
    if include_raw:
        raw = payload.get("raw")
        result["raw"] = dict(raw) if isinstance(raw, Mapping) else dict(payload)
    return result


def _normalize_point(point: Any) -> dict[str, Any]:
    if not isinstance(point, Mapping):
        point = {}

    curve_number = _as_int(point.get("curveNumber"))
    point_number = _as_int(point.get("pointNumber"))
    point_numbers = _as_int_list(point.get("pointNumbers"))
    trace = point.get("trace") if isinstance(point.get("trace"), Mapping) else {}
    trace_type = _as_str(point.get("traceType")) or _as_str(trace.get("type"))
    trace_name = _as_str(point.get("traceName")) or _as_str(trace.get("name"))
    x = _json_value(point.get("x"))
    y = _json_value(point.get("y"))

    z_matrix = trace.get("z")
    row, col = _infer_row_col(
        point_numbers=point_numbers,
        point_number=point_number,
        z_matrix=z_matrix,
    )
    if row is None or col is None:
        row, col = _infer_row_col_from_axes(
            x=x,
            y=y,
            trace_x=trace.get("x"),
            trace_y=trace.get("y"),
        )

    z = point.get("z", None)
    if z is None and row is not None and col is not None:
        z = _matrix_get(z_matrix, row, col)

    return {
        "curve_number": curve_number,
        "point_number": point_number,
        "point_numbers": point_numbers,
        "row": row,
        "col": col,
        "x": x,
        "y": y,
        "z": _json_value(z),
        "value": _json_value(z),
        "customdata": _json_value(point.get("customdata")),
        "text": _json_value(point.get("text")),
        "trace_name": trace_name,
        "trace_type": trace_type,
    }


def _infer_row_col(
    *,
    point_numbers: list[int] | None,
    point_number: int | None,
    z_matrix: Any,
) -> tuple[int | None, int | None]:
    if point_numbers and len(point_numbers) >= 2:
        return point_numbers[0], point_numbers[1]

    if point_number is None:
        return None, None

    n_cols = _matrix_col_count(z_matrix)
    if n_cols is None or n_cols <= 0:
        return None, None
    return point_number // n_cols, point_number % n_cols


def _matrix_col_count(value: Any) -> int | None:
    if not _is_sequence(value):
        return None
    for row in value:
        if _is_sequence(row):
            return len(row)
    return None


def _matrix_get(value: Any, row: int, col: int) -> Any:
    try:
        return value[row][col]
    except (IndexError, KeyError, TypeError):
        return None


def _infer_row_col_from_axes(
    *,
    x: Any,
    y: Any,
    trace_x: Any,
    trace_y: Any,
) -> tuple[int | None, int | None]:
    col = _sequence_index(trace_x, x)
    row = _sequence_index(trace_y, y)
    return row, col


def _sequence_index(sequence: Any, value: Any) -> int | None:
    if not _is_sequence(sequence):
        return None
    for index, item in enumerate(sequence):
        if item == value:
            return index
    return None


def _as_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None


def _as_int_list(value: Any) -> list[int] | None:
    if not _is_sequence(value):
        return None
    items = [_as_int(item) for item in value]
    if any(item is None for item in items):
        return None
    return [item for item in items if item is not None]


def _as_str(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _event_from_plotly_event(plotly_event: str) -> str:
    for event, mapped in EVENT_TO_PLOTLY_EVENT.items():
        if plotly_event == mapped:
            return event
    return ""


def _first_trace_type(points: list[dict[str, Any]]) -> str | None:
    for point in points:
        trace_type = point.get("trace_type")
        if isinstance(trace_type, str) and trace_type:
            return trace_type
    return None


def _json_value(value: Any) -> Any:
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def _is_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray))
