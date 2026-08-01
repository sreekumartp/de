import csv
from pathlib import Path


def check(silver_csv):
    """
    Perform data quality checks on normalized silver accounts data.

    Validates that all rows have non-empty Id and Name fields, and that
    all Ids are unique.

    Args:
        silver_csv: Path to silver accounts CSV file

    Returns:
        dict with:
        - 'rows': Total number of data rows
        - 'blank_id': Count of rows with empty Id
        - 'blank_name': Count of rows with empty Name
        - 'duplicate_id': Count of duplicate Id values
        - 'ok': True only when blank_id, blank_name, and duplicate_id are all zero
    """
    rows = 0
    blank_id = 0
    blank_name = 0
    seen_ids = set()
    duplicate_id = 0

    with open(silver_csv, 'r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)

        if reader.fieldnames is None:
            return {
                'rows': 0,
                'blank_id': 0,
                'blank_name': 0,
                'duplicate_id': 0,
                'ok': True,
            }

        for row in reader:
            rows += 1

            row_id = row.get('Id', '').strip()
            row_name = row.get('Name', '').strip()

            if not row_id:
                blank_id += 1

            if not row_name:
                blank_name += 1

            if row_id:
                if row_id in seen_ids:
                    duplicate_id += 1
                else:
                    seen_ids.add(row_id)

    ok = blank_id == 0 and blank_name == 0 and duplicate_id == 0

    return {
        'rows': rows,
        'blank_id': blank_id,
        'blank_name': blank_name,
        'duplicate_id': duplicate_id,
        'ok': ok,
    }


if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2:
        print("Usage: python quality.py <silver_csv>")
        sys.exit(1)

    silver_csv = sys.argv[1]

    result = check(silver_csv)

    print(f"Rows: {result['rows']}")
    print(f"Blank Id: {result['blank_id']}")
    print(f"Blank Name: {result['blank_name']}")
    print(f"Duplicate Id: {result['duplicate_id']}")
    print(f"Status: {'PASS' if result['ok'] else 'FAIL'}")

    if not result['ok']:
        sys.exit(1)
