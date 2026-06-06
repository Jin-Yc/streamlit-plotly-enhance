import plotly.express as px
import streamlit as st

from streamlit_plotly_enhance import plotly_cell_events

st.title("px.imshow cell events")

fig = px.imshow(
    [[0.1, 0.4, 0.9], [0.2, 0.6, 0.8]],
    x=["A", "B", "C"],
    y=["row-1", "row-2"],
)

event = plotly_cell_events(fig, events=("click",), key="imshow-basic")
st.json(event or {})
