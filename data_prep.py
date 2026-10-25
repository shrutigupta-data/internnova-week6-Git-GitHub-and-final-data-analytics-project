"""Validate and clean the Week 6 student-performance CSV."""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = PROJECT_ROOT / "data" / "raw" / "students.csv"
CLEAN_PATH = PROJECT_ROOT / "data" / "cleaned" / "students_cleaned.csv"
TEXT_COLUMNS = ["student_id", "name", "department"]
SCORE_COLUMNS = ["english", "mathematics", "science", "computer_science"]
NUMERIC_COLUMNS = [*SCORE_COLUMNS, "attendance"]
REQUIRED_COLUMNS = [*TEXT_COLUMNS, *NUMERIC_COLUMNS]


def prepare_data() -> pd.DataFrame:
    """Apply documented validation rules and save a clean CSV."""
    data = pd.read_csv(RAW_PATH)
    print(f"Raw dataset shape: {data.shape}")
    print("Raw dataset dtypes:")
    print(data.dtypes.to_string())
    print("Raw null counts:")
    print(data.isna().sum().to_string())

    missing_columns = sorted(set(REQUIRED_COLUMNS) - set(data.columns))
    if missing_columns:
        raise ValueError(f"Required columns are missing: {', '.join(missing_columns)}")

    original_rows = len(data)
    data = data[REQUIRED_COLUMNS].copy()

    # Remove only exact duplicate rows first; conflicting repeated IDs are handled below.
    exact_duplicates = int(data.duplicated().sum())
    data = data.drop_duplicates()

    # Blank identifiers, names, or departments cannot support reliable analysis.
    for column in TEXT_COLUMNS:
        data[column] = data[column].astype("string").str.strip()
        data[column] = data[column].replace("", pd.NA)
    missing_identity_rows = int(data[TEXT_COLUMNS].isna().any(axis=1).sum())
    data = data.dropna(subset=TEXT_COLUMNS)

    # Scores and attendance are percentages. Out-of-range records are invalid, not imputable.
    for column in NUMERIC_COLUMNS:
        data[column] = pd.to_numeric(data[column], errors="coerce")
    in_range = data[NUMERIC_COLUMNS].ge(0) & data[NUMERIC_COLUMNS].le(100)
    valid_range = data[NUMERIC_COLUMNS].isna() | in_range
    invalid_range_rows = int((~valid_range.all(axis=1)).sum())
    data = data.loc[valid_range.all(axis=1)].copy()

    # Missing or non-numeric measures are filled from the department median, then the
    # cohort median if a department has no observed value for that measure.
    imputed_by_column = {}
    for column in NUMERIC_COLUMNS:
        missing_count = int(data[column].isna().sum())
        imputed_by_column[column] = missing_count
        if missing_count:
            department_medians = data.groupby("department")[column].transform("median")
            data[column] = data[column].fillna(department_medians)
            data[column] = data[column].fillna(data[column].median())

    # IDs are the record key. Keep the first valid row when a key is repeated.
    duplicate_ids = int(data["student_id"].duplicated().sum())
    data = data.drop_duplicates(subset="student_id", keep="first")
    data = data.dropna(subset=NUMERIC_COLUMNS)

    CLEAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(CLEAN_PATH, index=False)

    print(f"Input shape: ({original_rows}, {len(REQUIRED_COLUMNS)})")
    print(f"Cleaned shape: {data.shape}")
    print(f"Exact duplicate rows removed: {exact_duplicates}")
    print(f"Rows with missing identity fields removed: {missing_identity_rows}")
    print(f"Rows with out-of-range measures removed: {invalid_range_rows}")
    print(f"Repeated student IDs removed (first valid record kept): {duplicate_ids}")
    print("Missing numeric values imputed by column:")
    for column, count in imputed_by_column.items():
        print(f"  {column}: {count} (department median; cohort median fallback)")
    print("Missing-value policy for identity fields: remove the record.")
    print(f"Saved cleaned data to: {CLEAN_PATH}")
    return data


if __name__ == "__main__":
    prepare_data()