
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
        axis.boxplot(series, orientation="vertical")
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

def create_correlation_heatmap(csv_content: str) -> bytes:
    """Generate a PNG correlation heatmap for numeric CSV columns."""
    if not csv_content or not csv_content.strip():
        raise ValueError("CSV content cannot be empty.")

    try:
        df = pd.read_csv(BytesIO(csv_content.encode("utf-8")))
    except pd.errors.EmptyDataError as exc:
        raise ValueError("The uploaded CSV contains no data.") from exc
    except pd.errors.ParserError as exc:
        raise ValueError("The CSV format is invalid or inconsistent.") from exc

    numeric_df = df.apply(pd.to_numeric, errors="coerce")
    numeric_df = numeric_df.dropna(axis=1, how="all")

    if numeric_df.empty or numeric_df.shape[1] < 2:
        raise ValueError(
            "At least two columns with numeric values are required."
        )

    correlation = numeric_df.corr()

    figure, axis = plt.subplots(figsize=(8, 6))
    try:
        image = axis.imshow(
            correlation.to_numpy(),
            cmap="coolwarm",
            vmin=-1,
            vmax=1,
            aspect="auto",
        )

        axis.set_xticks(range(len(correlation.columns)))
        axis.set_xticklabels(
            correlation.columns, rotation=45, ha="right"
        )
        axis.set_yticks(range(len(correlation.columns)))
        axis.set_yticklabels(correlation.columns)

        for row in range(len(correlation.columns)):
            for col in range(len(correlation.columns)):
                value = correlation.iloc[row, col]
                label = "N/A" if pd.isna(value) else f"{value:.2f}"
                axis.text(col, row, label, ha="center", va="center")

        axis.set_title("Correlation Heatmap")
        figure.colorbar(image, ax=axis, label="Correlation")
        figure.tight_layout()

        image_buffer = BytesIO()
        figure.savefig(image_buffer, format="png", dpi=120)
        return image_buffer.getvalue()
    finally:
        plt.close(figure)

