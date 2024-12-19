# Cellosaurus Database Parser

This script processes Cellosaurus database files and generates a structured output database. It also integrates information from ontologies such as BTO (BRENDA Tissue Ontology) and CL (Cell Ontology) to enrich the resulting dataset with detailed annotations.

---

## Features

- **Parse OBO files:** Reads ontology files (`*.obo`) to extract hierarchical relationships and synonyms.
- **Integrate ontology data:** Links Cellosaurus entries to BTO and CL ontologies for enhanced annotations.
- **Generate structured output:** Creates a tab-separated file with detailed fields such as cell line names, accessions, organism details, and more.

---

## Usage

```bash
python script_name.py cellosaurus-database --cellosaurus <cellosaurus_file.gz> \
--bto <bto_file.obo> --cl <cl_file.obo> --output <output_file.tsv>
```

### Arguments

- **--cellosaurus**: Path to the gzipped Cellosaurus database file.
- **--bto**: Path to the BTO ontology file (*.obo).
- **--cl**: Path to the CL ontology file (*.obo).
- **--output**: Path to the output file where the processed database will be saved.

---

## File Descriptions

### Input Files

- **Cellosaurus File**: The Cellosaurus database file in gzipped format.
- **BTO Ontology File**: BRENDA Tissue Ontology file (*.obo).
- **CL Ontology File**: Cell Ontology file (*.obo).

### Output File

A tab-separated values (TSV) file containing structured data with the following fields:

- cellosaurus name
- cellosaurus accession
- bto cell line
- organism
- age
- developmental stage
- sex
- ancestry category
- disease
- cell type
- sampling site
- synonyms

### Functions

#### Core Functions

```python
 # Parses OBO ontology files into a dictionary.
 read_obo_file(file_path: str) -> Dict[str, dict] 
 
 # Formats a list into a semicolon-separated string or returns "no available" if empty.  
 string_if_not_empty(param: List[Union[str, float]]) -> str
 
 # Writes parsed Cellosaurus data into a TSV file.
 write_database_cellosaurus(current_cl_database: List[dict], database: str)
 
 # Parses the Cellosaurus file and integrates BTO and CL annotations.
 parse_cellosaurus_file(file_path: str, bto: Dict[str, dict], cl_type: Dict[str, dict]) -> List[dict]

 # Creates a new entry for a cell line based on the parsed Cellosaurus data.
 create_new_entry_from_cellosaurus(cellosaurus: dict) -> dict
```

#### Helper Functions

```python
    # Checks if a text contains age information.
    is_age_in_text(age_text: str) -> bool
    
    # Extracts sampling site information from comments.
    get_sampling_site(cellosaurus_comment: str) -> Optional[str]
    
    # Extracts cell type information from comments.
    get_cell_type(cellosaurus_comment: str) -> Optional[str]
    
    # Parses organism and taxonomy information.
    parse_cellosaurus_taxonomy(organism_text: str) -> Tuple[Optional[str], Optional[str]]
```

---
## Requirements

- Python 3.7+
- Required Python libraries:
  - `click`
  - `numpy`
  - `re`
  - `gzip`

## Installation

Clone the repository and install the required Python libraries:

```bash
git clone <repository-url>
cd <repository-directory>
pip install -r requirements.txt


