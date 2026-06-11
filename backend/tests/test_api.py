from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "message": "Electronic Department API is running",
    }


def test_get_department_info():
    response = client.get("/api/department/info")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "description" in data
    assert data["id"] == 1


def test_mock_login_admin():
    response = client.post("/api/auth/mock-login", json={"role": "admin"})
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "admin"
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["name"] == "Адміністратор Системи"


def test_mock_login_invalid_role():
    response = client.post("/api/auth/mock-login", json={"role": "superman"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid simulator role: superman"