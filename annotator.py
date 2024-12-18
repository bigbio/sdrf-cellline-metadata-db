import click
import pandas as pd
import os

import logging
logging.basicConfig(level=logging.DEBUG)

@click.command()
@click.option('--sdrf-file', required=True, type=click.Path(exists=True), help='Path to the SDRF file.')
@click.option('--db-file', required=True, type=click.Path(exists=True), help='Path to the cell line database (TSV).', default='cl-annotations-db.tsv')
@click.option('--output-file', required=True, type=click.Path(), help='Path to the output TSV file.')
def annotate_sdrf(sdrf_file, db_file, output_file):
    """
    Output the columns needed to annotaed an SDRF file with cell line information from a database.

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
        required_columns = ['source name', 'characteristics[cell line]']
        if not all(col in sdrf_data.columns for col in required_columns):
            raise ValueError(f"SDRF file must contain the columns: {', '.join(required_columns)}")

        # Load cell line database
        click.echo(f"Loading cell line database: {db_file}")
        cellline_db = pd.read_csv(db_file, sep="\t", dtype=str)

        # Standardize database column names for matching
        db_columns = ['cell line', 'cellosaurus name', 'cellosaurus accession', 'synonyms']
        if not all(col in cellline_db.columns for col in db_columns):
            raise ValueError(f"Database file must contain the columns: {', '.join(db_columns)}")

        # Prepare the output data
        output_data = []

        click.echo("Annotating SDRF file...")
        for _, row in sdrf_data.iterrows():
            source_name = row['source name']
            cell_line_name = row['characteristics[cell line]']

            # Search for a match in the database
            match = cellline_db[
                (cellline_db['cell line'].str.lower() == str(cell_line_name).lower()) |
                (cellline_db['cellosaurus name'].str.lower() == str(cell_line_name).lower()) |
                (cellline_db['cellosaurus accession'].str.lower() == str(cell_line_name).lower()) |
                (cellline_db['synonyms'].str.contains(str(cell_line_name), case=False, na=False))
                ]

            if not match.empty:
                # Add the first match to the output
                db_row = match.iloc[0]
                output_data.append({
                    "source name": source_name,
                    "characteristics[cell line]": cell_line_name['cell line'],
                    "cell line": db_row['cell line'],
                    "cellosaurus name": db_row['cellosaurus name'],
                    "cellosaurus accession": db_row['cellosaurus accession'],
                    "bto cell line": db_row['bto cell line'],
                    "organism": db_row['organism'],
                    "organism part": db_row['organism part'],
                    "sampling site": db_row['sampling site'],
                    "age": db_row['age'],
                    "developmental stage": db_row['developmental stage'],
                    "sex": db_row["sex"],
                    "ancestry category": db_row['ancestry category'],
                    "disease": db_row['disease'],
                    "cell type": db_row['cell type'],
                    "material type": db_row['material type'],
                })
            else:
                # No match found
                output_data.append({
                    "source name": source_name,
                    "characteristics[cell line]": cell_line_name['cell line'],
                    "cell line": "not available",
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
                })
                logging.warning(f"No match found for cell line: {cell_line_name}")

        # Convert output data to DataFrame
        output_df = pd.DataFrame(output_data)

        # Save to output file
        click.echo(f"Saving annotated data to: {output_file}")
        output_df.to_csv(output_file, sep="\t", index=False)

        click.echo("Annotation complete.")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise

if __name__ == '__main__':
    annotate_sdrf()