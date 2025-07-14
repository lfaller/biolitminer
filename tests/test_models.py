"""
Pytest tests for our data models.
"""

from src.biolitminer.core.models import Article, Author


def test_author_creation():
    """Test creating an Author."""
    author = Author("Smith", "Jane", "J.")

    assert author.last_name == "Smith"
    assert author.first_name == "Jane"
    assert author.initials == "J."
    assert str(author) == "Jane Smith"


def test_author_without_initials():
    """Test creating an Author without initials."""
    author = Author("Doe", "Jane")

    assert author.last_name == "Doe"
    assert author.first_name == "Jane"
    assert author.initials == ""


def test_article_creation():
    """Test creating an Article."""
    article = Article("12345", "Test Article About COVID-19")

    assert article.pmid == "12345"
    assert article.title == "Test Article About COVID-19"
    assert article.abstract == ""
    assert len(article.authors) == 0
    assert article.publication_date is None
    assert article.journal == ""


def test_article_add_author():
    """Test adding an author to an article."""
    article = Article("12345", "Test Article")
    author = Author("Smith", "Jane", "J.")

    article.add_author(author)

    assert len(article.authors) == 1
    assert article.authors[0] == author


def test_article_multiple_authors():
    """Test adding multiple authors to an article."""
    article = Article("12345", "Test Article")

    author1 = Author("Smith", "Jane", "J.")
    author2 = Author("Doe", "Jane", "J.")

    article.add_author(author1)
    article.add_author(author2)

    assert len(article.authors) == 2
    assert article.authors[0] == author1
    assert article.authors[1] == author2


def test_article_string_representation():
    """Test the string representation of an article."""
    article = Article("12345", "This is a very long title that should be truncated")

    result = str(article)
    assert "pmid=12345" in result
    assert "This is a very long title that should be truncat" in result
