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
