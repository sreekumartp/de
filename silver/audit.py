import csv
import sys


def audit(silver_csv):
    """
    Audit normalized silver accounts data for quality issues.

    Checks for:
    - Blank Id values
    - Blank Name values
    - Duplicate Id values

    Args:
        silver_csv: Path to silver accounts CSV file

    Returns:
        List of warning strings, one per issue found. Empty list if no issues.
    """
    warnings = []
    seen_ids = {}  # id -> row_number where first seen

    with open(silver_csv, 'r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)

        if reader.fieldnames is None:
            return []

        row_num = 1  # Header is row 1
        for row in reader:
            row_num += 1  # First data row is row 2

            row_id = row.get('Id', '').strip()
            row_name = row.get('Name', '').strip()

            if not row_id:
                warnings.append(f"Row {row_num}: blank Id")

            if not row_name:
                warnings.append(f"Row {row_num}: blank Name")

            if row_id:
                if row_id in seen_ids:
                    warnings.append(f"Row {row_num}: duplicate Id {row_id}")
                else:
                    seen_ids[row_id] = row_num

    return warnings


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python audit.py <silver_csv>")
        sys.exit(1)

    silver_csv = sys.argv[1]

    issues = audit(silver_csv)

    for issue in issues:
        print(issue)

    if issues:
        sys.exit(1)
