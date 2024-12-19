import difflib
import logging
import re
from functools import lru_cache
from typing import Optional

import click
import pandas as pd

logging.basicConfig(level=logging.INFO)
import spacy
from typing import Dict, List, Tuple
from sklearn.metrics.pairwise import cosine_similarity


class CellLineMatcher:
    def __init__(
        self,
        model_name: str = "en_core_web_lg",
        threshold: float = 0.95,
        top_results: int = 5,
        similarity_method: str = "cosine",
        log_level: int = logging.INFO,
    ):
        """
        Advanced Cell Line Matcher with configurable NLP matching.

        :param model_name: SpaCy language model to use
        :param threshold: Minimum similarity threshold for matches
        :param top_results: Maximum number of results to return
        :param log_level: Logging level for the matcher
        """
        # Configure logging
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelName)s - %(message)s",
        )
        self.logger = logging.getLogger(self.__class__.__name__)

        # Load SpaCy model with robust error handling
        try:
            self.nlp = spacy.load(model_name)
            self.logger.info(f"Loaded SpaCy model: {model_name}")
        except OSError:
            self.logger.error(f"Model {model_name} not found")
            raise ValueError(
                f"SpaCy model {model_name} not found. "
                "Please download it using 'python -m spacy download <model_name>'"
            )

        # Configuration parameters
        self.threshold = threshold
        self.top_results = top_results
        self.similarity_method = similarity_method

    @lru_cache(maxsize=1000)
    def _preprocess_text(self, text: str) -> str:
        """
        Cached text preprocessing method.

        :param text: Input text to preprocess
        :return: Preprocessed text
        """
        return text.strip().lower()

    def _normalize_cellline_name(self, name: str) -> str:
        """
        Normalize cell line name for consistent matching.

        :param name: Original cell line name
        :return: Normalized name
        """
        # Remove spaces, convert to uppercase
        return re.sub(r"\s+", "", name.upper())

    def calculate_similarity(self, query_term: str, synonyms: List[str]) -> float:
        """
        Advanced similarity calculation with multiple strategies.

        :param query_term: Term to match
        :param synonyms: List of synonyms to compare
        :return: Maximum similarity score
        """
        # Preprocess inputs
        query_term = self._preprocess_text(query_term)
        synonyms = [self._preprocess_text(syn) for syn in synonyms]
        if self.similarity_method == "cosine":
            query_vec = self.nlp(" ".join(query_term)).vector
            synonyms_vec = [self.nlp(" ".join(synonym)).vector for synonym in synonyms]
            similarities = cosine_similarity([query_vec], synonyms_vec)
            return max(similarities[0])
        else:
            logging.error(f"Unknown similarity method: {self.similarity_method}")
            raise ValueError(f"Unknown similarity method: {self.similarity_method}")

    def map_celllines(
        self, cellline_query: str, all_celllines: Dict[str, Optional[str]]
    ) -> List[Tuple[str, float]]:
        """
        Map cell line query to most similar entries.

        :param cellline_query: Cell line to match
        :param all_celllines: Dictionary of cell lines and synonyms
        :return: Sorted list of matches with similarity scores
        """
        # Validate inputs
        if not cellline_query or not all_celllines:
            self.logger.warning("Empty query or cell lines dictionary")
            return []

        results = []

        for entry, synonyms in all_celllines.items():
            # Prepare synonym list
            if synonyms is None:
                synonyms = []
            else:
                synonyms = [synonym.strip() for synonym in synonyms.split(";")]

            # Always include the entry itself as a synonym
            synonyms.append(entry)

            # Calculate similarity
            similarity = self.calculate_similarity(cellline_query, synonyms)

            # Round similarity to handle floating-point precision
            similarity_round = round(similarity, 3)

            # Add to results if above threshold
            if self.similarity_method == "cosine":
                if similarity_round >= self.threshold:
                    results.append((entry, similarity_round))
            else:
                results.append((entry, similarity_round))

        # Sort results by similarity in descending order
        sorted_results = sorted(results, key=lambda x: x[1], reverse=True)

        # Prioritize exact matches (score 1.0)
        top_results = [
            result for result in sorted_results if result[1] > self.threshold
        ]

        # Add additional results if needed
        top_results.extend(
            [result for result in sorted_results if result[1] < self.threshold][
                : self.top_results
            ]
        )

        # Log matching results
        self.logger.debug(
            f"Matched '{cellline_query}' with {len(top_results)} results "
            f"above threshold {self.threshold}"
        )

        return top_results[: self.top_results]

@click.command()
@click.option(
    "--sdrf-file",
    required=True,
    type=click.Path(exists=True),
    help="Path to the SDRF file.",
)
@click.option(
    "--db-file",
    required=True,
    type=click.Path(exists=True),
    help="Path to the cell line database (TSV).",
    default="cl-annotations-db.tsv",
)
@click.option(
    "--output-file",
    required=True,
    type=click.Path(),
    help="Path to the output TSV file.",
)
def annotate_sdrf(sdrf_file, db_file, output_file):
    """
    Output the columns needed to annotate an SDRF file with cell line information from a database.

    This command-line tool reads an SDRF file and a cell line database file,
    matches cell line information, and outputs an annotated TSV file. It ensures
    the presence of required columns in both input files and logs warnings for
    unmatched cell lines.

    Parameters:
        sdrf_file (str): Path to the SDRF file.
        db_file (str): Path to the cell line database (TSV).
        output_file (str): Path to the output TSV file.
    """
    try:
        # Load SDRF file
        click.echo(f"Loading SDRF file: {sdrf_file}")
        sdrf_data = pd.read_csv(sdrf_file, sep="\t", dtype=str)
        # change all the columns to lower case
        sdrf_data.columns = [col.lower() for col in sdrf_data.columns]

        # Ensure required columns exist in the SDRF
        required_columns = ["source name", "characteristics[cell line]"]
        if not all(col in sdrf_data.columns for col in required_columns):
            raise ValueError(
                f"SDRF file must contain the columns: {', '.join(required_columns)}"
            )

        # Load cell line database
        click.echo(f"Loading cell line database: {db_file}")
        cellline_db = pd.read_csv(db_file, sep="\t", dtype=str)

        # Standardize database column names for matching
        db_columns = [
            "cell line",
            "cellosaurus name",
            "cellosaurus accession",
            "synonyms",
        ]
        if not all(col in cellline_db.columns for col in db_columns):
            raise ValueError(
                f"Database file must contain the columns: {', '.join(db_columns)}"
            )

        # Prepare the output data
        output_data = []
        unknown_cell_lines = []

        click.echo("Annotating SDRF file...")
        for _, row in sdrf_data.iterrows():
            source_name = row["source name"]
            cell_line_name = row["characteristics[cell line]"]

            # Search for a match in the database
            match = cellline_db[
                (cellline_db["cell line"].str.lower() == str(cell_line_name).lower())
                | (
                    cellline_db["cellosaurus name"].str.lower()
                    == str(cell_line_name).lower()
                )
                | (
                    cellline_db["cellosaurus accession"].str.lower()
                    == str(cell_line_name).lower()
                )
            ]

            if match.empty:
                # Split synonyms by semicolon, strip whitespaces, and check each synonym
                for idx, row in cellline_db.iterrows():
                    synonyms = row["synonyms"]  # Get the synonyms for the current row
                    if pd.notna(synonyms):  # Only proceed if synonyms are not NaN
                        synonyms_list = [
                            synonym.strip() for synonym in synonyms.split(";")
                        ]
                        # Check if any synonym matches the cell line name
                        for synonym in synonyms_list:
                            if cell_line_name.lower() in synonym.lower():
                                match = pd.DataFrame([row])  # Create a match
                                break  # Stop searching once a match is found
                    if not match.empty:  # If match found, break the loop
                        break

            if not match.empty:
                # Add the first match to the output
                db_row = match.iloc[0]
                output_data.append(
                    {
                        "source name": source_name,
                        "characteristics[cell line]": cell_line_name,
                        "cell line": db_row["cell line"],
                        "cellosaurus name": db_row["cellosaurus name"],
                        "cellosaurus accession": db_row["cellosaurus accession"],
                        "bto cell line": db_row["bto cell line"],
                        "organism": db_row["organism"],
                        "organism part": db_row["organism part"],
                        "sampling site": db_row["sampling site"],
                        "age": db_row["age"],
                        "developmental stage": db_row["developmental stage"],
                        "sex": db_row["sex"],
                        "ancestry category": db_row["ancestry category"],
                        "disease": db_row["disease"],
                        "cell type": db_row["cell type"],
                        "material type": db_row["Material type"],
                    }
                )
            else:
                # No match found
                output_data.append(
                    {
                        "source name": source_name,
                        "characteristics[cell line]": cell_line_name,
                        "cell line": cell_line_name,
                        "cellosaurus name": "not available",
                        "cellosaurus accession": "not available",
                        "bto cell line": "not available",
                        "organism": "not available",
                        "organism part": "not available",
                        "sampling site": "not available",
                        "age": "not available",
                        "developmental stage": "not available",
                        "sex": "not available",
                        "ancestry category": "not available",
                        "disease": "not available",
                        "cell type": "not available",
                        "material type": "not available",
                    }
                )
                unknown_cell_lines.append(cell_line_name)
                logging.warning(f"No match found for cell line: {cell_line_name}")

        # Convert output data to DataFrame
        output_df = pd.DataFrame(output_data)

        # Save to output file
        click.echo(f"Saving annotated data to: {output_file}")
        output_df.to_csv(output_file, sep="\t", index=False)

        # Log unknown cell lines
        if unknown_cell_lines:
            # Only log unique unknown cell lines
            unknown_cell_lines = list(set(unknown_cell_lines))
            logging.warning(f"Unknown cell lines: {', '.join(unknown_cell_lines)}")

            # check using NLP if the unknown cell lines can be matched
            cell_lines_db = (
                cellline_db[["cell line", "synonyms"]]
                .set_index("cell line")
                .to_dict()["synonyms"]
            )
            nlp_matcher = CellLineMatcher(similarity_method="cosine")
            for cell_line in unknown_cell_lines:
                matches_scores = nlp_matcher.map_celllines(cell_line, cell_lines_db)
                # Remove mathces in dictionary with score less than 0.9
                matches_scores = [
                    (match, score) for match, score in matches_scores if score > 0.98
                ]
                if matches_scores:
                    logging.warning(
                        f"Match found for cell line: {cell_line} with {matches_scores}"
                    )
                else:
                    logging.warning(f"No match found for cell line: {cell_line}")

        click.echo("Annotation complete.")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise

if __name__ == "__main__":
    annotate_sdrf()
