from io import StringIO

import pandas as pd


def analyze_data_quality(csv_content: str, high_cardinality_threshold: float = 0.9) -> dict:
    """Analyze missingness, duplicates, constant columns, cardinality, and mixed types."""
    if not csv_content or not csv_content.strip():
        raise ValueError("CSV content cannot be empty.")

    if not 0 < high_cardinality_threshold <= 1:
        raise ValueError("High-cardinality threshold must be greater than 0 and at most 1.")

    try:
        df = pd.read_csv(StringIO(csv_content))
    except pd.errors.EmptyDataError as exc:
        raise ValueError("The uploaded CSV contains no data.") from exc
    except pd.errors.ParserError as exc:
        raise ValueError("The CSV format is invalid or inconsistent.") from exc

    if len(df.columns) == 0:
        raise ValueError("The CSV must contain column headers.")

    constant_columns = []
    high_cardinality_columns = []
    mixed_type_columns = []
    column_details = []

    for column in df.columns:
        series = df[column]
        non_missing = series.dropna()
        non_missing_count = len(non_missing)
        unique_count = int(non_missing.nunique())
        ratio = (
            float(unique_count / non_missing_count)
            if non_missing_count
            else 0.0
        )
        name = str(column)

        if non_missing_count > 0 and unique_count == 1:
            constant_columns.append(name)

        if non_missing_count >= 2 and ratio >= high_cardinality_threshold:
            high_cardinality_columns.append({
                "column": name,
                "unique_values": unique_count,
                "non_missing_values": non_missing_count,
                "unique_ratio": round(ratio, 4),
            })

        if pd.api.types.is_object_dtype(series.dtype) or pd.api.types.is_string_dtype(series.dtype):
            text_values = non_missing.astype(str).str.strip()
            text_values = text_values[text_values != ""]
            numeric_mask = pd.to_numeric(text_values, errors="coerce").notna()

            # Avoid flagging ordinary text columns just because a value
            # happens to look numeric (for example, a description like "123").
            if numeric_mask.any() and (~numeric_mask).any():
                numeric_values = text_values[numeric_mask]
                non_numeric_values = text_values[~numeric_mask]
                if len(numeric_values) >= 2 and len(non_numeric_values) >= 1:
                    mixed_type_columns.append(name)

        column_details.append({
            "column": name,
            "missing_values": int(series.isna().sum()),
            "missing_percentage": (
                round(float(series.isna().mean() * 100), 2)
                if len(df)
                else 0.0
            ),
            "unique_values": unique_count,
            "unique_ratio": round(ratio, 4),
        })

    return {
        "rows": int(df.shape[0]),
        "columns_count": int(df.shape[1]),
        "missing_values_total": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "constant_columns": constant_columns,
        "high_cardinality_columns": high_cardinality_columns,
        "mixed_type_columns": mixed_type_columns,
        "columns": column_details,
        "high_cardinality_threshold": high_cardinality_threshold,
    }
