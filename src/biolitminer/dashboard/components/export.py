"""
Simple export functionality for BioLitMiner dashboard.
"""

import json
from datetime import datetime
from typing import Any, Dict, List

import streamlit as st


def show_export_options(articles: List[Dict[str, Any]], query: str):
    """Show basic export options for search results."""
    st.subheader("💾 Export Results")

    col1, col2 = st.columns(2)

    with col1:
        # JSON export only
        json_data = create_json_export(articles, query)
        st.download_button(
            label="📄 Download JSON",
            data=json_data,
            file_name=generate_filename("json"),
            mime="application/json",
            help="Export search results as JSON file",
        )

    with col2:
        # Show basic stats
        st.info(
            f"📊 Found {len(articles)} articles from {len(set(a.get('journal', 'Unknown') for a in articles))} journals"
        )


def create_json_export(articles: List[Dict[str, Any]], query: str) -> str:
    """Create simple JSON export."""
    export_data = {
        "search_query": query,
        "export_date": datetime.now().isoformat(),
        "total_articles": len(articles),
        "articles": articles,
    }
    return json.dumps(export_data, indent=2, default=str)


def generate_filename(file_type: str) -> str:
    """Generate timestamped filename."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"biolitminer_results_{timestamp}.{file_type}"
