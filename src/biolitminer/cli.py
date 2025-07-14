"""
Command-line interface for BioLitMiner.
"""

from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .core.logging_config import setup_logging
from .data.pubmed_client import PubMedClient

app = typer.Typer(help="BioLitMiner - Biomedical Literature Mining Tool")
console = Console()


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query for PubMed"),
    max_results: int = typer.Option(
        10, "--max", "-m", help="Maximum number of results"
    ),
    email: str = typer.Option(
        "user@example.com", "--email", "-e", help="Your email for PubMed API"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="Save results to file (JSON)"
    ),
):
    """Search PubMed for biomedical articles."""

    # Set up logging
    log_level = "DEBUG" if verbose else "INFO"
    setup_logging(level=log_level, log_to_console=verbose)

    console.print(f"[bold blue]Searching PubMed for:[/bold blue] {query}")
    console.print(f"[dim]Max results: {max_results}, Email: {email}[/dim]\n")

    # Create PubMed client
    client = PubMedClient(email=email)

    # Search with progress indicator
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Searching PubMed...", total=None)
        articles = client.search_and_fetch(query, max_results)
        progress.update(task, description="Search completed!")

    if not articles:
        console.print("[red]No articles found![/red]")
        return

    # Display results in a nice table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("PMID", style="cyan", width=10)
    table.add_column("Title", style="white", width=50)
    table.add_column("Journal", style="green", width=20)
    table.add_column("Authors", style="yellow", width=15)

    for article in articles:
        # Truncate title if too long
        title = (
            article["title"][:47] + "..."
            if len(article["title"]) > 50
            else article["title"]
        )

        # Get first few authors
        author_names = []
        for author in article["authors"][:2]:  # First 2 authors
            author_names.append(f"{author['first_name']} {author['last_name']}")

        if len(article["authors"]) > 2:
            author_names.append("et al.")

        authors_str = ", ".join(author_names)

        table.add_row(
            article["pmid"],
            title,
            (
                article["journal"][:17] + "..."
                if len(article["journal"]) > 20
                else article["journal"]
            ),
            authors_str,
        )

    console.print(table)
    console.print(f"\n[bold green]Found {len(articles)} articles[/bold green]")

    # Save to file if requested
    if output:
        import json

        with open(output, "w") as f:
            json.dump(articles, f, indent=2, default=str)
        console.print(f"[green]Results saved to {output}[/green]")


@app.command()
def version():
    """Show BioLitMiner version."""
    console.print("[bold blue]BioLitMiner[/bold blue] version [green]0.2.0[/green]")


if __name__ == "__main__":
    app()
