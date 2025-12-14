import streamlit as st


st.set_page_config(page_title="Busy Board", layout="wide")


def home():
    st.title("📋 Busy Board")
    st.write("Choose a tool from the top navigation.")


# Register pages using Streamlit's Page navigation API
pages = [
    st.Page(home, title="Home"),
    st.Page("apps/csv_to_json.py", title="CSV → JSON"),
    st.Page("apps/json_to_df.py", title="JSON → DataFrame"),
]

nav = st.navigation(pages)
nav.run()
