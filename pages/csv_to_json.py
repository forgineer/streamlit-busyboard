import io
import json
import urllib.parse
import html as _html
from typing import Any, Dict

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


def _ensure_state():
    if "csv_input" not in st.session_state:
        st.session_state.csv_input = """name,age,email,address.line1,address.line2,address.city,address.state,address.zip
Alice,30,alice@example.com,123 Main St,Apt 1,New York,NY,10001
Bob,25,bob@example.com,456 Market Ave,,San Francisco,CA,94105
Carol,42,carol@example.com,789 Oak Dr,Suite 200,Chicago,IL,60611
"""
    if "observe_nested" not in st.session_state:
        st.session_state.observe_nested = False
    if "converted" not in st.session_state:
        st.session_state.converted = False
    if "json_output" not in st.session_state:
        st.session_state.json_output = ""
    if "convert_error" not in st.session_state:
        st.session_state.convert_error = ""
    if "csv_mode" not in st.session_state:
        st.session_state.csv_mode = "CSV File"


def _nest_flat_record(flat: Dict[str, Any]) -> Dict[str, Any]:
    """Convert flat dict with dot-notation keys into nested dicts.

    Example: {"addr.city": "X", "addr.zip": "Y"} -> {"addr": {"city": "X", "zip": "Y"}}
    """
    nested: Dict[str, Any] = {}
    for key, value in flat.items():
        if "." in key:
            parts = key.split(".")
            cur = nested
            for p in parts[:-1]:
                if p not in cur or not isinstance(cur[p], dict):
                    cur[p] = {}
                cur = cur[p]
            cur[parts[-1]] = value
        else:
            # avoid overwriting previously created nested object
            if key in nested and isinstance(nested[key], dict):
                # keep nested as-is (cannot coerce)
                nested[key]["value"] = value
            else:
                nested[key] = value
    return nested


def _records_from_df(df: pd.DataFrame, observe_nested: bool) -> Any:
    # Replace NaN/NA with empty strings so JSON contains empty strings instead of NaN/null
    df_clean = df.fillna("")
    records = df_clean.to_dict(orient="records")
    if observe_nested:
        return [_nest_flat_record(r) for r in records]
    return records


def _convert_from_file(file_obj):
    st.session_state.convert_error = ""
    if not file_obj:
        st.session_state.convert_error = "No file uploaded"
        return
    try:
        # file_obj is an UploadedFile; read as text
        file_obj.seek(0)
        df = pd.read_csv(file_obj)
        records = _records_from_df(df, st.session_state.observe_nested)
        st.session_state.json_output = json.dumps(records, indent=4)
        st.session_state.converted = True
    except Exception as e:
        st.session_state.convert_error = str(e)


def _convert_from_text():
    st.session_state.convert_error = ""
    txt = st.session_state.get("csv_input", "")
    if not txt or not txt.strip():
        st.session_state.convert_error = "No CSV text provided"
        return
    try:
        df = pd.read_csv(io.StringIO(txt))
        records = _records_from_df(df, st.session_state.observe_nested)
        st.session_state.json_output = json.dumps(records, indent=4)
        st.session_state.converted = True
    except Exception as e:
        st.session_state.convert_error = str(e)


def render():
    st.title("CSV → JSON Records")
    _ensure_state()
    # If not converted, show upload/text entry controls
    if not st.session_state.converted:
        # Mode selector: Upload File or Paste CSV Text
        mode = st.radio(
            "Input mode",
            ["CSV File", "CSV Text"],
            index=0 if st.session_state.csv_mode == "CSV File" else 1,
            key="csv_mode",
        )

        # Observe nested checkbox (present in both modes)
        st.checkbox("Observe Nested Structures", value=st.session_state.observe_nested, key="observe_nested")

        if mode == "CSV File":
            # File upload path: show uploader left-justified in a narrower left column and Convert button beneath it
            col_left, col_right = st.columns([4, 6])
            with col_left:
                uploaded = st.file_uploader("Upload CSV file", type=["csv"], key="csv_file")
                st.write("")
                st.button("Convert CSV", on_click=_convert_from_file, args=(uploaded,), key="btn_convert_file", type="primary")

        else:
            # Text entry path: show large textbox and Convert button below
            st.text_area("Paste CSV text here", value=st.session_state.csv_input, height=320, key="csv_input")
            st.button("Convert CSV", on_click=_convert_from_text, key="btn_convert_text", type="primary")

        if st.session_state.convert_error:
            st.error(st.session_state.convert_error)

    else:
        # Converted: show JSON output and Back button only
        if st.session_state.json_output:
            st.subheader("JSON Records")
            # Render a copy + download UI using an HTML textarea and buttons.
            json_text = st.session_state.json_output
            # Create a data URI for download
            data_uri = "data:application/json;charset=utf-8," + urllib.parse.quote(json_text)
            escaped = _html.escape(json_text)
            html = f"""
            <div>
              <textarea id="jsonBox" style="width:100%;height:420px;">{escaped}</textarea>
              <div style="margin-top:8px;">
                <button onclick="navigator.clipboard.writeText(document.getElementById('jsonBox').value)">Copy JSON</button>
                <a download="converted.json" href="{data_uri}"><button>Download JSON</button></a>
              </div>
            </div>
            """
            components.html(html, height=500)

        def _go_back():
            st.session_state.converted = False

        st.button("Back", on_click=_go_back, type="primary")
