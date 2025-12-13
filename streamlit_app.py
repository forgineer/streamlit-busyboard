import streamlit as st

from pages import json_to_df, placeholder


st.set_page_config(page_title="Busy Board", layout="wide")

# Sidebar navigation
st.sidebar.title("📋 Busy Board")
pages = {
    "JSON → DataFrame": json_to_df,
    "Placeholder Page": placeholder,
}
page = st.sidebar.radio("Pages", list(pages.keys()))

# Render selected page
pages[page].render()
