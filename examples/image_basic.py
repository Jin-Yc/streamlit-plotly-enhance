import plotly.graph_objects as go
import streamlit as st

from streamlit_plotly_enhance import plotly_cell_events

st.title("Image cell events")

fig = go.Figure(
    go.Image(
        z=[
            [[255, 0, 0], [0, 255, 0]],
            [[0, 0, 255], [255, 255, 0]],
        ]
    )
)

event = plotly_cell_events(fig, events=("click",), key="image-basic")
st.json(event or {})
