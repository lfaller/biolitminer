"""
Simple PubMed client for searching biomedical literature.
"""
import requests
import xml.etree.ElementTree as ET
from typing import List
import time


class PubMedClient:
    """Simple client for searching PubMed with rate limiting."""
    
    def __init__(self, email: str = "user@example.com"):
        """Initialize the PubMed client."""
        self.email = email
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.last_request_time = 0
        self.min_delay = 0.5  # Minimum 0.5 seconds between requests
        
    def _rate_limit(self):
        """Apply rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_delay:
            sleep_time = self.min_delay - time_since_last
            print(f"Rate limiting: waiting {sleep_time:.2f} seconds...")
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
        # Apply rate limiting
        self._rate_limit()
        
        # Build the search URL
        search_url = f"{self.base_url}/esearch.fcgi"
        
        # Parameters for the search
        params = {
            'db': 'pubmed',
            'term': query,
            'retmax': max_results,
            'retmode': 'xml',
            'email': self.email
        }
        
        try:
            # Make the request
            print(f"Searching PubMed for: {query}")
            response = requests.get(search_url, params=params)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            # Parse the XML response
            root = ET.fromstring(response.text)
            
            # Extract PMIDs
            pmids = []
            for id_elem in root.findall('.//Id'):
                pmids.append(id_elem.text)
            
            print(f"Found {len(pmids)} articles")
            return pmids
            
        except requests.RequestException as e:
            if "429" in str(e):
                print("Rate limit exceeded. Waiting 10 seconds...")
                time.sleep(10)
                return self.search_pubmed(query, max_results)  # Retry once
            else:
                print(f"Error searching PubMed: {e}")
                return []
        except ET.ParseError as e:
            print(f"Error parsing XML response: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error: {e}")
            return []