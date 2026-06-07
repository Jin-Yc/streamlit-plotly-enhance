import plotly.graph_objects as go
import streamlit as st

from streamlit_plotly_enhance import plotly_cell_events

st.set_page_config(page_title="streamlit-plotly-enhance demo", layout="centered")

st.title("Heatmap cell events")

fig = go.Figure(
    data=go.Heatmap(
        z=[[1, 2, 3], [4, 5, 6]],
        x=["A", "B", "C"],
        y=["row-1", "row-2"],
        colorscale="Viridis",
        name="basic heatmap",
        hovertemplate="x=%{x}<br>y=%{y}<br>value=%{z}<extra></extra>",
    )
)

fig.update_layout(
    height=320,
    margin={"l": 20, "r": 20, "t": 30, "b": 20},
)

st.caption("Native Streamlit Plotly rendering")
st.plotly_chart(fig, width="stretch")

st.caption("Enhanced component with normalized cell events")
event = plotly_cell_events(fig, events=("click",), key="readme-heatmap-demo")
st.json(event or {})
