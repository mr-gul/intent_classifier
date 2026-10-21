from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "Intent Classification API is running"


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_predict_password_reset():
    response = client.post(
        "/predict",
        json={"text": "I forgot my password"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["text"] == "I forgot my password"
    assert data["intent"] == "password_reset"
    assert 0 <= data["confidence"] <= 1


def test_predict_subscription():
    response = client.post(
        "/predict",
        json={"text": "I want information about my subscription"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["intent"] == "subscription_information"
    assert 0 <= data["confidence"] <= 1