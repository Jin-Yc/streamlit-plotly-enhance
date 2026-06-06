import plotly.graph_objects as go
import streamlit as st

from streamlit_plotly_enhance import plotly_cell_events

st.title("Contour events")

fig = go.Figure(
    go.Contour(
        z=[[1, 2, 3], [2, 4, 6], [3, 6, 9]],
        x=["A", "B", "C"],
        y=["row-1", "row-2", "row-3"],
        name="contour",
    )
)

event = plotly_cell_events(fig, events=("click", "hover", "relayout"), key="contour-basic")
st.json(event or {})
