import csv


def row_metrics(csv_path):
    """
    Calculate metrics for a CSV file.

    Args:
        csv_path: Path to CSV file

    Returns:
        dict with:
        - 'rows': Total number of data rows (excluding header)
        - 'columns': Total number of columns
        - 'empty_cells': Count of cells with empty or whitespace-only values
    """
    rows = 0
    columns = 0
    empty_cells = 0

    with open(csv_path, 'r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)

        if reader.fieldnames is None:
            return {
                'rows': 0,
                'columns': 0,
                'empty_cells': 0,
            }

        columns = len(reader.fieldnames)

        for row in reader:
            rows += 1
            for value in row.values():
                if value is None or value.strip() == '':
                    empty_cells += 1

    return {
        'rows': rows,
        'columns': columns,
        'empty_cells': empty_cells,
    }


if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2:
        print("Usage: python -m silver.metrics <csv_path>")
        sys.exit(1)

    csv_path = sys.argv[1]

    result = row_metrics(csv_path)

    print(f"Rows: {result['rows']}")
    print(f"Columns: {result['columns']}")
    print(f"Empty cells: {result['empty_cells']}")
