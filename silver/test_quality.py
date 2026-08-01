import pytest
from silver.quality import check


def test_clean_file(tmp_path):
    """Test that a clean file with no quality issues passes all checks."""
    source_csv = tmp_path / "accounts.csv"
    source_csv.write_text(
        "Id,Name,CreatedDate\n"
        "ABC123,Acme Corp,2023-01-01\n"
        "XYZ789,Beta Inc,2023-01-02\n"
        "DEF456,Gamma Ltd,2023-01-03\n"
    )

    result = check(str(source_csv))

    assert result['rows'] == 3
    assert result['blank_id'] == 0
    assert result['blank_name'] == 0
    assert result['duplicate_id'] == 0
    assert result['ok'] is True


def test_blank_id(tmp_path):
    """Test detection of rows with blank Id."""
    source_csv = tmp_path / "accounts.csv"
    source_csv.write_text(
        "Id,Name,CreatedDate\n"
        "ABC123,Acme Corp,2023-01-01\n"
        ",Beta Inc,2023-01-02\n"
        "DEF456,Gamma Ltd,2023-01-03\n"
    )

    result = check(str(source_csv))

    assert result['rows'] == 3
    assert result['blank_id'] == 1
    assert result['blank_name'] == 0
    assert result['duplicate_id'] == 0
    assert result['ok'] is False


def test_blank_name(tmp_path):
    """Test detection of rows with blank Name."""
    source_csv = tmp_path / "accounts.csv"
    source_csv.write_text(
        "Id,Name,CreatedDate\n"
        "ABC123,Acme Corp,2023-01-01\n"
        "XYZ789,,2023-01-02\n"
        "DEF456,Gamma Ltd,2023-01-03\n"
    )

    result = check(str(source_csv))

    assert result['rows'] == 3
    assert result['blank_id'] == 0
    assert result['blank_name'] == 1
    assert result['duplicate_id'] == 0
    assert result['ok'] is False


def test_duplicate_id(tmp_path):
    """Test detection of duplicate Ids."""
    source_csv = tmp_path / "accounts.csv"
    source_csv.write_text(
        "Id,Name,CreatedDate\n"
        "ABC123,Acme Corp,2023-01-01\n"
        "ABC123,Different Corp,2023-01-02\n"
        "DEF456,Gamma Ltd,2023-01-03\n"
    )

    result = check(str(source_csv))

    assert result['rows'] == 3
    assert result['blank_id'] == 0
    assert result['blank_name'] == 0
    assert result['duplicate_id'] == 1
    assert result['ok'] is False


def test_multiple_blank_ids(tmp_path):
    """Test counting multiple rows with blank Ids."""
    source_csv = tmp_path / "accounts.csv"
    source_csv.write_text(
        "Id,Name,CreatedDate\n"
        ",Acme Corp,2023-01-01\n"
        "ABC123,Beta Inc,2023-01-02\n"
        ",Gamma Ltd,2023-01-03\n"
    )

    result = check(str(source_csv))

    assert result['rows'] == 3
    assert result['blank_id'] == 2
    assert result['blank_name'] == 0
    assert result['duplicate_id'] == 0
    assert result['ok'] is False


def test_multiple_blank_names(tmp_path):
    """Test counting multiple rows with blank Names."""
    source_csv = tmp_path / "accounts.csv"
    source_csv.write_text(
        "Id,Name,CreatedDate\n"
        "ABC123,,2023-01-01\n"
        "XYZ789,Beta Inc,2023-01-02\n"
        "DEF456,,2023-01-03\n"
    )

    result = check(str(source_csv))

    assert result['rows'] == 3
    assert result['blank_id'] == 0
    assert result['blank_name'] == 2
    assert result['duplicate_id'] == 0
    assert result['ok'] is False


def test_multiple_duplicate_ids(tmp_path):
    """Test counting multiple duplicate Ids."""
    source_csv = tmp_path / "accounts.csv"
    source_csv.write_text(
        "Id,Name,CreatedDate\n"
        "ABC123,Acme Corp,2023-01-01\n"
        "ABC123,Different Corp,2023-01-02\n"
        "XYZ789,Beta Inc,2023-01-03\n"
        "XYZ789,Another Corp,2023-01-04\n"
    )

    result = check(str(source_csv))

    assert result['rows'] == 4
    assert result['blank_id'] == 0
    assert result['blank_name'] == 0
    assert result['duplicate_id'] == 2
    assert result['ok'] is False


def test_combined_issues(tmp_path):
    """Test detection of multiple types of quality issues together."""
    source_csv = tmp_path / "accounts.csv"
    source_csv.write_text(
        "Id,Name,CreatedDate\n"
        "ABC123,Acme Corp,2023-01-01\n"
        ",Beta Inc,2023-01-02\n"
        "DEF456,,2023-01-03\n"
        "ABC123,Different Corp,2023-01-04\n"
    )

    result = check(str(source_csv))

    assert result['rows'] == 4
    assert result['blank_id'] == 1
    assert result['blank_name'] == 1
    assert result['duplicate_id'] == 1
    assert result['ok'] is False


def test_whitespace_only_treated_as_blank(tmp_path):
    """Test that whitespace-only values are treated as blank."""
    source_csv = tmp_path / "accounts.csv"
    source_csv.write_text(
        "Id,Name,CreatedDate\n"
        "   ,Acme Corp,2023-01-01\n"
        "ABC123,   ,2023-01-02\n"
        "DEF456,Gamma Ltd,2023-01-03\n"
    )

    result = check(str(source_csv))

    assert result['rows'] == 3
    assert result['blank_id'] == 1
    assert result['blank_name'] == 1
    assert result['duplicate_id'] == 0
    assert result['ok'] is False


def test_empty_csv_headers_only(tmp_path):
    """Test that a CSV with only headers returns zero rows and passes."""
    source_csv = tmp_path / "accounts.csv"
    source_csv.write_text("Id,Name,CreatedDate\n")

    result = check(str(source_csv))

    assert result['rows'] == 0
    assert result['blank_id'] == 0
    assert result['blank_name'] == 0
    assert result['duplicate_id'] == 0
    assert result['ok'] is True


def test_single_good_row(tmp_path):
    """Test a single valid row."""
    source_csv = tmp_path / "accounts.csv"
    source_csv.write_text(
        "Id,Name,CreatedDate\n"
        "ABC123,Acme Corp,2023-01-01\n"
    )

    result = check(str(source_csv))

    assert result['rows'] == 1
    assert result['blank_id'] == 0
    assert result['blank_name'] == 0
    assert result['duplicate_id'] == 0
    assert result['ok'] is True
