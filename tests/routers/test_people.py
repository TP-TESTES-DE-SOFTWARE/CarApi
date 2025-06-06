import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import date
from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_person_data():
    return {
        "id": 1,
        "name": "Ana",
        "cpf": "12345678900",
        "birth_date": str(date(1990, 5, 17))
    }

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

@patch("app.routers.people.repository.get_person_by_cpf")
@patch("app.routers.people.repository.create_person")
def test_create_person(mock_create_person, mock_get_person_by_cpf, mock_person_data):
    mock_get_person_by_cpf.return_value = None
    mock_create_person.return_value = mock_person_data

    payload = mock_person_data.copy()
    del payload["id"]
    response = client.post("/people/", json=payload)
    assert response.status_code == 200
    assert response.json()["cpf"] == "12345678900"

@patch("app.routers.people.repository.get_person_by_cpf")
def test_create_person_with_existing_cpf(mock_get_person_by_cpf, mock_person_data):
    mock_get_person_by_cpf.return_value = mock_person_data
    payload = mock_person_data.copy()
    del payload["id"]
    response = client.post("/people/", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "CPF already registered"

@patch("app.routers.people.repository.get_people")
def test_read_people(mock_get_people, mock_person_data):
    mock_get_people.return_value = [mock_person_data]
    response = client.get("/people/")
    assert response.status_code == 200
    assert len(response.json()) == 1

@patch("app.routers.people.repository.get_person_with_cars")
def test_read_person_found(mock_get_person_with_cars, mock_person_data, mock_car_data):
    mock_get_person_with_cars.return_value = {**mock_person_data, "cars": [mock_car_data]}
    response = client.get("/people/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Ana"

@patch("app.routers.people.repository.get_person_with_cars")
def test_read_person_not_found(mock_get_person_with_cars):
    mock_get_person_with_cars.return_value = None
    response = client.get("/people/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Person not found"

@patch("app.routers.people.repository.update_person")
def test_update_person_success(mock_update_person, mock_person_data):
    mock_update_person.return_value = mock_person_data
    payload = mock_person_data.copy()
    del payload["id"]
    response = client.put("/people/1", json=payload)
    assert response.status_code == 200

@patch("app.routers.people.repository.update_person")
def test_update_person_not_found(mock_update_person, mock_person_data):
    mock_update_person.return_value = None
    payload = mock_person_data.copy()
    del payload["id"]
    response = client.put("/people/999", json=payload)
    assert response.status_code == 404

@patch("app.routers.people.repository.delete_person")
def test_delete_person_success(mock_delete_person):
    mock_delete_person.return_value = True
    response = client.delete("/people/1")
    assert response.status_code == 200
    assert response.json()["message"] == "Person deleted successfully"

@patch("app.routers.people.repository.delete_person")
def test_delete_person_not_found(mock_delete_person):
    mock_delete_person.return_value = False
    response = client.delete("/people/999")
    assert response.status_code == 404

@patch("app.routers.people.repository.get_person_with_cars")
@patch("app.routers.people.repository.disassociate_car_from_person")
@patch("app.routers.people.repository.get_car")
@patch("app.routers.people.repository.get_person")
def test_remove_car_from_person_success(mock_get_person, mock_get_car, mock_disassociate, mock_get_person_with_cars, mock_person_data):
    mock_get_person.return_value = mock_person_data
    mock_car = MagicMock()
    mock_car.owner_id = 1
    mock_get_car.return_value = mock_car
    mock_disassociate.return_value = True
    mock_get_person_with_cars.return_value = {**mock_person_data, "cars": []}
    response = client.post("/people/1/cars", json={"car_id": 1, "action": "remove"})
    assert response.status_code == 200

@patch("app.routers.people.repository.get_person_with_cars")
@patch("app.routers.people.repository.associate_car_to_person")
@patch("app.routers.people.repository.get_car")
@patch("app.routers.people.repository.get_person")
def test_add_car_to_person_success(mock_get_person, mock_get_car, mock_associate, mock_get_person_with_cars, mock_person_data, mock_car_data):
    mock_get_person.return_value = mock_person_data
    mock_get_car.return_value = mock_car_data
    mock_associate.return_value = True
    mock_get_person_with_cars.return_value = {**mock_person_data, "cars": [mock_car_data]}
    response = client.post("/people/1/cars", json={"car_id": 1, "action": "add"})
    assert response.status_code == 200

@patch("app.routers.people.repository.get_car")
@patch("app.routers.people.repository.get_person")
def test_manage_car_invalid_action(mock_get_person, mock_get_car, mock_person_data, mock_car_data):
    mock_get_person.return_value = mock_person_data
    mock_get_car.return_value = mock_car_data
    response = client.post("/people/1/cars", json={"car_id": 1, "action": "INVALID"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid action"

@patch("app.routers.people.repository.get_car")
@patch("app.routers.people.repository.get_person")
def test_manage_car_remove_fail_disassociation(mock_get_person, mock_get_car, mock_person_data):
    mock_get_person.return_value = mock_person_data
    mock_car = MagicMock()
    mock_car.owner_id = 1
    mock_get_car.return_value = mock_car
    with patch("app.routers.people.repository.disassociate_car_from_person", return_value=False):
        response = client.post("/people/1/cars", json={"car_id": 1, "action": "remove"})
        assert response.status_code == 400
        assert response.json()["detail"] == "Disassociation failed"

@patch("app.routers.people.repository.get_car")
@patch("app.routers.people.repository.get_person")
def test_manage_car_remove_wrong_owner(mock_get_person, mock_get_car, mock_person_data):
    mock_get_person.return_value = mock_person_data
    mock_car = MagicMock()
    mock_car.owner_id = 999
    mock_get_car.return_value = mock_car
    response = client.post("/people/1/cars", json={"car_id": 1, "action": "remove"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Car not owned by this person"

@patch("app.routers.people.repository.get_car")
@patch("app.routers.people.repository.get_person")
def test_manage_car_association_failed(mock_get_person, mock_get_car, mock_person_data, mock_car_data):
    mock_get_person.return_value = mock_person_data
    mock_get_car.return_value = mock_car_data
    with patch("app.routers.people.repository.associate_car_to_person", return_value=False):
        response = client.post("/people/1/cars", json={"car_id": 1, "action": "add"})
        assert response.status_code == 400
        assert response.json()["detail"] == "Association failed"

@patch("app.routers.people.repository.get_car")
def test_manage_car_person_not_found(mock_get_car):
    mock_get_car.return_value = {}
    with patch("app.routers.people.repository.get_person", return_value=None):
        response = client.post("/people/1/cars", json={"car_id": 1, "action": "add"})
        assert response.status_code == 404
        assert response.json()["detail"] == "Person not found"

@patch("app.routers.people.repository.get_person")
def test_manage_car_car_not_found(mock_get_person, mock_person_data):
    mock_get_person.return_value = mock_person_data
    with patch("app.routers.people.repository.get_car", return_value=None):
        response = client.post("/people/1/cars", json={"car_id": 999, "action": "add"})
        assert response.status_code == 404
        assert response.json()["detail"] == "Car not found"
