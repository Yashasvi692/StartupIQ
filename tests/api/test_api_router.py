from fastapi.testclient import TestClient

from backend.main import app


class TestApiRouter:
    def test_health_route_loaded(self):
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_version_route_loaded(self):
        client = TestClient(app)
        response = client.get("/version")
        assert response.status_code == 200
        data = response.json()
        assert data["project"] == "StartupIQ"

    def test_unknown_route_returns_404(self):
        client = TestClient(app)
        response = client.get("/unknown")
        assert response.status_code == 404
