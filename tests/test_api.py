import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.main import app
from utils.config import config

client = TestClient(app)


class TestAuth:
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_register(self):
        response = client.post(
            "/api/auth/register",
            json={
                "username": "testdoctor",
                "email": "test@hospital.com",
                "password": "testpass123",
                "full_name": "Dr. Test",
            },
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert "access_token" in data

    def test_login_success(self):
        response = client.post(
            "/api/auth/login",
            json={"username": "testdoctor", "password": "testpass123"},
        )
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_login_failure(self):
        response = client.post(
            "/api/auth/login",
            json={"username": "testdoctor", "password": "wrongpass"},
        )
        assert response.status_code == 401


class TestPredictions:
    def test_predict_invalid_file(self):
        response = client.post(
            "/api/predictions/upload-predict",
            files={"file": ("test.txt", b"not an image", "text/plain")},
            data={"patient_name": "Test Patient"},
        )
        assert response.status_code == 422

    def test_predict_no_auth(self):
        response = client.post(
            "/api/predictions/upload-predict",
            files={"file": ("test.png", b"fakeimage", "image/png")},
            data={"patient_name": "Test Patient"},
        )
        assert response.status_code == 401

    def test_get_history_no_auth(self):
        response = client.get("/api/predictions/history")
        assert response.status_code == 401


class TestAnalytics:
    def test_dashboard_no_auth(self):
        response = client.get("/api/analytics/dashboard")
        assert response.status_code == 401

    def test_disease_distribution_no_auth(self):
        response = client.get("/api/analytics/disease-distribution")
        assert response.status_code == 401
