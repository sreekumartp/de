# Bronze-to-Silver Stage

Transforms raw bronze account data into normalized silver data, then validates quality.

## normalise.py

Normalizes bronze CSV data:
- **All columns**: Strip leading/trailing whitespace
- **Id**: Convert to uppercase
- **CreatedDate**: Parse and standardize to ISO `YYYY-MM-DD` format
  - Accepts input formats: `YYYY-MM-DD`, `DD/MM/YYYY`
  - Drops rows with unparseable dates
- Outputs: `accounts.csv` in the specified directory

**Usage:**
```bash
python normalise.py <bronze_csv> <out_dir>
```

Returns counts of normalised and dropped rows.

## quality.py

Validates normalized silver data:
- **Id**: All rows must have non-empty Id (no blanks)
- **Name**: All rows must have non-empty Name (no blanks)
- **Id uniqueness**: No duplicate Id values across rows

**Usage:**
```bash
python quality.py <silver_csv>
```

Returns row count, error counts, and pass/fail status. Exits with code 1 on failure.

## Workflow

1. Run `normalise.py` on bronze CSV to produce silver data
2. Run `quality.py` on silver CSV to validate; fix any issues before proceeding
