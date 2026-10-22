
from io import BytesIO

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


def create_histogram(csv_content: str, column_name: str) -> bytes:
    """Generate a PNG histogram for a numeric CSV column."""
    if not csv_content or not csv_content.strip():
        raise ValueError("CSV content cannot be empty.")

    try:
        df = pd.read_csv(BytesIO(csv_content.encode("utf-8")))
    except pd.errors.EmptyDataError as exc:
        raise ValueError("The uploaded CSV contains no data.") from exc
    except pd.errors.ParserError as exc:
        raise ValueError("The CSV format is invalid or inconsistent.") from exc

    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' was not found in the CSV.")

    series = pd.to_numeric(df[column_name], errors="coerce").dropna()

    if series.empty:
        raise ValueError(f"Column '{column_name}' has no numeric values.")

    figure, axis = plt.subplots(figsize=(8, 5))
    try:
        axis.hist(series, bins="auto", edgecolor="black")
        axis.set_title(f"Distribution of {column_name}")
        axis.set_xlabel(column_name)
        axis.set_ylabel("Frequency")
        figure.tight_layout()

        image_buffer = BytesIO()
        figure.savefig(image_buffer, format="png", dpi=120)
        return image_buffer.getvalue()
    finally:
        plt.close(figure)


def create_box_plot(csv_content: str, column_name: str) -> bytes:
    """Generate a PNG box plot for a numeric CSV column."""
    if not csv_content or not csv_content.strip():
        raise ValueError("CSV content cannot be empty.")

    try:
        df = pd.read_csv(BytesIO(csv_content.encode("utf-8")))
    except pd.errors.EmptyDataError as exc:
        raise ValueError("The uploaded CSV contains no data.") from exc
    except pd.errors.ParserError as exc:
        raise ValueError("The CSV format is invalid or inconsistent.") from exc

    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' was not found in the CSV.")

    series = pd.to_numeric(df[column_name], errors="coerce").dropna()

    if series.empty:
        raise ValueError(f"Column '{column_name}' has no numeric values.")

    figure, axis = plt.subplots(figsize=(8, 5))
    try:
        axis.boxplot(series, vert=True)
        axis.set_title(f"Box Plot of {column_name}")
        axis.set_ylabel(column_name)
        figure.tight_layout()

        image_buffer = BytesIO()
        figure.savefig(image_buffer, format="png", dpi=120)
        return image_buffer.getvalue()
    finally:
        plt.close(figure)


def detect_outliers(csv_content: str, column_name: str) -> dict:
    """Detect potential numeric outliers using the 1.5×IQR rule."""
    if not csv_content or not csv_content.strip():
        raise ValueError("CSV content cannot be empty.")

    try:
        df = pd.read_csv(BytesIO(csv_content.encode("utf-8")))
    except pd.errors.EmptyDataError as exc:
        raise ValueError("The uploaded CSV contains no data.") from exc
    except pd.errors.ParserError as exc:
        raise ValueError("The CSV format is invalid or inconsistent.") from exc

    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' was not found in the CSV.")

    series = pd.to_numeric(df[column_name], errors="coerce").dropna()

    if series.empty:
        raise ValueError(f"Column '{column_name}' has no numeric values.")

    q1 = float(series.quantile(0.25))
    q3 = float(series.quantile(0.75))
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    outliers = series[(series < lower_bound) | (series > upper_bound)]

    return {
        "column": column_name,
        "method": "1.5xIQR",
        "lower_bound": lower_bound,
        "upper_bound": upper_bound,
        "outlier_count": int(len(outliers)),
        "outlier_values": outliers.tolist(),
    }
