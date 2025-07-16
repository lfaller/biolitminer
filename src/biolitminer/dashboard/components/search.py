"""
Search interface component for BioLitMiner dashboard.
"""

import streamlit as st


def render_search_interface():
    """Render the main search interface."""
    st.header("🔍 Search PubMed")

    # Search form
    with st.form("search_form"):
        query = st.text_input(
            "Enter your search query:",
            placeholder="e.g., COVID-19, BRCA1 breast cancer, machine learning genomics",
            help="Use PubMed search syntax for best results",
        )

        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            search_button = st.form_submit_button("🔍 Search", type="primary")
        with col2:
            clear_button = st.form_submit_button("🗑️ Clear")

    return query, search_button, clear_button


def render_example_queries():
    """Render example query buttons."""
    st.header("💡 Example Queries")
    col1, col2, col3 = st.columns(3)

    examples = {
        "🦠 COVID-19 research": "COVID-19",
        "🧬 BRCA1 breast cancer": "BRCA1 breast cancer",
        "🤖 AI in medicine": "artificial intelligence medicine",
    }

    selected_example = None

    for i, (button_text, query) in enumerate(examples.items()):
        col = [col1, col2, col3][i]
        with col:
            if st.button(button_text):
                selected_example = query

    return selected_example
