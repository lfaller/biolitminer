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
