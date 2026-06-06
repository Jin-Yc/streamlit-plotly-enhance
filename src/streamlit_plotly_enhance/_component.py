from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import streamlit as st

from streamlit_plotly_enhance._normalize import normalize_component_event, validate_events
from streamlit_plotly_enhance._types import CellEvent

_component = None


def plotly_cell_events(
    fig: Any,
    events: Sequence[str] = ("click",),
    *,
    key: str | None = None,
    use_container_width: bool = True,
    height: int | None = None,
    config: dict[str, Any] | None = None,
    theme: str | None = None,
    raw_event: bool = False,
) -> CellEvent | None:
    """Render a Plotly figure and return heatmap-like cell events.

    Parameters
    ----------
    fig:
        A Plotly figure or figure-like object with a ``to_plotly_json`` method.
    events:
        Events to listen for. V1 supports ``click``, ``hover``, ``unhover``, and
        ``relayout``. The default is ``("click",)``.
    key:
        Streamlit component key.
    use_container_width:
        If true, mount the component with stretch width.
    height:
        Optional fixed component height in pixels. Defaults to the figure layout
        height or 450.
    config:
        Plotly.js config object.
    theme:
        Reserved for future theme integration.
    raw_event:
        Include the sanitized raw frontend event payload in the return value.
    """
    normalized_events = validate_events(events)
    figure = _figure_to_json(fig)
    resolved_height = _resolve_height(figure, height)

    result = _get_component()(
        data={
            "figure": figure,
            "events": normalized_events,
            "config": config or {},
            "theme": theme,
        },
        key=key,
        width="stretch" if use_container_width else None,
        height=resolved_height,
        on_event_change=lambda: None,
    )
    return normalize_component_event(result.event, include_raw=raw_event)


def _get_component():
    global _component
    if _component is None:
        _component = st.components.v2.component(
            name="streamlit-plotly-enhance.plotly_cell_events",
            js="index-*.js",
            css="style-*.css",
            isolate_styles=False,
        )
    return _component


def _figure_to_json(fig: Any) -> dict[str, Any]:
    if hasattr(fig, "to_plotly_json"):
        value = fig.to_plotly_json()
    elif isinstance(fig, dict):
        value = fig
    else:
        raise TypeError("fig must be a Plotly figure or a figure-like dict.")

    if not isinstance(value, dict):
        raise TypeError("fig.to_plotly_json() must return a dict.")

    value.setdefault("data", [])
    value.setdefault("layout", {})
    return value


def _resolve_height(figure: dict[str, Any], height: int | None) -> int:
    if height is not None:
        if height <= 0:
            raise ValueError("height must be a positive integer.")
        return height

    layout = figure.get("layout")
    if isinstance(layout, dict):
        layout_height = layout.get("height")
        if isinstance(layout_height, int) and layout_height > 0:
            return layout_height
    return 450
