"""
Simple PubMed client for searching biomedical literature.
"""

import requests
import xml.etree.ElementTree as ET
from typing import List
import time

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
            Dictionary with article details
        """
        try:
            # Get the basic citation info
            citation = article_elem.find(".//MedlineCitation")
            if citation is None:
                logger.warning("No MedlineCitation found in article")
                return None

            # Extract PMID
            pmid_elem = citation.find(".//PMID")
            pmid = pmid_elem.text if pmid_elem is not None else ""

            # Extract article info
            article = citation.find(".//Article")
            if article is None:
                logger.warning(f"No Article element found for PMID {pmid}")
                return None

            # Extract title
            title_elem = article.find(".//ArticleTitle")
            title = title_elem.text if title_elem is not None else ""

            # Extract abstract
            abstract_elem = article.find(".//AbstractText")
            abstract = abstract_elem.text if abstract_elem is not None else ""

            # Extract authors
            authors = []
            author_list = article.find(".//AuthorList")
            if author_list is not None:
                for author_elem in author_list.findall(".//Author"):
                    last_name_elem = author_elem.find(".//LastName")
                    first_name_elem = author_elem.find(".//ForeName")

                    if last_name_elem is not None and first_name_elem is not None:
                        authors.append(
                            {
                                "last_name": last_name_elem.text,
                                "first_name": first_name_elem.text,
                            }
                        )

            # Extract journal
            journal_elem = article.find(".//Journal/Title")
            journal = journal_elem.text if journal_elem is not None else ""

            logger.debug(f"Parsed article {pmid}: {title[:50]}...")

            return {
                "pmid": pmid,
                "title": title,
                "abstract": abstract,
                "authors": authors,
                "journal": journal,
            }

        except Exception as e:
            logger.error(f"Error parsing article XML: {e}")
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
