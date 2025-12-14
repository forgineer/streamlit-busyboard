import re
import streamlit as st
from html import escape


def convert_list(text: str, remove_dupes: bool, quote: str, wrapper: str) -> str:
    if not text:
        return ""

    # Split on newlines, tabs, or commas
    tokens = re.split(r'[,\t\r\n]+', text)
    items = [t.strip() for t in tokens if t.strip()]

    # Remove duplicates while preserving order
    if remove_dupes:
        seen = set()
        uniq = []
        for it in items:
            if it not in seen:
                seen.add(it)
                uniq.append(it)
        items = uniq

    # Apply quoting
    if quote == "single":
        # For SQL-friendly single quotes, double any single quote inside values
        items = ["'" + it.replace("'", "''") + "'" for it in items]
    elif quote == "double":
        items = ['"' + it.replace('"', '\\"') + '"' for it in items]

    result = ', '.join(items)

    # Apply wrapper
    if wrapper == "paren":
        result = f"({result})"
    elif wrapper == "bracket":
        result = f"[{result}]"
    elif wrapper == "brace":
        result = f"{{{result}}}"

    return result


def main():
    st.title("🔢 List → IN-style List")

    st.write("Paste values from a spreadsheet or editor and convert them into a comma-separated IN list.")

    with st.expander("Options", expanded=True):
        remove_dupes = st.checkbox("Remove duplicates", value=True)

        quote = st.radio("Surround each value with:",
                         options=["None", "Single quote (')", 'Double quote (")'],
                         index=0)
        quote_key = "none"
        if quote.startswith("Single"):
            quote_key = "single"
        elif quote.startswith('Double'):
            quote_key = "double"

        wrapper = st.radio("Encase the entire list with:",
                           options=["None", "Parentheses ()", "Brackets []", "Braces {}"],
                           index=0)
        wrapper_key = "none"
        if wrapper.startswith("Parentheses"):
            wrapper_key = "paren"
        elif wrapper.startswith("Brackets"):
            wrapper_key = "bracket"
        elif wrapper.startswith("Braces"):
            wrapper_key = "brace"

    input_text = st.text_area("Input values", placeholder="Paste values here (one per line or tab/comma separated)", height=200)

    if st.button("Convert List"):
        output = convert_list(input_text, remove_dupes, quote_key, wrapper_key)
        st.session_state["list_converter_output"] = output

    output = st.session_state.get("list_converter_output", "")

    # Show converted output without a persistent widget key so it updates correctly
    st.text_area("Converted list", value=output, height=150)

    # Copy button via JS
    escaped = escape(output)
    copy_html = f"""
    <div>
      <textarea id="copyArea" style="width:100%;height:120px;display:none">{escaped}</textarea>
      <button onclick="(function(){{
        const t = document.getElementById('copyArea');
        if(!t) return;
        navigator.clipboard.writeText(t.value).then(function(){{
          const e = document.getElementById('copyMsg'); if(e) e.innerText='Copied to clipboard';
        }});
      }})()">Copy List</button>
      <span id="copyMsg" style="margin-left:12px;color:green"></span>
    </div>
    """

    st.markdown(copy_html, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
