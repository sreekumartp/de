import csv
import pytest
from bronze.ingest_accounts import ingest


def test_all_valid_rows(tmp_path):
    """Test that rows with all required columns are ingested."""
    source_csv = tmp_path / "source.csv"
    source_csv.write_text(
        "Id,Name,CreatedDate\n"
        "001,Acme Corp,2023-01-01\n"
        "002,Beta Inc,2023-01-02\n"
        "003,Gamma Ltd,2023-01-03\n"
    )

    out_dir = tmp_path / "output"
    result = ingest(str(source_csv), str(out_dir))

    assert result['ingested'] == 3
    assert result['rejected'] == 0

    ingested_file = out_dir / "accounts.csv"
    assert ingested_file.exists()
    lines = ingested_file.read_text().strip().split('\n')
    assert len(lines) == 4


def test_missing_id(tmp_path):
    """Test that rows with missing Id are rejected."""
    source_csv = tmp_path / "source.csv"
    source_csv.write_text(
        "Id,Name,CreatedDate\n"
        "001,Acme Corp,2023-01-01\n"
        ",Beta Inc,2023-01-02\n"
    )

    out_dir = tmp_path / "output"
    result = ingest(str(source_csv), str(out_dir))

    assert result['ingested'] == 1
    assert result['rejected'] == 1

    rejected_file = out_dir / "accounts_rejects.csv"
    assert rejected_file.exists()


def test_empty_id(tmp_path):
    """Test that rows with empty Id (whitespace only) are rejected."""
    source_csv = tmp_path / "source.csv"
    source_csv.write_text(
        "Id,Name,CreatedDate\n"
        "001,Acme Corp,2023-01-01\n"
        "   ,Beta Inc,2023-01-02\n"
    )

    out_dir = tmp_path / "output"
    result = ingest(str(source_csv), str(out_dir))

    assert result['ingested'] == 1
    assert result['rejected'] == 1


def test_missing_name(tmp_path):
    """Test that rows with missing Name are rejected."""
    source_csv = tmp_path / "source.csv"
    source_csv.write_text(
        "Id,Name,CreatedDate\n"
        "001,,2023-01-01\n"
        "002,Beta Inc,2023-01-02\n"
    )

    out_dir = tmp_path / "output"
    result = ingest(str(source_csv), str(out_dir))

    assert result['ingested'] == 1
    assert result['rejected'] == 1


def test_empty_name(tmp_path):
    """Test that rows with empty Name (whitespace only) are rejected."""
    source_csv = tmp_path / "source.csv"
    source_csv.write_text(
        "Id,Name,CreatedDate\n"
        "001,Acme Corp,2023-01-01\n"
        "002,   ,2023-01-02\n"
    )

    out_dir = tmp_path / "output"
    result = ingest(str(source_csv), str(out_dir))

    assert result['ingested'] == 1
    assert result['rejected'] == 1


def test_missing_created_date(tmp_path):
    """Test that rows with missing CreatedDate are rejected."""
    source_csv = tmp_path / "source.csv"
    source_csv.write_text(
        "Id,Name,CreatedDate\n"
        "001,Acme Corp,2023-01-01\n"
        "002,Beta Inc,\n"
    )

    out_dir = tmp_path / "output"
    result = ingest(str(source_csv), str(out_dir))

    assert result['ingested'] == 1
    assert result['rejected'] == 1


def test_empty_created_date(tmp_path):
    """Test that rows with empty CreatedDate (whitespace only) are rejected."""
    source_csv = tmp_path / "source.csv"
    source_csv.write_text(
        "Id,Name,CreatedDate\n"
        "001,Acme Corp,2023-01-01\n"
        "002,Beta Inc,  \n"
    )

    out_dir = tmp_path / "output"
    result = ingest(str(source_csv), str(out_dir))

    assert result['ingested'] == 1
    assert result['rejected'] == 1


def test_counts_dict_structure(tmp_path):
    """Test that the returned dict has correct keys and types."""
    source_csv = tmp_path / "source.csv"
    source_csv.write_text(
        "Id,Name,CreatedDate\n"
        "001,Acme Corp,2023-01-01\n"
        ",Beta Inc,2023-01-02\n"
    )

    out_dir = tmp_path / "output"
    result = ingest(str(source_csv), str(out_dir))

    assert isinstance(result, dict)
    assert 'ingested' in result
    assert 'rejected' in result
    assert isinstance(result['ingested'], int)
    assert isinstance(result['rejected'], int)


def test_header_row_in_ingested(tmp_path):
    """Test that accounts.csv preserves the header row."""
    source_csv = tmp_path / "source.csv"
    source_csv.write_text(
        "Id,Name,CreatedDate,Industry\n"
        "001,Acme Corp,2023-01-01,Technology\n"
        "002,Beta Inc,2023-01-02,Finance\n"
    )

    out_dir = tmp_path / "output"
    ingest(str(source_csv), str(out_dir))

    ingested_file = out_dir / "accounts.csv"
    with open(ingested_file, 'r') as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames

    assert header == ['Id', 'Name', 'CreatedDate', 'Industry']


def test_header_row_in_rejected(tmp_path):
    """Test that accounts_rejects.csv preserves the header row."""
    source_csv = tmp_path / "source.csv"
    source_csv.write_text(
        "Id,Name,CreatedDate,Industry\n"
        "001,Acme Corp,2023-01-01,Technology\n"
        ",Beta Inc,2023-01-02,Finance\n"
    )

    out_dir = tmp_path / "output"
    ingest(str(source_csv), str(out_dir))

    rejected_file = out_dir / "accounts_rejects.csv"
    with open(rejected_file, 'r') as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames

    assert header == ['Id', 'Name', 'CreatedDate', 'Industry']


def test_missing_required_column_raises_error(tmp_path):
    """Test that missing required column in header raises ValueError."""
    source_csv = tmp_path / "source.csv"
    source_csv.write_text(
        "Id,Name\n"
        "001,Acme Corp\n"
    )

    out_dir = tmp_path / "output"

    with pytest.raises(ValueError, match="CSV missing required columns"):
        ingest(str(source_csv), str(out_dir))


def test_empty_csv_raises_error(tmp_path):
    """Test that empty CSV raises ValueError."""
    source_csv = tmp_path / "source.csv"
    source_csv.write_text("")

    out_dir = tmp_path / "output"

    with pytest.raises(ValueError, match="CSV file is empty or invalid"):
        ingest(str(source_csv), str(out_dir))
