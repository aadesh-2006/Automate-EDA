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