import csv
import os
from pathlib import Path


def ingest(source_path, out_dir):
    """
    Ingest Salesforce accounts CSV export.

    Required columns: Id, Name, CreatedDate

    Rows are ingested if they contain all three required columns with non-empty values.
    Rows missing or having empty values for any required column are rejected.

    Args:
        source_path: Path to source CSV file
        out_dir: Output directory for ingested and rejected CSVs

    Returns:
        dict with 'ingested' and 'rejected' counts
    """
    ingested = 0
    rejected = 0

    required_columns = ['Id', 'Name', 'CreatedDate']

    # Create output directory if needed
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    # Paths for output files
    ingested_path = os.path.join(out_dir, 'accounts.csv')
    rejected_path = os.path.join(out_dir, 'accounts_rejects.csv')

    with open(source_path, 'r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)

        # Verify required columns exist in CSV
        if reader.fieldnames is None:
            raise ValueError("CSV file is empty or invalid")

        missing_columns = set(required_columns) - set(reader.fieldnames)
        if missing_columns:
            raise ValueError(f"CSV missing required columns: {', '.join(sorted(missing_columns))}")

        # Prepare output file writers
        with open(ingested_path, 'w', newline='', encoding='utf-8') as outfile_ingested:
            with open(rejected_path, 'w', newline='', encoding='utf-8') as outfile_rejected:
                # Write headers using all fieldnames from input
                writer_ingested = csv.DictWriter(outfile_ingested, fieldnames=reader.fieldnames)
                writer_rejected = csv.DictWriter(outfile_rejected, fieldnames=reader.fieldnames)

                writer_ingested.writeheader()
                writer_rejected.writeheader()

                # Process rows
                for row in reader:
                    # Check if all required columns have non-empty values
                    has_all_required = all(
                        row.get(col, '').strip()
                        for col in required_columns
                    )

                    if has_all_required:
                        writer_ingested.writerow(row)
                        ingested += 1
                    else:
                        writer_rejected.writerow(row)
                        rejected += 1

    return {'ingested': ingested, 'rejected': rejected}


if __name__ == '__main__':
    import sys

    if len(sys.argv) != 3:
        print("Usage: python ingest_accounts.py <source_path> <out_dir>")
        sys.exit(1)

    source_path = sys.argv[1]
    out_dir = sys.argv[2]

    result = ingest(source_path, out_dir)
    print(f"Ingested: {result['ingested']}")
    print(f"Rejected: {result['rejected']}")
