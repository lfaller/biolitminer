# BioLitMiner

A biomedical literature mining tool that extracts knowledge from PubMed articles, performs named entity recognition, constructs knowledge graphs, and provides interactive visualizations.

## Features

- **Literature Mining**: Query PubMed for biomedical articles
- **Entity Extraction**: Extract genes, proteins, diseases, drugs, and other biomedical entities
- **Knowledge Graph**: Build relationships between entities from literature
- **Interactive Dashboard**: Streamlit-based visualization and exploration
- **Database Integration**: Link entities to external databases (UniProt, OMIM, ChEMBL)

## Installation

```bash
git clone <this repo>
poetry install
```

## Streamlit Dashboard

Launch the interactive web dashboard:

```bash
poetry run streamlit run src/biolitminer/dashboard/app.py
```

The dashboard provides:

* Interactive search interface
* Real-time progress indicators
* Rich article display with expandable details
* Summary statistics and metrics
* JSON export functionality
* Responsive design with modular architecture

Access at: http://localhost:8501

## Run Tests

```bash
poetry run pytest
```

## CLI Usage

### Search PubMed
```bash
# Basic search
biolitminer search "COVID-19" --max 10 --email "your.email@example.com"

# Search with verbose output
biolitminer search "BRCA1 breast cancer" --verbose --email "your.email@example.com"

# Search and save to JSON file
biolitminer search "machine learning genomics" --output "results.json" --email "your.email@example.com"
```

## Versioning

The version is maintained in `pyproject.toml`. Any other files (right now, `cli.py`) pull from there.

```bash
# For bug fixes (0.2.0 → 0.2.1)
poetry version patch

# For new features (0.2.1 → 0.3.0)
poetry version minor

# For breaking changes (0.3.0 → 1.0.0)
poetry version major

# Check the version was updated
poetry run biolitminer version

# See current version without running the CLI
poetry version
```
