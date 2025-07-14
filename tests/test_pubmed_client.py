"""
Pytest tests for PubMed client.
"""
from src.biolitminer.data.pubmed_client import PubMedClient


##TODO: add mock responses for the tests 

def test_pubmed_client_creation():
    """Test creating a PubMed client."""
    client = PubMedClient(email="test@example.com")
    assert client.email == "test@example.com"
    assert "eutils.ncbi.nlm.nih.gov" in client.base_url


def test_pubmed_search_covid():
    """Test searching for COVID-19 articles."""
    client = PubMedClient(email="test@example.com")
    pmids = client.search_pubmed("COVID-19", max_results=3)
    
    assert isinstance(pmids, list)
    assert len(pmids) <= 3
    assert len(pmids) > 0  # Should find some COVID articles
    
    # Check that PMIDs are strings and numeric
    for pmid in pmids:
        assert isinstance(pmid, str)
        assert pmid.isdigit()


def test_pubmed_search_empty_query():
    """Test searching with empty query."""
    client = PubMedClient(email="test@example.com")
    pmids = client.search_pubmed("", max_results=3)
    
    # Should return empty list for empty query
    assert isinstance(pmids, list)


def test_pubmed_search_max_results():
    """Test that max_results parameter works."""
    client = PubMedClient(email="test@example.com")
    pmids = client.search_pubmed("cancer", max_results=2)
    
    assert isinstance(pmids, list)
    assert len(pmids) <= 2