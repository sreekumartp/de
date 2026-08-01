# Bronze

The Bronze layer contains Source-to-Bronze ingestion steps for data pipeline layers.

## Accounts Ingestion

The `ingest_accounts.py` module ingests Salesforce account CSV exports into the Bronze layer.

### Required Columns

The input CSV must contain the following columns:
- `Id`: Salesforce account identifier
- `Name`: Account name
- `CreatedDate`: Account creation date

### Rejection Rule

Rows are rejected (written to `accounts_rejects.csv`) if they are missing or have empty values for any of the required columns. Only rows with non-empty values for all three required columns are ingested to `accounts.csv`.

### Usage

```bash
python ingest_accounts.py <source_csv_path> <output_directory>
```

This will produce:
- `accounts.csv`: Rows with all required columns populated
- `accounts_rejects.csv`: Rows missing any required column value
