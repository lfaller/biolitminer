"""
Sidebar component for BioLitMiner dashboard.
"""

import streamlit as st

from biolitminer.core.version import get_version


def render_sidebar():
    """Render the sidebar with configuration options."""
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Version info
        version = get_version()
        st.info(f"Version: {version}")

        # Email input
        email = st.text_input(
            "📧 Email for PubMed API",
            value="user@example.com",
            help="Required by NCBI for API access",
        )

        # Max results
        max_results = st.slider(
            "📊 Max Results",
            min_value=1,
            max_value=100,
            value=10,
            help="Maximum number of articles to retrieve",
        )

        # Advanced options
        with st.expander("🔧 Advanced Options"):
            verbose_logging = st.checkbox("Enable verbose logging")
            show_abstracts = st.checkbox("Show abstracts in results", value=True)

        return {
            "email": email,
            "max_results": max_results,
            "verbose_logging": verbose_logging,
            "show_abstracts": show_abstracts,
        }
