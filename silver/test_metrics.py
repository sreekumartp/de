import pytest
from silver.metrics import row_metrics


def test_basic_csv(tmp_path):
    """Test metrics for a basic CSV with complete data."""
    source_csv = tmp_path / "test.csv"
    source_csv.write_text(
        "Id,Name,CreatedDate\n"
        "ABC123,Acme Corp,2023-01-01\n"
        "XYZ789,Beta Inc,2023-01-02\n"
        "DEF456,Gamma Ltd,2023-01-03\n"
    )

    result = row_metrics(str(source_csv))

    assert result['rows'] == 3
    assert result['columns'] == 3
    assert result['empty_cells'] == 0


def test_csv_with_empty_cells(tmp_path):
    """Test that empty cells are counted correctly."""
    source_csv = tmp_path / "test.csv"
    source_csv.write_text(
        "Id,Name,CreatedDate\n"
        "ABC123,Acme Corp,2023-01-01\n"
        "XYZ789,,2023-01-02\n"
        "DEF456,Gamma Ltd,\n"
    )

    result = row_metrics(str(source_csv))

    assert result['rows'] == 3
    assert result['columns'] == 3
    assert result['empty_cells'] == 2


def test_csv_with_whitespace_only_cells(tmp_path):
    """Test that whitespace-only cells are counted as empty."""
    source_csv = tmp_path / "test.csv"
    source_csv.write_text(
        "Id,Name,CreatedDate\n"
        "ABC123,   ,2023-01-01\n"
        "XYZ789,Beta Inc,  \n"
        "DEF456,Gamma Ltd,2023-01-03\n"
    )

    result = row_metrics(str(source_csv))

    assert result['rows'] == 3
    assert result['columns'] == 3
    assert result['empty_cells'] == 2


def test_csv_header_only(tmp_path):
    """Test that a CSV with only headers returns zero rows."""
    source_csv = tmp_path / "test.csv"
    source_csv.write_text("Id,Name,CreatedDate\n")

    result = row_metrics(str(source_csv))

    assert result['rows'] == 0
    assert result['columns'] == 3
    assert result['empty_cells'] == 0


def test_empty_csv(tmp_path):
    """Test that an empty CSV returns zeros."""
    source_csv = tmp_path / "test.csv"
    source_csv.write_text("")

    result = row_metrics(str(source_csv))

    assert result['rows'] == 0
    assert result['columns'] == 0
    assert result['empty_cells'] == 0


def test_single_column(tmp_path):
    """Test metrics for a CSV with a single column."""
    source_csv = tmp_path / "test.csv"
    source_csv.write_text(
        "Id\n"
        "ABC123\n"
        "XYZ789\n"
    )

    result = row_metrics(str(source_csv))

    assert result['rows'] == 2
    assert result['columns'] == 1
    assert result['empty_cells'] == 0


def test_many_columns(tmp_path):
    """Test metrics for a CSV with many columns."""
    source_csv = tmp_path / "test.csv"
    source_csv.write_text(
        "A,B,C,D,E,F,G\n"
        "1,2,3,4,5,6,7\n"
        "8,9,10,11,12,13,14\n"
    )

    result = row_metrics(str(source_csv))

    assert result['rows'] == 2
    assert result['columns'] == 7
    assert result['empty_cells'] == 0


def test_all_empty_cells(tmp_path):
    """Test CSV where all data cells are empty."""
    source_csv = tmp_path / "test.csv"
    source_csv.write_text(
        "Id,Name,CreatedDate\n"
        ",,\n"
        ",,\n"
    )

    result = row_metrics(str(source_csv))

    assert result['rows'] == 2
    assert result['columns'] == 3
    assert result['empty_cells'] == 6


def test_mixed_empty_and_whitespace(tmp_path):
    """Test CSV with mix of empty and whitespace-only cells."""
    source_csv = tmp_path / "test.csv"
    source_csv.write_text(
        "A,B,C\n"
        ",  , \n"
        "val, ,val\n"
    )

    result = row_metrics(str(source_csv))

    assert result['rows'] == 2
    assert result['columns'] == 3
    assert result['empty_cells'] == 4


def test_dict_structure(tmp_path):
    """Test that the returned dict has correct keys and types."""
    source_csv = tmp_path / "test.csv"
    source_csv.write_text(
        "Id,Name\n"
        "ABC123,Acme Corp\n"
    )

    result = row_metrics(str(source_csv))

    assert isinstance(result, dict)
    assert 'rows' in result
    assert 'columns' in result
    assert 'empty_cells' in result
    assert isinstance(result['rows'], int)
    assert isinstance(result['columns'], int)
    assert isinstance(result['empty_cells'], int)


def test_large_csv(tmp_path):
    """Test metrics on a CSV with many rows."""
    source_csv = tmp_path / "test.csv"
    lines = ["Id,Name,Value\n"]
    for i in range(100):
        lines.append(f"{i},name{i},val{i}\n")
    source_csv.write_text("".join(lines))

    result = row_metrics(str(source_csv))

    assert result['rows'] == 100
    assert result['columns'] == 3
    assert result['empty_cells'] == 0


def test_csv_with_special_characters(tmp_path):
    """Test CSV with special characters and quotes."""
    source_csv = tmp_path / "test.csv"
    source_csv.write_text(
        'Id,Description,Value\n'
        '"A001","Company, Inc.",100\n'
        '"A002","Beta & Co.",200\n'
    )

    result = row_metrics(str(source_csv))

    assert result['rows'] == 2
    assert result['columns'] == 3
    assert result['empty_cells'] == 0
