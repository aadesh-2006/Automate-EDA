from fastapi.testclient import TestClient

from app.main import app
from app.services.report import generate_html_report, generate_pdf_report

client = TestClient(app)


def test_report_contains_dataset_summary_and_columns():
    report = generate_html_report("age,salary\n20,30000\n30,50000\n")

    assert "DataLens AI" in report
    assert "Rows" in report
    assert "2" in report
    assert "age" in report
    assert "salary" in report
    assert "Numeric Summary" in report


def test_report_embeds_charts_as_base64_images():
    report = generate_html_report("age,salary\n20,30000\n30,50000\n40,60000\n")

    assert "data:image/png;base64," in report
    assert "Correlation Heatmap" in report


def test_report_escapes_html_in_column_names():
    report = generate_html_report('"<script>",value\n1,2\n3,4\n')

    assert "<script>" not in report
    assert "&lt;script&gt;" in report


def test_report_endpoint_returns_downloadable_html():
    response = client.post(
        "/api/v1/eda/report/html",
        content="age,salary\n20,30000\n30,50000\n",
        headers={"Content-Type": "text/csv"},
    )

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert 'attachment; filename="datalens-eda-report.html"' in (
        response.headers["content-disposition"]
    )
    assert "DataLens AI" in response.text


def test_report_endpoint_rejects_empty_csv():
    response = client.post(
        "/api/v1/eda/report/html",
        content="",
        headers={"Content-Type": "text/csv"},
    )

    assert response.status_code == 400


def test_pdf_report_generates_valid_pdf():
    report = generate_pdf_report(
        "age,salary\\n20,30000\\n30,50000\\n40,60000\\n"
    )

    assert report.startswith(b"%PDF-")
    assert len(report) > 1000


def test_pdf_report_supports_text_only_dataset():
    report = generate_pdf_report(
        "name,department\\nAadesh,Engineering\\nRahul,Sales\\n"
    )

    assert report.startswith(b"%PDF-")


def test_pdf_report_endpoint_returns_downloadable_pdf():
    response = client.post(
        "/api/v1/eda/report/pdf",
        content="age,salary\\n20,30000\\n30,50000\\n40,60000\\n",
        headers={"Content-Type": "text/csv"},
    )

    assert response.status_code == 200
    assert "application/pdf" in response.headers["content-type"]
    assert 'attachment; filename="datalens-eda-report.pdf"' in (
        response.headers["content-disposition"]
    )
    assert response.content.startswith(b"%PDF-")


def test_pdf_report_endpoint_rejects_empty_csv():
    response = client.post(
        "/api/v1/eda/report/pdf",
        content="",
        headers={"Content-Type": "text/csv"},
    )

    assert response.status_code == 400
