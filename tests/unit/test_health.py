from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_health_ok():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_metrics_exposes_requests_total():
    client.get("/health")
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "requests_total" in r.text
