import pytest

from app.eda import profile_csv


def test_profile_basic_csv():
    csv_content = "name,age\nAadesh,20\nRahul,21"

    result = profile_csv(csv_content)

    assert result["rows"] == 2
    assert result["columns_count"] == 2
    assert result["column_names"] == ["name", "age"]
    assert result["missing_values_total"] == 0
    assert result["duplicate_rows"] == 0
    assert "age" in result["numeric_summary"]


def test_profile_missing_values_and_duplicates():
    csv_content = "name,age\nAadesh,20\nAadesh,20\nRahul,"

    result = profile_csv(csv_content)

    assert result["rows"] == 3
    assert result["missing_values_total"] == 1
    assert result["duplicate_rows"] == 1

    age_column = next(
        column for column in result["columns"]
        if column["name"] == "age"
    )
    assert age_column["missing_values"] == 1


def test_profile_header_only_csv():
    result = profile_csv("name,age")

    assert result["rows"] == 0
    assert result["columns_count"] == 2
    assert result["numeric_summary"] == {}

    for column in result["columns"]:
        assert column["missing_percentage"] == 0.0


def test_profile_empty_csv_raises_error():
    with pytest.raises(ValueError, match="cannot be empty"):
        profile_csv("")


def test_profile_whitespace_csv_raises_error():
    with pytest.raises(ValueError, match="cannot be empty"):
        profile_csv("   ")