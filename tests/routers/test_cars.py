import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import date
from app.main import app

client = TestClient(app)


@pytest.fixture
def mock_car_data():
    return {
        "id": 1,
        "make": "Toyota",
        "model": "Corolla",
        "year": 2020,
        "color": "White",
        "price": 70000.0,
        "owner_id": 1
    }

@pytest.fixture
def mock_person_data():
    return {
        "id": 1,
        "name": "Ana",
        "cpf": "12345678900",
        "birth_date": date(1990, 5, 17)
    }


@patch("app.routers.cars.repository.get_person")
@patch("app.routers.cars.repository.create_car")
def test_create_car(mock_create_car, mock_get_person, mock_car_data, mock_person_data):
    mock_get_person.return_value = mock_person_data
    mock_create_car.return_value = mock_car_data

    payload = mock_car_data.copy()
    del payload["id"]

    response = client.post("/cars/", json=payload)
    assert response.status_code == 200
    assert response.json()["model"] == "Corolla"


@patch("app.routers.cars.repository.get_person")
def test_create_car_with_invalid_owner(mock_get_person, mock_car_data):
    mock_get_person.return_value = None

    payload = mock_car_data.copy()
    del payload["id"]

    response = client.post("/cars/", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Owner not found"


@patch("app.routers.cars.repository.get_cars")
def test_read_cars(mock_get_cars, mock_car_data):
    mock_get_cars.return_value = [mock_car_data]
    response = client.get("/cars/")
    assert response.status_code == 200
    assert len(response.json()) == 1


@patch("app.routers.cars.repository.get_car_with_owner")
def test_read_car_found(mock_get_car, mock_car_data, mock_person_data):
    mock_get_car.return_value = {**mock_car_data, "owner": mock_person_data}
    response = client.get("/cars/1")
    assert response.status_code == 200
    assert response.json()["owner"]["name"] == "Ana"


@patch("app.routers.cars.repository.get_car_with_owner")
def test_read_car_not_found(mock_get_car):
    mock_get_car.return_value = None
    response = client.get("/cars/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Car not found"


@patch("app.routers.cars.repository.update_car")
@patch("app.routers.cars.repository.get_person")
def test_update_car_success(mock_get_person, mock_update_car, mock_car_data, mock_person_data):
    mock_get_person.return_value = mock_person_data
    mock_update_car.return_value = mock_car_data

    payload = mock_car_data.copy()
    del payload["id"]

    response = client.put("/cars/1", json=payload)
    assert response.status_code == 200
    assert response.json()["model"] == "Corolla"


@patch("app.routers.cars.repository.update_car")
@patch("app.routers.cars.repository.get_person")
def test_update_car_not_found(mock_get_person, mock_update_car, mock_car_data, mock_person_data):
    mock_get_person.return_value = mock_person_data
    mock_update_car.return_value = None

    payload = mock_car_data.copy()
    del payload["id"]

    response = client.put("/cars/99", json=payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "Car not found"


@patch("app.routers.cars.repository.get_person")
def test_update_car_invalid_owner(mock_get_person, mock_car_data):
    mock_get_person.return_value = None
    payload = mock_car_data.copy()
    del payload["id"]

    response = client.put("/cars/1", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Owner not found"


@patch("app.routers.cars.repository.delete_car")
def test_delete_car_success(mock_delete_car):
    mock_delete_car.return_value = True
    response = client.delete("/cars/1")
    assert response.status_code == 200
    assert response.json()["message"] == "Car deleted successfully"


@patch("app.routers.cars.repository.delete_car")
def test_delete_car_not_found(mock_delete_car):
    mock_delete_car.return_value = False
    response = client.delete("/cars/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Car not found"


@patch("app.routers.cars.repository.update_car_owner")
def test_patch_update_owner_success(mock_update_owner, mock_car_data, mock_person_data):
    mock_update_owner.return_value = {**mock_car_data, "owner": mock_person_data}
    response = client.patch("/cars/1/owner", json={"owner_id": 1})
    assert response.status_code == 200
    assert response.json()["owner"]["cpf"] == "12345678900"


@patch("app.routers.cars.repository.update_car_owner")
def test_patch_update_owner_fail(mock_update_owner):
    mock_update_owner.return_value = None
    response = client.patch("/cars/1/owner", json={"owner_id": 99})
    assert response.status_code == 404
    assert response.json()["detail"] == "Car not found or invalid owner"


@patch("app.routers.cars.repository.get_person_cars")
@patch("app.routers.cars.repository.get_person")
def test_get_cars_by_owner_success(mock_get_person, mock_get_person_cars, mock_car_data, mock_person_data):
    mock_get_person.return_value = mock_person_data
    mock_get_person_cars.return_value = [mock_car_data]

    response = client.get("/cars/owner/1")
    assert response.status_code == 200
    assert len(response.json()) == 1


@patch("app.routers.cars.repository.get_person")
def test_get_cars_by_owner_not_found(mock_get_person):
    mock_get_person.return_value = None
    response = client.get("/cars/owner/99")
    assert response.status_code == 404
    assert response.json()["detail"] == "Owner not found"
