# SDRF Cell Line Metadata Database

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14524549.svg)](https://doi.org/10.5281/zenodo.14524549) 

This repository provides tools to create and manage a **cell line metadata database** for annotating SDRFs (Sample and Data Relationship Format) in proteomics studies. The primary use case is enhancing annotation consistency for [quantms.org](https://quantms.org) datasets. The scripts integrate multiple ontologies and **natural language processing (NLP)** methods to standardize cell line metadata.

You can query the database for cell line metadata, including information on the organism, tissue, disease, and other relevant fields [in GitHub](https://github.com/bigbio/sdrf-cellline-metadata-db/blob/main/cl-annotations-db.tsv). The database is designed to be easily extensible and can be updated with new cell line information.

> **NOTE**:
>This is **NOT an Ontology of cell lines**; but a registry/table where users can find the required information about a cell line in a standardized format for SDRF annotation.



---

## Table of Contents

1. [Motivation](#motivation)  
2. [Metadata Sources](#metadata-sources)  
3. [Ontologies](#ontologies)  
4. [Database Structure](#database-structure)  
5. [Features](#features)  
6. [Requirements](#requirements)  
7. [Installation](#installation)  
8. [Usage](#usage)  
9. [Contribution](#contribution)  
10. [License](#license)

---

## Motivation

Cell lines are essential in biological research but often lack standardized metadata, leading to inconsistencies. This repository aims to:

- **Create a centralized database** for cell line metadata.
- **Facilitate annotation and validation** of cell line SDRFs, particularly in proteomics datasets.

---

## Cell line metadata sources

We integrate metadata from **three main sources** and additional curation efforts:

1. **[Cellosaurus](https://web.expasy.org/cellosaurus/):**  
   The primary metadata source.  
   - Download: [cellosaurus.txt](https://ftp.expasy.org/databases/cellosaurus/cellosaurus.txt)  
   - Script: [`cellosaurus_db.py`](cellosaurus/cellosaurus_db.py) extracts relevant fields and transform some of the cellosaurus fields to SDRF compatible format. 

2. **[Cell Model Passports](https://cog.sanger.ac.uk/cmp):**  
   A collection of cell lines from various sources.  
   - Input file: [model_list_20240110.csv](cellpassports/model_list_20240110.csv)  
   - Script: [`cellpassports_db.py`](cellpassports/cellpassports_db.py) processes this data.  

3. **[Expression Atlas (EA)](https://www.ebi.ac.uk/gxa):**  
   Metadata curated over RNA experiments for over 10 years.  
   - Collected data: Stored in the `ea/` folder.  
   - Script: [`ea_db.py`](ea/ea_db.py) processes this source.  

> **Additional Curation**: Manual annotation is performed using data from:  
> - [Coriell Cell Line Catalog](https://www.coriell.org/)  
> - [Cell Bank RIKEN](https://cell.brc.riken.jp/en/)  
> - [ATCC](https://www.atcc.org/)

---

### Ontologies

The following ontologies are used for annotation:

1. **[MONDO](https://bioportal.bioontology.org/ontologies/MONDO):**  
   Used to annotate the disease associated with a cell line.

2. **[BTO](https://bioportal.bioontology.org/ontologies/BTO):**  
   Provides additional references for cell line IDs.

---

## Database Structure

The database is implemented using **tsv** and contains the following key fields:

| Field Name                | Description                                                    |
|---------------------------|----------------------------------------------------------------|
| **cell line**             | Cell line code                                                 |
| **cellosaurus name**      | Name as annotated in Cellosaurus `ID`.                         |
| **cellosaurus accession** | Accession ID from Cellosaurus `AC`.                            |
| **bto cell line**         | Name as annotated in BTO.                                      |
| **organism**              | Organism species (from Cellosaurus).                           |
| **organism part**         | Annotated from supplementary sources.                          |
| **sampling site**         | Sampling site of the cell line.                                |
| **age**                   | Age of the cell line (from Cellosaurus or additional sources). |
| **developmental stage**   | Developmental stage (inferred from age if missing).            |
| **sex**                   | Sex information (from Cellosaurus).                            |
| **ancestry category**     | Ancestry classification (from Cellosaurus or supplementary sources). |
| **disease**               | Agreed-upon disease annotation across sources.                 |
| **cell type**             | Agreed-upon cell type annotation across sources.               |
| **material type**         | Agreed-upon material classification.                           |
| **synonyms**              | Consolidated synonyms and accessions from all sources.         |
| **curated**               | Curation status: `_not curated_`, `_AI curated_`, or `_manual curated_`. |

> **Note**: The final database is provided as a **tab-delimited file** for easy integration. It can be loaded into tools like **Pandas** or viewed directly via GitHub's table renderer.

---

## Features

- Standardizes metadata from **multiple sources**.
- Uses **ontologies** to annotate diseases and tissue information.
- Supports **AI-based curation** and manual validation for accuracy.
- Provides **easy-to-query** tab-delimited outputs.

---

## SDRF Cell Line Annotator

This script annotates the cell lines from an SDRF (Sample to Data relationship format) with cell line information from a provided [cell line metadata database](cl-annotations-db.tsv). It matches cell line names from the SDRF with entries in the database, considering exact matches for cell line, cellosaurus name, and cellosaurus accession, as well as partial matches against synonyms. If a match is found, the corresponding metadata (e.g., organism, disease, age, and more) is provided. If no match is found, the fields are populated with "not available" and a warning is logged.

```bash
python annotator.py --sdrf-file MSV000085836.sdrf.tsv --db-file cl-annotations-db.tsv --output-file suggested-terms.tsv
```

### Key Features:

- **Database Matching**: Matches cell line names from the SDRF file against a cell line database with multiple matching criteria (exact and synonym-based).
- **Synonym Handling**: Synonyms in the database are split by semicolon and compared to the cell line names, ensuring flexible matching.
- **Logging and Error Handling**: Warnings are logged for any unmatched cell lines, and errors are gracefully handled.
- **TSV Output**: Annotates and outputs the results to a new TSV file, maintaining structured data for downstream analysis.

---

## Requirements

To use the scripts, ensure the following is installed:

- **Python 3.x**
- Required libraries:  
- `pandas`
- `numpy`
- `spacy`
- install the `en_core_web_lg` model for spaCy: `python -m spacy download en_core_web_sm`

---
## Code of Conduct

We strive to foster a welcoming, inclusive, and respectful community where everyone feels encouraged to participate and contribute. As contributors and maintainers, we are committed to upholding ethical standards to prevent conflicts, harassment, and discrimination. We ask all participants to communicate respectfully, avoid personal attacks, and be constructive in their feedback. Contributions should be made with honesty, empathy, and respect for differing perspectives. Read the full [Code of Conduct](code_of_conduct.md).

## Commenting and contributing 

We welcome contributions from the community. If you would like to
contribute, please open an issue or a pull request. We will review your
contribution and provide feedback. We aim to be inclusive and
collaborative, and we welcome all contributions that are in line with
our goals.

- If you want to contribute to the manuscript, please do the following: 
  - Fork the repository
  - Change the content [manuscript.md](manuscript.md)
  - Submit a pull request
  - We will review your contribution and provide feedback
- If you want to discuss a topic, please open an issue. 

NOTE: If, based on your contribution, you would like to be added as a
co-author, please open an issue and provide your name and affiliation
and a short description of your contribution or a link to the relevant
issue and pull request.

--- 

## Contributors

- [Yasset Perez-Riverol](@ypriverol) - EMBL-EBI, UK
