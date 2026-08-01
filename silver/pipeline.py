import sys
from pathlib import Path
import bronze.ingest_accounts
import silver.normalise
import silver.quality


def run_pipeline(source_csv, working_dir):
    """
    Run the three-stage ETL pipeline: bronze ingest -> silver normalise -> silver quality check.

    Args:
        source_csv: Path to source accounts CSV file
        working_dir: Working directory for pipeline output staging

    Prints:
        Counts from each stage
    """
    working_path = Path(working_dir)

    # Stage 1: Bronze ingest
    print("Stage 1: Bronze Ingest")
    bronze_dir = working_path / 'bronze'
    ingest_result = bronze.ingest_accounts.ingest(source_csv, str(bronze_dir))
    print(f"  Ingested: {ingest_result['ingested']}")
    print(f"  Rejected: {ingest_result['rejected']}")

    # Stage 2: Silver normalise
    print("Stage 2: Silver Normalise")
    bronze_csv = bronze_dir / 'accounts.csv'
    silver_dir = working_path / 'silver'
    normalise_result = silver.normalise.normalise(str(bronze_csv), str(silver_dir))
    print(f"  Normalised: {normalise_result['normalised']}")
    print(f"  Dropped: {normalise_result['dropped']}")

    # Stage 3: Silver quality check
    print("Stage 3: Silver Quality Check")
    silver_csv = silver_dir / 'accounts.csv'
    quality_result = silver.quality.check(str(silver_csv))
    print(f"  Rows: {quality_result['rows']}")
    print(f"  Blank Id: {quality_result['blank_id']}")
    print(f"  Blank Name: {quality_result['blank_name']}")
    print(f"  Duplicate Id: {quality_result['duplicate_id']}")
    print(f"  Status: {'PASS' if quality_result['ok'] else 'FAIL'}")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python -m silver.pipeline <source_csv> <working_dir>")
        sys.exit(1)

    source_csv = sys.argv[1]
    working_dir = sys.argv[2]

    run_pipeline(source_csv, working_dir)
