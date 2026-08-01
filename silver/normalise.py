import csv
import os
from pathlib import Path
from datetime import datetime


def parse_date(date_str):
    """
    Parse a date string in YYYY-MM-DD or DD/MM/YYYY format.

    Returns a string in ISO YYYY-MM-DD format, or None if parsing fails.
    """
    if not date_str:
        return None

    date_str = date_str.strip()

    formats = [
        '%Y-%m-%d',
        '%d/%m/%Y',
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue

    return None


def normalise(bronze_csv, out_dir):
    """
    Normalize bronze account data from CSV.

    For each row:
    - Strips surrounding whitespace from every value
    - Upper-cases Id column
    - Rewrites CreatedDate to ISO YYYY-MM-DD format
      (accepts YYYY-MM-DD and DD/MM/YYYY as input)
    - Drops rows with unparseable dates and counts them

    Args:
        bronze_csv: Path to source bronze CSV file
        out_dir: Output directory for normalized CSV

    Returns:
        dict with 'normalised' and 'dropped' counts
    """
    normalised = 0
    dropped = 0

    Path(out_dir).mkdir(parents=True, exist_ok=True)

    output_path = os.path.join(out_dir, 'accounts.csv')

    with open(bronze_csv, 'r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)

        if reader.fieldnames is None:
            raise ValueError("CSV file is empty or invalid")

        with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
            writer.writeheader()

            for row in reader:
                stripped_row = {key: value.strip() for key, value in row.items()}

                if 'Id' in stripped_row:
                    stripped_row['Id'] = stripped_row['Id'].upper()

                if 'CreatedDate' in stripped_row:
                    parsed_date = parse_date(stripped_row['CreatedDate'])
                    if parsed_date is None:
                        dropped += 1
                        continue
                    stripped_row['CreatedDate'] = parsed_date

                writer.writerow(stripped_row)
                normalised += 1

    return {'normalised': normalised, 'dropped': dropped}


if __name__ == '__main__':
    import sys

    if len(sys.argv) != 3:
        print("Usage: python normalise.py <bronze_csv> <out_dir>")
        sys.exit(1)

    bronze_csv = sys.argv[1]
    out_dir = sys.argv[2]

    result = normalise(bronze_csv, out_dir)
    print(f"Normalised: {result['normalised']}")
    print(f"Dropped: {result['dropped']}")
