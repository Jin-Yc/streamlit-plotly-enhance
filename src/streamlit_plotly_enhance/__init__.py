"""Streamlit helpers for enhanced Plotly cell events."""

from importlib.metadata import PackageNotFoundError, version

from streamlit_plotly_enhance._component import plotly_cell_events
from streamlit_plotly_enhance._types import CellEvent, CellEventPoint

try:
    __version__ = version("streamlit-plotly-enhance")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = ["CellEvent", "CellEventPoint", "__version__", "plotly_cell_events"]
