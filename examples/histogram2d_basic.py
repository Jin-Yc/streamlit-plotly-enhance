import plotly.graph_objects as go
import streamlit as st

from streamlit_plotly_enhance import plotly_cell_events

st.title("Histogram2d events")

fig = go.Figure(
    go.Histogram2d(
        x=[1, 1, 2, 2, 3, 3, 4],
        y=[1, 2, 1, 2, 3, 4, 4],
        name="histogram2d",
    )
)

event = plotly_cell_events(fig, events=("click", "relayout"), key="histogram2d-basic")
st.json(event or {})
