import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_app_metadata():
    assert app.title == "Car API"
    assert app.description == "A simple Car API to exercise UnitTests"
    assert app.version == "0.1.0"


def test_openapi_schema():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "Car API"
    assert schema["info"]["version"] == "0.1.0"

def test_docs_ui_available():
    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_health_of_app():
    """
    Simula uma verificação básica de 'liveness'. 
    Útil quando não há rota /health específica.
    """
    response = client.get("/")
    assert response.status_code in [200, 404]
