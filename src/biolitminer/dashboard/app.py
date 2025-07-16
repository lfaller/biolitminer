"""
BioLitMiner Streamlit Dashboard - Main Application
"""

import sys
from pathlib import Path

import streamlit as st

# Add the src directory to Python path
src_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(src_path))

from biolitminer.core.logging_config import setup_logging
from biolitminer.dashboard.components.export import show_export_options
from biolitminer.dashboard.components.results import (
    display_results,
    display_summary_stats,
)
from biolitminer.dashboard.components.search import (
    render_example_queries,
    render_search_interface,
)
from biolitminer.dashboard.components.sidebar import render_sidebar
from biolitminer.data.pubmed_client import PubMedClient

# Configure Streamlit
st.set_page_config(
    page_title="BioLitMiner",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Setup quiet logging for dashboard
setup_logging(level="WARNING", log_to_console=False)


def main():
    """Main dashboard application."""
    # Header
    st.title("🧬 BioLitMiner")
    st.subheader("Biomedical Literature Mining and Analysis")

    # Render sidebar and get config
    config = render_sidebar()

    # Render search interface
    query, search_button, clear_button = render_search_interface()

    # Handle clear button
    if clear_button:
        st.session_state.clear()
        st.rerun()

    # Handle search
    if search_button and query.strip():
        perform_search(query, config)

    # Handle example queries
    example_query = render_example_queries()
    if example_query:
        perform_search(example_query, config)


def perform_search(query: str, config: dict):
    """Perform the PubMed search with given configuration."""
    st.header(f"📄 Results for: *{query}*")

    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        # Update logging if verbose
        if config["verbose_logging"]:
            setup_logging(level="DEBUG", log_to_console=True)

        # Initialize and search
        status_text.text("🔧 Initializing PubMed client...")
        client = PubMedClient(email=config["email"])
        progress_bar.progress(20)

        status_text.text("🔍 Searching PubMed...")
        pmids = client.search_pubmed(query, config["max_results"])
        progress_bar.progress(50)

        if not pmids:
            st.warning("No articles found. Try different keywords.")
            return

        status_text.text(f"📥 Fetching details for {len(pmids)} articles...")
        articles = client.fetch_article_details(pmids)
        progress_bar.progress(90)

        progress_bar.progress(100)
        status_text.text("✅ Search completed!")

        if not articles:
            st.error("Found articles but couldn't parse details.")
            return

        # Display results
        display_summary_stats(articles, len(pmids))
        display_results(articles, config["show_abstracts"])

        # Store results and show export options
        st.session_state.last_results = articles
        st.session_state.last_query = query
        show_export_options(articles, query)

    except Exception as e:
        st.error(f"Error during search: {str(e)}")
        if config.get("verbose_logging"):
            st.exception(e)
    finally:
        progress_bar.empty()
        status_text.empty()


if __name__ == "__main__":
    main()
