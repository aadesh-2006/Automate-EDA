import json

from app.eda import profile_csv
from app.services.data_quality import analyze_data_quality
from app.services.llm_client import generate_chat_completion


def build_insights_evidence(csv_content: str) -> dict:
    """Build a deterministic evidence package for grounded AI insights."""
    profile = profile_csv(csv_content)
    quality = analyze_data_quality(csv_content)

    findings = []

    if profile["missing_values_total"] > 0:
        findings.append(
            {
                "type": "missing_values",
                "severity": "warning",
                "evidence": {
                    "count": profile["missing_values_total"],
                    "columns": [
                        {
                            "name": column["name"],
                            "count": column["missing_values"],
                            "percentage": column["missing_percentage"],
                        }
                        for column in profile["columns"]
                        if column["missing_values"] > 0
                    ],
                },
            }
        )

    if profile["duplicate_rows"] > 0:
        findings.append(
            {
                "type": "duplicate_rows",
                "severity": "warning",
                "evidence": {
                    "count": profile["duplicate_rows"],
                    "rows": profile["rows"],
                },
            }
        )

    if quality["constant_columns"]:
        findings.append(
            {
                "type": "constant_columns",
                "severity": "info",
                "evidence": {"columns": quality["constant_columns"]},
            }
        )

    if quality["high_cardinality_columns"]:
        findings.append(
            {
                "type": "high_cardinality",
                "severity": "info",
                "evidence": {"columns": quality["high_cardinality_columns"]},
            }
        )

    if quality["mixed_type_columns"]:
        findings.append(
            {
                "type": "mixed_types",
                "severity": "warning",
                "evidence": {"columns": quality["mixed_type_columns"]},
            }
        )

    return {
        "dataset": {
            "rows": profile["rows"],
            "columns_count": profile["columns_count"],
            "column_names": profile["column_names"],
            "columns": profile["columns"],
            "numeric_summary": profile["numeric_summary"],
        },
        "data_quality": {
            "missing_values_total": quality["missing_values_total"],
            "duplicate_rows": quality["duplicate_rows"],
            "constant_columns": quality["constant_columns"],
            "high_cardinality_columns": quality["high_cardinality_columns"],
            "mixed_type_columns": quality["mixed_type_columns"],
        },
        "findings": findings,
    }


INSIGHTS_SYSTEM_PROMPT = """
You are a data analyst. Return only the final report in concise Markdown.
Do not explain your reasoning or repeat these instructions.
Use exactly these headings:
## Dataset overview
## Key findings
## Recommended next steps

Use only facts present in the supplied evidence.
Mention row and column counts, missing values, and duplicate rows.
Report the listed findings. Recommend checking constant columns and reviewing
the uniqueness of Timestamp. Do not claim unsupported correlations or causes.
Keep the entire answer under 180 words.
""".strip()


async def generate_dataset_insights(csv_content: str) -> dict:
    """Generate grounded natural-language insights from deterministic evidence."""
    evidence = build_insights_evidence(csv_content)
    user_prompt = (
        "Analyze this deterministic EDA evidence and produce grounded insights.\n"
        "Do not infer facts that are not present in the evidence.\n\n"
        "Evidence JSON:\n"
        + json.dumps(evidence, ensure_ascii=False, allow_nan=False)
    )

    insights = await generate_chat_completion(
        system_prompt=INSIGHTS_SYSTEM_PROMPT,
        user_prompt=user_prompt,
    )

    return {
        "dataset": evidence["dataset"],
        "findings": evidence["findings"],
        "insights": insights,
    }


