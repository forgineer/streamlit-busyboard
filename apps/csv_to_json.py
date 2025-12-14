import io
import json
import html as _html
from typing import Any, Dict, List

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


def _ensure_state():
    if "csv_input" not in st.session_state:
        st.session_state.csv_input = ""
    if "observe_nested" not in st.session_state:
        st.session_state.observe_nested = False
    if "csv_converted" not in st.session_state:
        st.session_state.csv_converted = False
    if "csv_json_output" not in st.session_state:
        st.session_state.csv_json_output = ""
    if "csv_convert_error" not in st.session_state:
        st.session_state.csv_convert_error = ""
    if "csv_mode" not in st.session_state:
        st.session_state.csv_mode = "CSV File"


def _nest_flat_record(flat: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a flat dictionary with dot-notation keys into a nested dictionary structure.
    
    Keys containing dots (e.g., "address.city") are split and converted into nested objects.
    Keys without dots are kept at the top level.
    
    Args:
        flat: A dictionary with potentially dot-notated keys
        
    Returns:
        A nested dictionary structure
        
    Example:
        >>> flat = {"name": "Alice", "address.city": "NYC", "address.zip": "10001"}
        >>> _nest_flat_record(flat)
        {"name": "Alice", "address": {"city": "NYC", "zip": "10001"}}
        
    Raises:
        ValueError: If a key conflict is detected (e.g., both "address" and "address.city" exist)
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
            if key in nested and isinstance(nested[key], dict):
                raise ValueError(
                    f"Conflict detected: key '{key}' exists as a nested object due to dotted keys, "
                    f"but also appears as a non-dotted key in the same record. "
                    f"Cannot merge these into a consistent structure."
                )
            else:
                nested[key] = value
    return nested


def _records_from_df(df: pd.DataFrame, observe_nested: bool) -> List[Dict[str, Any]]:
    df_clean = df.fillna("")
    records = df_clean.to_dict(orient="records")
    if observe_nested:
        return [_nest_flat_record(r) for r in records]
    return records


def _convert_from_file(file_obj):
    st.session_state.csv_convert_error = ""
    if not file_obj:
        st.session_state.csv_convert_error = "No file uploaded"
        return
    try:
        file_obj.seek(0)
        df = pd.read_csv(file_obj)
        records = _records_from_df(df, st.session_state.observe_nested)
        st.session_state.csv_json_output = json.dumps(records, indent=4)
        st.session_state.csv_converted = True
    except Exception as e:
        st.session_state.csv_convert_error = str(e)


def _convert_from_text():
    st.session_state.csv_convert_error = ""
    txt = st.session_state.get("csv_input", "")
    if not txt or not txt.strip():
        st.session_state.csv_convert_error = "No CSV text provided"
        return
    try:
        df = pd.read_csv(io.StringIO(txt))
        records = _records_from_df(df, st.session_state.observe_nested)
        st.session_state.csv_json_output = json.dumps(records, indent=4)
        st.session_state.csv_converted = True
    except Exception as e:
        st.session_state.csv_convert_error = str(e)


def render():
    st.title("CSV → JSON Records")
    _ensure_state()
    # Reset page-specific state when navigating to this page from another page
    page_id = "csv_to_json"
    if st.session_state.get("last_rendered_page") != page_id:
        st.session_state.csv_converted = False
    if not st.session_state.csv_converted:
        mode = st.radio(
            "Input mode",
            ["CSV File", "CSV Text"],
            index=0 if st.session_state.csv_mode == "CSV File" else 1,
            key="csv_mode",
        )

        st.checkbox("Observe Nested Structures", key="observe_nested")

        if mode == "CSV File":
            col_left, col_right = st.columns([4, 6])
            with col_left:
                uploaded = st.file_uploader("Upload CSV file", type=["csv"], key="csv_file")
                st.write("")
                st.button("Convert CSV", on_click=_convert_from_file, args=(uploaded,), key="btn_convert_file", type="primary")

        else:
            st.text_area("Paste CSV text here", height=320, key="csv_input")
            st.button("Convert CSV", on_click=_convert_from_text, key="btn_convert_text", type="primary")

        if st.session_state.csv_convert_error:
            st.error(st.session_state.csv_convert_error)

    else:
        if st.session_state.csv_json_output:
            st.subheader("JSON Records")
            json_text = st.session_state.csv_json_output
            escaped = _html.escape(json_text)
            html = f"""
            <div>
              <textarea id="jsonBox" style="width:100%;height:420px;">{escaped}</textarea>
              <div style="margin-top:8px;">
                <button onclick="navigator.clipboard.writeText(document.getElementById('jsonBox').value)">Copy JSON</button>
              </div>
            </div>
            """
            components.html(html, height=500)
            st.download_button(
                label="Download JSON",
                data=json_text,
                file_name="converted.json",
                mime="application/json"
            )

        def _go_back():
            st.session_state.csv_converted = False

        st.button("Back", on_click=_go_back, type="primary")

    # mark this page as the last rendered so other pages can detect navigation
    st.session_state.last_rendered_page = page_id


if __name__ == "__main__":
    render()
