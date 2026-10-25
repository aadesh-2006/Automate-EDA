import json

import pytest

from app.services.insights import build_insights_evidence


def test_builds_dataset_summary_and_numeric_evidence():
    result = build_insights_evidence(
        "age,salary\n20,30000\n30,50000\n40,60000\n"
    )

    assert result["dataset"]["rows"] == 3
    assert result["dataset"]["columns_count"] == 2
    assert result["dataset"]["column_names"] == ["age", "salary"]
    assert "age" in result["dataset"]["numeric_summary"]


def test_detects_missing_values_and_duplicates():
    result = build_insights_evidence(
        "name,score\nAadesh,10\nAadesh,10\nRahul,\n"
    )

    findings = {item["type"]: item for item in result["findings"]}

    assert findings["missing_values"]["evidence"]["count"] == 1
    assert findings["duplicate_rows"]["evidence"]["count"] == 1


def test_detects_constant_high_cardinality_and_mixed_type_columns():
    result = build_insights_evidence(
        "constant,id,mixed\nsame,1,10\nsame,2,unknown\nsame,3,20\n"
    )

    findings = {item["type"]: item for item in result["findings"]}

    assert findings["constant_columns"]["evidence"]["columns"] == ["constant"]
    assert any(
        item["column"] == "id"
        for item in findings["high_cardinality"]["evidence"]["columns"]
    )
    assert "mixed" in findings["mixed_types"]["evidence"]["columns"]


def test_clean_dataset_has_no_findings():
    result = build_insights_evidence(
        "a,b,c\n0,0,0\n0,0,1\n0,1,0\n0,1,1\n1,0,0\n1,0,1\n1,1,0\n1,1,1\n"
    )

    assert result["findings"] == []


def test_evidence_is_json_serializable_without_nonstandard_numbers():
    result = build_insights_evidence("score,note\n10,hello\n20,world\n")

    assert json.dumps(result, allow_nan=False)


@pytest.mark.parametrize("csv_content", ["", "   "])
def test_empty_csv_is_rejected(csv_content):
    with pytest.raises(ValueError, match="cannot be empty"):
        build_insights_evidence(csv_content)


import asyncio
import json

from app.services import insights as insights_service


def test_generate_dataset_insights_returns_grounded_evidence_and_text(monkeypatch):
    captured = {}

    async def mock_generate_chat_completion(system_prompt, user_prompt):
        captured["system_prompt"] = system_prompt
        captured["user_prompt"] = user_prompt
        return "## Dataset overview\nTwo rows and two columns."

    monkeypatch.setattr(
        insights_service,
        "generate_chat_completion",
        mock_generate_chat_completion,
    )

    result = asyncio.run(
        insights_service.generate_dataset_insights(
            "score,note\n10,hello\n20,world\n"
        )
    )

    evidence_json = captured["user_prompt"].split("Evidence JSON:", 1)[1].strip()
    evidence = json.loads(evidence_json)

    assert evidence["dataset"]["rows"] == 2
    assert evidence["dataset"]["column_names"] == ["score", "note"]
    assert "Do not invent statistics" in captured["system_prompt"]
    assert result["dataset"]["rows"] == 2
    assert isinstance(result["findings"], list)
    assert "Two rows and two columns." in result["insights"]


def test_generate_dataset_insights_rejects_empty_csv_without_calling_llm(monkeypatch):
    async def unexpected_call(**kwargs):
        raise AssertionError("LLM should not be called for invalid CSV")

    monkeypatch.setattr(
        insights_service,
        "generate_chat_completion",
        unexpected_call,
    )

    with pytest.raises(ValueError, match="cannot be empty"):
        asyncio.run(insights_service.generate_dataset_insights(""))

