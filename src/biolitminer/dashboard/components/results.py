"""
Results display component for BioLitMiner dashboard.
"""

import pandas as pd
import streamlit as st


def display_summary_stats(articles: list, total_pmids: int):
    """Display summary statistics about the search results."""
    st.subheader("📊 Summary Statistics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📄 Articles Found", len(articles))

    with col2:
        st.metric("✅ Successfully Parsed", f"{len(articles)}/{total_pmids}")

    with col3:
        journals = set(article.get("journal", "Unknown") for article in articles)
        st.metric("📚 Unique Journals", len(journals))

    with col4:
        total_authors = sum(len(article.get("authors", [])) for article in articles)
        st.metric("👥 Total Authors", total_authors)


def display_results(articles: list, show_abstracts: bool):
    """Display search results in a nice format."""
    st.subheader("📄 Articles")

    for i, article in enumerate(articles, 1):
        with st.expander(
            f"**{i}. {article.get('title', 'No title')}**", expanded=False
        ):
            # Article metadata
            col1, col2 = st.columns([2, 1])

            with col1:
                st.write(f"**PMID:** {article.get('pmid', 'Unknown')}")
                st.write(f"**Journal:** {article.get('journal', 'Unknown')}")

                # Authors
                authors = article.get("authors", [])
                if authors:
                    author_names = []
                    for author in authors[:5]:
                        first_name = author.get("first_name", "") or author.get(
                            "initials", ""
                        )
                        last_name = author.get("last_name", "")
                        if first_name and last_name:
                            author_names.append(f"{first_name} {last_name}")
                        elif last_name:
                            author_names.append(last_name)

                    if len(authors) > 5:
                        author_names.append("et al.")

                    st.write(f"**Authors:** {', '.join(author_names)}")

            with col2:
                pub_date = article.get("publication_date")
                if pub_date:
                    st.write(f"**Year:** {pub_date}")

            # Abstract
            if show_abstracts:
                abstract = article.get("abstract", "")
                if abstract:
                    st.write("**Abstract:**")
                    st.write(abstract)
                else:
                    st.write("*No abstract available*")


def show_summary_report(articles: list, query: str):
    """Generate and display a summary report."""
    from datetime import datetime

    st.subheader("📋 Summary Report")

    st.write(f"**Search Query:** {query}")
    st.write(f"**Search Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.write(f"**Total Articles:** {len(articles)}")

    if articles:
        journals = [article.get("journal", "Unknown") for article in articles]
        journal_counts = pd.Series(journals).value_counts()

        st.write("**Top Journals:**")
        for journal, count in journal_counts.head(5).items():
            st.write(f"- {journal}: {count} articles")
