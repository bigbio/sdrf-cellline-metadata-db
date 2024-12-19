# Cell Passports Database Creator

This script processes Cell Passport files to create a structured database of cell lines. It extracts essential details such as model name, organism part, disease, sampling site, and more, outputting the results as a tab-separated file.

---

## Features

- **Filter by Cell Line**: Only processes entries where `model_type` is `Cell Line`.
- **Field Mapping**: Maps raw column names to meaningful database fields.
- **Data Cleaning**: Fills missing values with "no available" and formats age without decimals.
- **Flexible CLI**: Simple command-line interface to specify input and output files.

--- 

## Input File Format

The input CSV file should contain the following columns (among others):

- model_name
- synonyms
- tissue
- cancer_type
- sample_site
- cancer_type_detail
- RRID
- species
- gender
- ethnicity
- age_at_sampling
- model_id
- sample_id
- patient_id
- model_type (used to filter Cell Line entries)

## Output File Format

The output TSV file will contain the following fields:

- cell line
- synonyms	
- organism part
- disease
- sampling site
- cancer type detail
- cellosaurus accession
- organism
- sex
- ancestry category
- age
- model_id
- sample_id
- patient_id

---

## Requirements

- Python 3.7+
- Required Python libraries:
  - `click`
  - `pandas`

## Installation

Clone the repository and install the required Python libraries:

```bash
git clone <repository-url>
cd <repository-directory>
pip install -r requirements.txt
