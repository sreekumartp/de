import csv
import pytest
from silver.normalise import normalise


def test_whitespace_stripping(tmp_path):
    """Test that surrounding whitespace is stripped from all values."""
    source_csv = tmp_path / "source.csv"
    source_csv.write_text(
        "Id,Name,CreatedDate\n"
        "  001  , Acme Corp , 2023-01-01 \n"
        "002,Beta Inc,2023-01-02\n"
    )

    out_dir = tmp_path / "output"
    result = normalise(str(source_csv), str(out_dir))

    assert result['normalised'] == 2
    assert result['dropped'] == 0

    output_file = out_dir / "accounts.csv"
    with open(output_file, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert rows[0]['Id'] == '001'
    assert rows[0]['Name'] == 'Acme Corp'
    assert rows[0]['CreatedDate'] == '2023-01-01'


def test_id_upper_casing(tmp_path):
    """Test that Id column is upper-cased."""
    source_csv = tmp_path / "source.csv"
    source_csv.write_text(
        "Id,Name,CreatedDate\n"
        "abc123,Acme Corp,2023-01-01\n"
        "XyZ789,Beta Inc,2023-01-02\n"
    )

    out_dir = tmp_path / "output"
    result = normalise(str(source_csv), str(out_dir))

    assert result['normalised'] == 2
    assert result['dropped'] == 0

    output_file = out_dir / "accounts.csv"
    with open(output_file, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert rows[0]['Id'] == 'ABC123'
    assert rows[1]['Id'] == 'XYZ789'


def test_date_format_yyyy_mm_dd(tmp_path):
    """Test that YYYY-MM-DD date format is accepted and preserved."""
    source_csv = tmp_path / "source.csv"
    source_csv.write_text(
        "Id,Name,CreatedDate\n"
        "001,Acme Corp,2023-01-15\n"
        "002,Beta Inc,2024-12-31\n"
    )

    out_dir = tmp_path / "output"
    result = normalise(str(source_csv), str(out_dir))

    assert result['normalised'] == 2
    assert result['dropped'] == 0

    output_file = out_dir / "accounts.csv"
    with open(output_file, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert rows[0]['CreatedDate'] == '2023-01-15'
    assert rows[1]['CreatedDate'] == '2024-12-31'


def test_date_format_dd_mm_yyyy(tmp_path):
    """Test that DD/MM/YYYY date format is converted to YYYY-MM-DD."""
    source_csv = tmp_path / "source.csv"
    source_csv.write_text(
        "Id,Name,CreatedDate\n"
        "001,Acme Corp,15/01/2023\n"
        "002,Beta Inc,31/12/2024\n"
    )

    out_dir = tmp_path / "output"
    result = normalise(str(source_csv), str(out_dir))

    assert result['normalised'] == 2
    assert result['dropped'] == 0

    output_file = out_dir / "accounts.csv"
    with open(output_file, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert rows[0]['CreatedDate'] == '2023-01-15'
    assert rows[1]['CreatedDate'] == '2024-12-31'


def test_unparseable_date_dropped(tmp_path):
    """Test that rows with unparseable dates are dropped and counted."""
    source_csv = tmp_path / "source.csv"
    source_csv.write_text(
        "Id,Name,CreatedDate\n"
        "001,Acme Corp,2023-01-01\n"
        "002,Beta Inc,invalid-date\n"
        "003,Gamma Ltd,2023-01-03\n"
    )

    out_dir = tmp_path / "output"
    result = normalise(str(source_csv), str(out_dir))

    assert result['normalised'] == 2
    assert result['dropped'] == 1

    output_file = out_dir / "accounts.csv"
    with open(output_file, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 2
    assert rows[0]['Id'] == '001'
    assert rows[1]['Id'] == '003'


def test_multiple_unparseable_dates(tmp_path):
    """Test that multiple rows with unparseable dates are all dropped and counted."""
    source_csv = tmp_path / "source.csv"
    source_csv.write_text(
        "Id,Name,CreatedDate\n"
        "001,Acme Corp,not-a-date\n"
        "002,Beta Inc,2023-13-45\n"
        "003,Gamma Ltd,2023-01-01\n"
        "004,Delta Inc,bad-format\n"
    )

    out_dir = tmp_path / "output"
    result = normalise(str(source_csv), str(out_dir))

    assert result['normalised'] == 1
    assert result['dropped'] == 3

    output_file = out_dir / "accounts.csv"
    with open(output_file, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 1
    assert rows[0]['Id'] == '003'


def test_mixed_date_formats(tmp_path):
    """Test that both date formats work in the same CSV."""
    source_csv = tmp_path / "source.csv"
    source_csv.write_text(
        "Id,Name,CreatedDate\n"
        "001,Acme Corp,2023-01-15\n"
        "002,Beta Inc,15/01/2023\n"
        "003,Gamma Ltd,2024-06-30\n"
    )

    out_dir = tmp_path / "output"
    result = normalise(str(source_csv), str(out_dir))

    assert result['normalised'] == 3
    assert result['dropped'] == 0

    output_file = out_dir / "accounts.csv"
    with open(output_file, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert rows[0]['CreatedDate'] == '2023-01-15'
    assert rows[1]['CreatedDate'] == '2023-01-15'
    assert rows[2]['CreatedDate'] == '2024-06-30'


def test_preserves_other_columns(tmp_path):
    """Test that other columns are preserved during normalization."""
    source_csv = tmp_path / "source.csv"
    source_csv.write_text(
        "Id,Name,CreatedDate,Industry,Status\n"
        "  001  , Acme Corp , 2023-01-01 , Technology , Active \n"
        "002,Beta Inc,2023-01-02,Finance,Inactive\n"
    )

    out_dir = tmp_path / "output"
    result = normalise(str(source_csv), str(out_dir))

    assert result['normalised'] == 2
    assert result['dropped'] == 0

    output_file = out_dir / "accounts.csv"
    with open(output_file, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert rows[0]['Industry'] == 'Technology'
    assert rows[0]['Status'] == 'Active'
    assert rows[1]['Industry'] == 'Finance'
    assert rows[1]['Status'] == 'Inactive'


def test_counts_dict_structure(tmp_path):
    """Test that the returned dict has correct keys and types."""
    source_csv = tmp_path / "source.csv"
    source_csv.write_text(
        "Id,Name,CreatedDate\n"
        "001,Acme Corp,2023-01-01\n"
    )

    out_dir = tmp_path / "output"
    result = normalise(str(source_csv), str(out_dir))

    assert isinstance(result, dict)
    assert 'normalised' in result
    assert 'dropped' in result
    assert isinstance(result['normalised'], int)
    assert isinstance(result['dropped'], int)


def test_empty_csv(tmp_path):
    """Test that empty CSV raises ValueError."""
    source_csv = tmp_path / "source.csv"
    source_csv.write_text("")

    out_dir = tmp_path / "output"

    with pytest.raises(ValueError, match="CSV file is empty or invalid"):
        normalise(str(source_csv), str(out_dir))


def test_header_preserved(tmp_path):
    """Test that CSV header is preserved in output."""
    source_csv = tmp_path / "source.csv"
    source_csv.write_text(
        "Id,Name,CreatedDate,Industry\n"
        "001,Acme Corp,2023-01-01,Tech\n"
    )

    out_dir = tmp_path / "output"
    normalise(str(source_csv), str(out_dir))

    output_file = out_dir / "accounts.csv"
    with open(output_file, 'r') as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames

    assert header == ['Id', 'Name', 'CreatedDate', 'Industry']
