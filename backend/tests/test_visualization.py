
import io

import matplotlib.image as mpimg
import pytest

from app.services.visualization import create_histogram


def test_create_histogram_returns_png_bytes():
    csv_content = "age,salary\n20,25000\n25,40000\n30,55000\n35,65000"

    result = create_histogram(csv_content, "age")

    assert isinstance(result, bytes)
    assert result.startswith(b"\x89PNG\r\n\x1a\n")

    image = mpimg.imread(io.BytesIO(result), format="png")
    assert image.size > 0


def test_create_histogram_ignores_non_numeric_values():
    csv_content = "score\n10\n20\ninvalid\n30"

    result = create_histogram(csv_content, "score")

    assert result.startswith(b"\x89PNG\r\n\x1a\n")


def test_create_histogram_rejects_missing_column():
    with pytest.raises(ValueError, match="was not found"):
        create_histogram("age\n20\n30", "salary")


def test_create_histogram_rejects_non_numeric_column():
    with pytest.raises(ValueError, match="no numeric values"):
        create_histogram("name\nAadesh\nRahul", "name")


def test_create_histogram_rejects_empty_csv():
    with pytest.raises(ValueError, match="cannot be empty"):
        create_histogram("", "age")


from app.services.visualization import create_box_plot, detect_outliers


def test_create_box_plot_returns_png_bytes():
    result = create_box_plot("score\n10\n20\n30\n40\n100", "score")

    assert isinstance(result, bytes)
    assert result.startswith(b"\x89PNG\r\n\x1a\n")


def test_detect_outliers_identifies_extreme_value():
    result = detect_outliers("score\n10\n11\n12\n13\n14\n100", "score")

    assert result["column"] == "score"
    assert result["method"] == "1.5xIQR"
    assert result["outlier_count"] == 1
    assert result["outlier_values"] == [100]


def test_detect_outliers_returns_zero_for_no_outliers():
    result = detect_outliers("score\n10\n11\n12\n13\n14", "score")

    assert result["outlier_count"] == 0
    assert result["outlier_values"] == []


def test_detect_outliers_rejects_missing_column():
    import pytest

    with pytest.raises(ValueError, match="was not found"):
        detect_outliers("age\n20\n30", "salary")
