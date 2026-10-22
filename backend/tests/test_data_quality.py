import json

import pytest

from app.services.data_quality import analyze_data_quality


def test_data_quality_summary_and_missing_values():
    result = analyze_data_quality(
        "name,score\nAadesh,10\nAadesh,10\nRahul,\n"
    )

    assert result["rows"] == 3
    assert result["columns_count"] == 2
    assert result["missing_values_total"] == 1
    assert result["duplicate_rows"] == 1


def test_detects_constant_and_entirely_missing_columns():
    result = analyze_data_quality(
        "constant,empty\nsame,\nsame,\nsame,\n"
    )

    assert result["constant_columns"] == ["constant"]
    assert "empty" not in result["constant_columns"]


def test_detects_high_cardinality_using_threshold():
    result = analyze_data_quality(
        "id,group\n1,A\n2,A\n3,B\n4,B\n",
        high_cardinality_threshold=0.9,
    )

    assert any(
        item["column"] == "id"
        for item in result["high_cardinality_columns"]
    )
    assert not any(
        item["column"] == "group"
        for item in result["high_cardinality_columns"]
    )


def test_detects_mixed_numeric_and_text_values():
    result = analyze_data_quality(
        "mixed,description\n10,hello\nunknown,world\n20,123\n"
    )

    assert "mixed" in result["mixed_type_columns"]
    assert "description" not in result["mixed_type_columns"]


def test_header_only_csv_is_supported():
    result = analyze_data_quality("name,score")

    assert result["rows"] == 0
    assert result["columns_count"] == 2
    assert result["missing_values_total"] == 0


def test_empty_csv_is_rejected():
    with pytest.raises(ValueError, match="cannot be empty"):
        analyze_data_quality("")


def test_malformed_csv_is_rejected():
    with pytest.raises(ValueError, match="invalid or inconsistent"):
        analyze_data_quality('name,age\n"Aadesh,20\nRahul,21')


def test_invalid_threshold_is_rejected():
    with pytest.raises(ValueError, match="threshold"):
        analyze_data_quality("score\n10\n20", 0)


def test_result_is_json_serializable():
    result = analyze_data_quality("score,note\n10,hello\n20,world\n")
    serialized = json.dumps(result, allow_nan=False)

    assert serialized
