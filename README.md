# streamlit-plotly-enhance

Enhanced Plotly interaction helpers for Streamlit Components v2.

`streamlit-plotly-enhance` renders Plotly figures in Streamlit and returns
cell-level interaction events for heatmap-like charts. It is designed for cases
where Streamlit's native `st.plotly_chart` event support is not enough,
especially heatmap cell click events.

## Status

V1 focuses on Plotly heatmap-like charts and click/hover/relayout event
payloads. The package is alpha-stage and intentionally conservative: chart
types that need highly specialized handling may be refined in later versions.

## Installation

From PyPI, after the package is published:

```bash
pip install streamlit-plotly-enhance
```

From GitHub:

```bash
pip install git+https://github.com/Jin-Yc/streamlit-plotly-enhance.git
```

## Quick Start

```python
import plotly.graph_objects as go
import streamlit as st

from streamlit_plotly_enhance import plotly_cell_events

st.title("Heatmap cell events")

fig = go.Figure(
    data=go.Heatmap(
        z=[[1, 2, 3], [4, 5, 6]],
        x=["A", "B", "C"],
        y=["row-1", "row-2"],
        colorscale="Viridis",
        name="basic heatmap",
    )
)

event = plotly_cell_events(fig, events=("click",), key="heatmap-basic")
st.json(event or {})
```

Run the example:

```bash
streamlit run examples/heatmap_basic.py
```

## Event Payload

Clicking the `A / row-2` cell in the quick-start example returns a normalized
payload like:

```python
{
    "event": "click",
    "plotly_event": "plotly_click",
    "trace_type": "heatmap",
    "points": [
        {
            "curve_number": 0,
            "point_number": None,
            "point_numbers": None,
            "row": 1,
            "col": 0,
            "x": "A",
            "y": "row-2",
            "z": 4,
            "value": 4,
            "customdata": None,
            "text": None,
            "trace_name": "basic heatmap",
            "trace_type": "heatmap",
        }
    ],
    "relayout": None,
}
```

## API

```python
plotly_cell_events(
    fig,
    events=("click",),
    *,
    key=None,
    use_container_width=True,
    height=None,
    config=None,
    theme=None,
    raw_event=False,
)
```

Supported V1 events:

- `click`
- `hover`
- `unhover`
- `relayout`

Primary V1 chart targets:

- `heatmap`
- `image`
- common `px.imshow` outputs
- `contour`
- `histogram2d`
- `histogram2dcontour`

`selected` and `selecting` are not V1 guarantees.

## Development

Create a local environment:

```bash
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest
```

Build the frontend:

```bash
cd src/streamlit_plotly_enhance/frontend
npm install
npm run build
```

The generated `src/streamlit_plotly_enhance/frontend/build` files are included
in the Python package so users do not need Node.js at runtime.

## License

MIT
