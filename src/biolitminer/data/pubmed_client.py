"""
Simple PubMed client for searching biomedical literature.
"""

import time
import xml.etree.ElementTree as ET
from typing import List

import requests

from ..core.logging_config import get_logger

logger = get_logger(__name__)


class PubMedClient:
    """Simple client for searching PubMed with rate limiting."""

    def __init__(self, email: str = "user@example.com"):
        """Initialize the PubMed client."""
        self.email = email
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.last_request_time = 0
        self.min_delay = 0.5  # Minimum 0.5 seconds between requests
        logger.info(f"Initialized PubMed client for {email}")

    def _rate_limit(self):
        """Apply rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.min_delay:
            sleep_time = self.min_delay - time_since_last
            logger.debug(f"Rate limiting: waiting {sleep_time:.2f} seconds")
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def search_pubmed(self, query: str, max_results: int = 10) -> List[str]:
        """
        Search PubMed and return a list of PMIDs.

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            List of PMIDs as strings
        """
        logger.info(f"Searching PubMed for: '{query}' (max_results={max_results})")

        # Apply rate limiting
        self._rate_limit()

        # Build the search URL
        search_url = f"{self.base_url}/esearch.fcgi"

        # Parameters for the search
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "xml",
            "email": self.email,
        }

        try:
            # Make the request
            logger.debug(f"Making request to: {search_url}")
            response = requests.get(search_url, params=params)
            response.raise_for_status()

            # Parse the XML response
            root = ET.fromstring(response.text)

            # Extract PMIDs
            pmids = []
            for id_elem in root.findall(".//Id"):
                pmids.append(id_elem.text)

            logger.info(f"Found {len(pmids)} articles")
            logger.debug(f"PMIDs: {pmids}")
            return pmids

        except requests.RequestException as e:
            if "429" in str(e):
                logger.warning("Rate limit exceeded. Waiting 10 seconds...")
                time.sleep(10)
                return self.search_pubmed(query, max_results)  # Retry once
            else:
                logger.error(f"Error searching PubMed: {e}")
                return []
        except ET.ParseError as e:
            logger.error(f"Error parsing XML response: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return []

    def fetch_article_details(self, pmids: List[str]) -> List:
        """
        Fetch detailed article information for given PMIDs.

        Args:
            pmids: List of PubMed IDs

        Returns:
            List of dictionaries containing article details
        """
        if not pmids:
            logger.warning("No PMIDs provided for fetching details")
            return []

        logger.info(f"Fetching details for {len(pmids)} articles")
        logger.debug(f"PMIDs to fetch: {pmids}")

        # Apply rate limiting
        self._rate_limit()

        # Build the fetch URL
        fetch_url = f"{self.base_url}/efetch.fcgi"

        # Parameters for fetching details
        params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml",
            "rettype": "abstract",
            "email": self.email,
        }

        try:
            logger.debug(f"Making request to: {fetch_url}")
            response = requests.get(fetch_url, params=params)
            response.raise_for_status()

            # Parse the XML response
            root = ET.fromstring(response.text)

            articles = []
            for article_elem in root.findall(".//PubmedArticle"):
                article_data = self._parse_article_xml(article_elem)
                if article_data:
                    articles.append(article_data)

            logger.info(f"Successfully parsed {len(articles)} articles")
            return articles

        except requests.RequestException as e:
            if "429" in str(e):
                logger.warning("Rate limit exceeded. Waiting 10 seconds...")
                time.sleep(10)
                return self.fetch_article_details(pmids)  # Retry once
            else:
                logger.error(f"Error fetching article details: {e}")
                return []
        except ET.ParseError as e:
            logger.error(f"Error parsing XML response: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return []

    def _parse_article_xml(self, article_elem) -> dict:
        """
        Parse a single article XML element into a dictionary.

        Args:
            article_elem: XML element containing article data

        Returns:
            Dictionary with article details or None if parsing fails
        """
        try:
            # Get the basic citation info
            citation = article_elem.find(".//MedlineCitation")
            if citation is None:
                logger.warning("No MedlineCitation found in article")
                return None

            # Extract PMID
            pmid_elem = citation.find(".//PMID")
            pmid = pmid_elem.text if pmid_elem is not None else "Unknown"

            logger.debug(f"Parsing article with PMID: {pmid}")

            # Extract article info
            article = citation.find(".//Article")
            if article is None:
                logger.warning(f"No Article element found for PMID {pmid}")
                return None

            # Extract title - handle multiple possible locations
            title = ""
            title_elem = article.find(".//ArticleTitle")
            if title_elem is not None and title_elem.text:
                title = title_elem.text.strip()
            else:
                logger.warning(f"No title found for PMID {pmid}")
                title = "No title available"

            # Extract abstract - handle multiple AbstractText elements
            abstract = ""
            abstract_section = article.find(".//Abstract")
            if abstract_section is not None:
                abstract_texts = abstract_section.findall(".//AbstractText")
                if abstract_texts:
                    # Join multiple abstract sections
                    abstract_parts = []
                    for abs_text in abstract_texts:
                        if abs_text.text:
                            # Handle structured abstracts with labels
                            label = abs_text.get("Label", "")
                            text = abs_text.text.strip()
                            if label:
                                abstract_parts.append(f"{label}: {text}")
                            else:
                                abstract_parts.append(text)
                    abstract = " ".join(abstract_parts)
                else:
                    logger.debug(f"No AbstractText found for PMID {pmid}")

            # Extract authors with better error handling
            authors = []
            author_list = article.find(".//AuthorList")
            if author_list is not None:
                for author_elem in author_list.findall(".//Author"):
                    try:
                        last_name_elem = author_elem.find(".//LastName")
                        first_name_elem = author_elem.find(".//ForeName")
                        initials_elem = author_elem.find(".//Initials")

                        # Handle different author formats
                        last_name = (
                            last_name_elem.text.strip()
                            if last_name_elem is not None and last_name_elem.text
                            else ""
                        )
                        first_name = (
                            first_name_elem.text.strip()
                            if first_name_elem is not None and first_name_elem.text
                            else ""
                        )
                        initials = (
                            initials_elem.text.strip()
                            if initials_elem is not None and initials_elem.text
                            else ""
                        )

                        # Only add author if we have at least a last name
                        if last_name:
                            authors.append(
                                {
                                    "last_name": last_name,
                                    "first_name": first_name,
                                    "initials": initials,
                                }
                            )
                        else:
                            # Handle collective names or other author formats
                            collective_name = author_elem.find(".//CollectiveName")
                            if collective_name is not None and collective_name.text:
                                authors.append(
                                    {
                                        "last_name": collective_name.text.strip(),
                                        "first_name": "",
                                        "initials": "",
                                    }
                                )

                    except Exception as e:
                        logger.warning(
                            f"Error parsing individual author for PMID {pmid}: {e}"
                        )
                        continue

            # Extract journal with fallback options
            journal = ""
            # Try multiple journal title locations
            journal_elem = article.find(".//Journal/Title")
            if journal_elem is None:
                journal_elem = article.find(".//Journal/ISOAbbreviation")
            if journal_elem is None:
                journal_elem = article.find(".//MedlineTA")

            if journal_elem is not None and journal_elem.text:
                journal = journal_elem.text.strip()
            else:
                logger.debug(f"No journal found for PMID {pmid}")
                journal = "Unknown journal"

            # Extract publication date with error handling
            pub_date = None
            try:
                journal_issue = article.find(".//Journal/JournalIssue")
                if journal_issue is not None:
                    pub_date_elem = journal_issue.find(".//PubDate")
                    if pub_date_elem is not None:
                        year_elem = pub_date_elem.find(".//Year")
                        if year_elem is not None and year_elem.text:
                            pub_date = year_elem.text.strip()
            except Exception as e:
                logger.debug(f"Error parsing publication date for PMID {pmid}: {e}")

            logger.debug(f"Successfully parsed article {pmid}: {title[:50]}...")

            return {
                "pmid": pmid,
                "title": title,
                "abstract": abstract,
                "authors": authors,
                "journal": journal,
                "publication_date": pub_date,
            }

        except Exception as e:
            logger.error(f"Error parsing article XML: {e}")
            # Try to extract at least the PMID for debugging
            try:
                pmid_elem = article_elem.find(".//PMID")
                pmid = pmid_elem.text if pmid_elem is not None else "Unknown"
                logger.error(f"Failed to parse article with PMID: {pmid}")
            except (AttributeError, TypeError) as debug_error:
                logger.error(
                    f"Could not even extract PMID from failed article: {debug_error}"
                )
            return None

    def search_and_fetch(self, query: str, max_results: int = 10) -> List:
        """
        Search PubMed and fetch full article details in one step.

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            List of dictionaries containing full article details
        """
        logger.info(f"Starting search and fetch for: '{query}'")

        # First search for PMIDs
        pmids = self.search_pubmed(query, max_results)

        if not pmids:
            logger.warning("No PMIDs found, returning empty list")
            return []

        # Then fetch full details
        articles = self.fetch_article_details(pmids)

        logger.info(f"Search and fetch completed. Retrieved {len(articles)} articles")
        return articles
