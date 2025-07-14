#!/usr/bin/env python3
"""
Test fetching full article details from PubMed.
"""
from src.biolitminer.data.pubmed_client import PubMedClient

def test_article_fetching():
    """Test fetching full article details."""
    client = PubMedClient(email="your.email@example.com")  # Replace with your email
    
    # Test search and fetch in one step
    print("Testing search and fetch combined...")
    articles = client.search_and_fetch("BRCA1", max_results=2)
    
    print(f"\nFound {len(articles)} articles:")
    print("="*80)
    
    for i, article in enumerate(articles, 1):
        print(f"\nArticle {i}:")
        print(f"PMID: {article['pmid']}")
        print(f"Title: {article['title']}")
        print(f"Journal: {article['journal']}")
        print(f"Authors: {len(article['authors'])} authors")
        
        # Print first few authors
        if article['authors']:
            print("First authors:")
            for author in article['authors'][:3]:
                print(f"  - {author['first_name']} {author['last_name']}")
        
        # Print abstract (first 200 chars)
        if article['abstract']:
            print(f"Abstract: {article['abstract'][:200]}...")
        
        print("-" * 80)

if __name__ == "__main__":
    test_article_fetching()