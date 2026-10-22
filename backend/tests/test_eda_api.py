from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_profile_csv_success():
    response = client.post(
        "/api/v1/eda/profile",
        content="name,age\nAadesh,20\nRahul,21",
    )

    assert response.status_code == 200

    data = response.json()
    assert data["rows"] == 2
    assert data["columns_count"] == 2
    assert data["column_names"] == ["name", "age"]
    assert data["missing_values_total"] == 0


def test_profile_empty_csv_returns_400():
    response = client.post(
        "/api/v1/eda/profile",
        content="",
    )

    assert response.status_code == 400
    assert "cannot be empty" in response.json()["detail"]


def test_profile_whitespace_csv_returns_400():
    response = client.post(
        "/api/v1/eda/profile",
        content="   ",
    )

    assert response.status_code == 400


def test_profile_invalid_utf8_returns_400():
    response = client.post(
        "/api/v1/eda/profile",
        content=b"\xff\xfe\xfa",
    )

    assert response.status_code == 400
    assert "UTF-8" in response.json()["detail"]


def test_health_endpoint_still_works():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_histogram_endpoint_returns_png():
    response = client.post(
        "/api/v1/eda/visualizations/histogram?column=age",
        content="age,salary\n20,25000\n25,40000\n30,55000",
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content.startswith(b"\x89PNG\r\n\x1a\n")


def test_box_plot_endpoint_returns_png():
    response = client.post(
        "/api/v1/eda/visualizations/box-plot?column=age",
        content="age\n10\n20\n30\n40\n100",
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content.startswith(b"\x89PNG\r\n\x1a\n")


def test_correlation_heatmap_endpoint_returns_png():
    response = client.post(
        "/api/v1/eda/visualizations/correlation-heatmap",
        content="age,salary\n20,25000\n25,40000\n30,55000",
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content.startswith(b"\x89PNG\r\n\x1a\n")


def test_outliers_endpoint_returns_json():
    response = client.post(
        "/api/v1/eda/outliers?column=score",
        content="score\n10\n11\n12\n13\n14\n100",
    )

    assert response.status_code == 200
    data = response.json()
    assert data["column"] == "score"
    assert data["outlier_count"] == 1
    assert data["outlier_values"] == [100]


def test_histogram_endpoint_returns_400_for_missing_column():
    response = client.post(
        "/api/v1/eda/visualizations/histogram?column=salary",
        content="age\n20\n30",
    )

    assert response.status_code == 400
    assert "was not found" in response.json()["detail"]


def test_heatmap_endpoint_returns_400_for_insufficient_numeric_columns():
    response = client.post(
        "/api/v1/eda/visualizations/correlation-heatmap",
        content="age,name\n20,Aadesh\n25,Rahul",
    )

    assert response.status_code == 400
    assert "At least two columns" in response.json()["detail"]


def test_data_quality_endpoint_returns_json():
    response = client.post(
        "/api/v1/eda/data-quality",
        content="name,score\nAadesh,10\nAadesh,10\nRahul,\n",
        headers={"Content-Type": "text/csv"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["rows"] == 3
    assert data["missing_values_total"] == 1
    assert data["duplicate_rows"] == 1


def test_data_quality_endpoint_rejects_empty_csv():
    response = client.post(
        "/api/v1/eda/data-quality",
        content="",
        headers={"Content-Type": "text/csv"},
    )
    assert response.status_code == 400
    assert "cannot be empty" in response.json()["detail"]
