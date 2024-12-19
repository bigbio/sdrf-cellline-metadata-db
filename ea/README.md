# EA Database Creator

The `ea-database` tool is a command-line utility for creating a comprehensive database of cell lines from the Expression Atlas. It processes large expression atlas files and generates a database containing detailed metadata for each cell line, such as organism, disease, developmental stage, and more.

---

## Features

- Extracts metadata from tab-delimited Expression Atlas files.
- Consolidates information from multiple files into a unified database.
- Supports the inclusion of a curated cell line catalog for additional metadata.
- Outputs a tab-separated `.tsv` file with the compiled database.

--- 

## Installation

### Requirements

- Python 3.7 or higher
- Dependencies listed in `requirements.txt`:
  - `numpy`
  - `pandas`
  - `click`

### Setup

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd <repository_directory>
