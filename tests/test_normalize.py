from streamlit_plotly_enhance._normalize import normalize_component_event, validate_events


def test_validate_events_deduplicates_and_normalizes():
    assert validate_events(["click", "CLICK", "hover"]) == ("click", "hover")


def test_validate_events_rejects_unknown_event():
    try:
        validate_events(["click", "selected"])
    except ValueError as exc:
        assert "selected" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_normalize_heatmap_point_numbers():
    payload = {
        "event": "click",
        "plotly_event": "plotly_click",
        "points": [
            {
                "curveNumber": 0,
                "pointNumber": 4,
                "pointNumbers": [1, 1],
                "x": "B",
                "y": "row-2",
                "traceType": "heatmap",
                "traceName": "matrix",
                "trace": {"type": "heatmap", "name": "matrix", "z": [[1, 2, 3], [4, 5, 6]]},
            }
        ],
    }

    event = normalize_component_event(payload)

    assert event is not None
    assert event["event"] == "click"
    assert event["trace_type"] == "heatmap"
    point = event["points"][0]
    assert point["row"] == 1
    assert point["col"] == 1
    assert point["z"] == 5
    assert point["value"] == 5


def test_normalize_flat_point_number_from_z_shape():
    payload = {
        "event": "click",
        "plotly_event": "plotly_click",
        "points": [
            {
                "pointNumber": 5,
                "trace": {"type": "heatmap", "z": [[1, 2, 3], [4, 5, 6]]},
            }
        ],
    }

    event = normalize_component_event(payload)

    point = event["points"][0]
    assert point["row"] == 1
    assert point["col"] == 2
    assert point["z"] == 6


def test_normalize_heatmap_row_col_from_axis_values():
    payload = {
        "event": "click",
        "plotly_event": "plotly_click",
        "points": [
            {
                "x": "A",
                "y": "row-2",
                "z": 4,
                "traceType": "heatmap",
                "trace": {
                    "type": "heatmap",
                    "x": ["A", "B", "C"],
                    "y": ["row-1", "row-2"],
                    "z": [[1, 2, 3], [4, 5, 6]],
                },
            }
        ],
    }

    event = normalize_component_event(payload)

    point = event["points"][0]
    assert point["row"] == 1
    assert point["col"] == 0
    assert point["z"] == 4


def test_normalize_relayout_event():
    payload = {
        "event": "relayout",
        "plotly_event": "plotly_relayout",
        "points": [],
        "relayout": {"xaxis.range[0]": 1, "xaxis.range[1]": 10},
    }

    event = normalize_component_event(payload)

    assert event["points"] == []
    assert event["relayout"] == {"xaxis.range[0]": 1, "xaxis.range[1]": 10}
