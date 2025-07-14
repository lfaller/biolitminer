"""
Simple data models for BioLitMiner.
"""
from datetime import datetime
from typing import List, Optional


class Author:
    """Simple author model."""
    
    def __init__(self, last_name: str, first_name: str, initials: str = ""):
        self.last_name = last_name
        self.first_name = first_name
        self.initials = initials
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Article:
    """Simple article model."""
    
    def __init__(self, pmid: str, title: str, abstract: str = ""):
        self.pmid = pmid
        self.title = title
        self.abstract = abstract
        self.authors: List[Author] = []
        self.publication_date: Optional[datetime] = None
        self.journal: str = ""
    
    def add_author(self, author: Author):
        """Add an author to the article."""
        self.authors.append(author)
    
    def __str__(self):
        return f"Article(pmid={self.pmid}, title='{self.title[:50]}...')"