# TODO: add JSON output format

def summarise(quality_report):
    """
    Format a quality report dict as a short plain-text report.

    Args:
        quality_report: dict returned by silver.quality.check()

    Returns:
        str: Plain-text report, one line per figure
    """
    lines = [
        f"Rows: {quality_report['rows']}",
        f"Blank Id: {quality_report['blank_id']}",
        f"Blank Name: {quality_report['blank_name']}",
        f"Duplicate Id: {quality_report['duplicate_id']}",
        f"Status: {'PASS' if quality_report['ok'] else 'FAIL'}",
    ]
    return '\n'.join(lines)


if __name__ == '__main__':
    import sys
    from silver.quality import check

    if len(sys.argv) != 2:
        print("Usage: python report.py <silver_csv>")
        sys.exit(1)

    silver_csv = sys.argv[1]
    result = check(silver_csv)
    print(summarise(result))

    if not result['ok']:
        sys.exit(1)
