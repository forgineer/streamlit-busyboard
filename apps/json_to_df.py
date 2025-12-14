import json
import pandas as pd
import streamlit as st


def parse_json_to_df(raw_text: str, normalize: bool = True) -> pd.DataFrame:
    raw_text = raw_text.strip()
    if not raw_text:
        raise ValueError("No JSON provided")

    data = json.loads(raw_text)

    if isinstance(data, dict):
        if data and all(isinstance(v, list) for v in data.values()):
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
        st.session_state.json_input = ""
    if "normalize" not in st.session_state:
        st.session_state.normalize = True
    if "json_converted" not in st.session_state:
        st.session_state.json_converted = False
    if "json_df" not in st.session_state:
        st.session_state.json_df = None
    if "json_convert_error" not in st.session_state:
        st.session_state.json_convert_error = ""


def do_convert():
    try:
        df = parse_json_to_df(st.session_state.json_input, normalize=st.session_state.normalize)
        st.session_state.json_df = df
        st.session_state.json_converted = True
        st.session_state.json_convert_error = ""
    except Exception as e:
        st.session_state.json_convert_error = str(e)


def go_back():
    st.session_state.json_converted = False


def render():
    st.title("JSON → DataFrame Converter")
    _ensure_state()

    # Reset page-specific state when navigating to this page from another page
    page_id = "json_to_df"
    if st.session_state.get("last_rendered_page") != page_id:
        st.session_state.json_converted = False

    if not st.session_state.json_converted:
        st.checkbox("Normalize JSON (use json_normalize)", key="normalize")

        st.text_area(
            "Paste JSON records here",
            height=500,
            key="json_input",
        )

        st.button("Convert JSON", on_click=do_convert, type="primary")

        if st.session_state.json_convert_error:
            st.error(f"Failed to parse JSON: {st.session_state.json_convert_error}")

    else:
        df = st.session_state.json_df
        if df is not None:
            st.dataframe(df)
            csv_bytes = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Download CSV",
                csv_bytes,
                file_name="converted.csv",
                mime="text/csv",
                type="secondary",
            )

        st.button("Back", on_click=go_back, type="primary")

    # mark this page as the last rendered so other pages can detect navigation
    st.session_state.last_rendered_page = page_id


if __name__ == "__main__":
    render()
