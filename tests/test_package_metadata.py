from importlib.metadata import version

import streamlit_plotly_enhance


def test_package_exposes_installed_version():
    assert streamlit_plotly_enhance.__version__ == version("streamlit-plotly-enhance")
