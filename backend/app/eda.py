
from io import StringIO

import pandas as pd


def profile_csv(csv_content: str) -> dict:
    """Generate a deterministic exploratory profile of CSV data."""
    if not csv_content or not csv_content.strip():
        raise ValueError("CSV content cannot be empty.")

    try:
        df = pd.read_csv(StringIO(csv_content))
    except pd.errors.EmptyDataError as exc:
        raise ValueError("The uploaded CSV contains no data.") from exc
    except pd.errors.ParserError as exc:
        raise ValueError("The CSV format is invalid or inconsistent.") from exc

    if df.empty and len(df.columns) == 0:
        raise ValueError("The CSV must contain column headers.")

    missing = df.isna().sum()
    duplicate_rows = int(df.duplicated().sum())

    columns = []
    for column in df.columns:
        series = df[column]
        columns.append(
            {
                "name": str(column),
                "dtype": str(series.dtype),
                "missing_values": int(series.isna().sum()),
                "missing_percentage": (
    round(float(series.isna().mean() * 100), 2)
    if len(df) > 0
    else 0.0
),
                "unique_values": int(series.nunique()),
            }
        )

    numeric_df = df.select_dtypes(include="number")
    numeric_summary = (
    numeric_df.describe().round(3).to_dict()
    if not numeric_df.empty
    else {}
)

    return {
        "rows": int(df.shape[0]),
        "columns_count": int(df.shape[1]),
        "column_names": [str(column) for column in df.columns],
        "columns": columns,
        "missing_values_total": int(missing.sum()),
        "duplicate_rows": duplicate_rows,
        "numeric_summary": numeric_summary,
    }
