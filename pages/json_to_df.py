import json
import pandas as pd
import streamlit as st


def parse_json_to_df(raw_text: str, normalize: bool = True) -> pd.DataFrame:
    """
    Parse a JSON string and convert it to a pandas DataFrame.

    This function handles various JSON structures, including:
    - A dictionary where all values are lists (e.g., column-oriented JSON).
    - A single dictionary representing one record.
    - A list of dictionaries (records).

    The `normalize` parameter controls whether to use `pd.json_normalize` for flattening nested data.

    Parameters
    ----------
    raw_text : str
        The JSON string to parse. Must not be empty.
    normalize : bool, optional
        If True (default), use `pandas.json_normalize` to flatten nested structures.
        If False, use `pandas.DataFrame` directly where possible.

    Returns
    -------
    pd.DataFrame
        The resulting DataFrame parsed from the JSON input.

    Raises
    ------
    ValueError
        If the input string is empty or only whitespace.
    json.JSONDecodeError
        If the input string is not valid JSON.

    Notes
    -----
    - If the input is a dict with all list values and `normalize` is True, uses `pd.json_normalize`.
    - If the input is a dict with all list values and `normalize` is False, uses `pd.DataFrame`.
    - If the input is a single dict, wraps it in a list.
    - If the input is a list of dicts, uses `pd.json_normalize` or `pd.DataFrame` depending on `normalize`.
    - If DataFrame construction fails, falls back to `pd.json_normalize`.
    """
    raw_text = raw_text.strip()
    if not raw_text:
        raise ValueError("No JSON provided")

    data = json.loads(raw_text)

    if isinstance(data, dict):
        if all(isinstance(v, list) for v in data.values()):
            if normalize:
                return pd.json_normalize(data)
            return pd.DataFrame(data)
        data = [data]

    if normalize:
        return pd.json_normalize(data)

    try:
        return pd.DataFrame(data)
    except Exception:
        return pd.json_normalize(data)


def _ensure_state():
    if "json_input" not in st.session_state:
        st.session_state.json_input = """[
  {"name": "Alice", "age": 30, "email": "alice@example.com", "address": {"line1": "123 Main St", "line2": "Apt 1", "city": "New York", "state": "NY", "zip": "10001"}},
  {"name": "Bob", "age": 25, "email": "bob@example.com", "address": {"line1": "456 Market Ave", "line2": "", "city": "San Francisco", "state": "CA", "zip": "94105"}},
  {"name": "Carol", "age": 42, "email": "carol@example.com", "address": {"line1": "789 Oak Dr", "line2": "Suite 200", "city": "Chicago", "state": "IL", "zip": "60611"}},
  {"name": "Dave", "age": 35, "email": "dave@example.com", "address": {"line1": "12 Pine Rd", "line2": "", "city": "Seattle", "state": "WA", "zip": "98101"}},
  {"name": "Eve", "age": 29, "email": "eve@example.com", "address": {"line1": "34 Elm St", "line2": "Floor 3", "city": "Boston", "state": "MA", "zip": "02108"}},
  {"name": "Frank", "age": 51, "email": "frank@example.com", "address": {"line1": "678 Cedar Ln", "line2": "Unit B", "city": "Denver", "state": "CO", "zip": "80202"}},
  {"name": "Grace", "age": 24, "email": "grace@example.com", "address": {"line1": "90 Birch Blvd", "line2": "", "city": "Austin", "state": "TX", "zip": "73301"}},
  {"name": "Heidi", "age": 38, "email": "heidi@example.com", "address": {"line1": "210 Maple Ave", "line2": "Apt 5C", "city": "Portland", "state": "OR", "zip": "97205"}},
  {"name": "Ivan", "age": 46, "email": "ivan@example.com", "address": {"line1": "321 Spruce St", "line2": "", "city": "Miami", "state": "FL", "zip": "33101"}},
  {"name": "Judy", "age": 33, "email": "judy@example.com", "address": {"line1": "555 Walnut Rd", "line2": "Suite 10", "city": "Atlanta", "state": "GA", "zip": "30303"}}
]"""
    if "normalize" not in st.session_state:
        st.session_state.normalize = True
    if "converted" not in st.session_state:
        st.session_state.converted = False
    if "df" not in st.session_state:
        st.session_state.df = None
    if "convert_error" not in st.session_state:
        st.session_state.convert_error = ""


def do_convert():
    try:
        df = parse_json_to_df(st.session_state.json_input, normalize=st.session_state.normalize)
        st.session_state.df = df
        st.session_state.converted = True
        st.session_state.convert_error = ""
    except Exception as e:
        st.session_state.convert_error = str(e)


def go_back():
    st.session_state.converted = False


def render():
    st.title("JSON → DataFrame Converter")
    _ensure_state()

    # Use Streamlit's built-in `type` parameter on buttons below

    if not st.session_state.converted:
        controls_col1, controls_col2 = st.columns([1, 1])
        with controls_col1:
            st.checkbox("Normalize JSON (use json_normalize)", key="normalize")
        with controls_col2:
            st.button("Convert JSON", on_click=do_convert, type="primary")

        st.text_area(
            "Paste JSON records here",
            value=st.session_state.json_input,
            height=600,
            key="json_input",
        )

        if st.session_state.convert_error:
            st.error(f"Failed to parse JSON: {st.session_state.convert_error}")

    else:
        df = st.session_state.df
        if df is not None:
            st.dataframe(df, use_container_width=True)
            csv_bytes = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Download CSV",
                csv_bytes,
                file_name="converted.csv",
                mime="text/csv",
                type="secondary",
            )

        st.button("Back", on_click=go_back, type="primary")
