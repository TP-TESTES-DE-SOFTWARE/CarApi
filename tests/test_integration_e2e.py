import pytest

@pytest.mark.usefixtures("client")
class TestPersonCar:

    @pytest.fixture(scope="class")
    def person(self, client):
        response = client.post("/people/", json={
            "name": "Carlos Silva",
            "cpf": "12345678901",
            "birth_date": "1990-05-20"
        })
        assert response.status_code == 200
        return response.json()

    @pytest.fixture(scope="class")
    def car(self, client, person):
        response = client.post("/cars/", json={
            "make": "Toyota",
            "model": "Corolla",
            "year": 2022,
            "color": "Prata",
            "price": 90000.0,
            "owner_id": person["id"]
        })
        assert response.status_code == 200
        return response.json()

    def test_get_person(self, client, person):
        response = client.get(f"/people/{person['id']}")
        assert response.status_code == 200
        assert response.json()["name"] == "Carlos Silva"

    def test_get_car_with_owner(self, client, car, person):
        response = client.get(f"/cars/{car['id']}")
        assert response.status_code == 200
        assert response.json()["owner_id"] == person["id"]

    def test_update_person_name(self, client, person):
        response = client.put(f"/people/{person['id']}", json={"name": "Carlos M. Silva"})
        assert response.status_code == 200
        assert response.json()["name"] == "Carlos M. Silva"

    def test_update_car_price(self, client, car):
        response = client.put(f"/cars/{car['id']}", json={"price": 87000.0})
        assert response.status_code == 200
        assert response.json()["price"] == 87000.0
    
    def test_delete_person_not_found(self, client):
        response = client.delete(f"/people/{2}")
        assert response.status_code == 404
        assert response.json()["detail"] == "Person not found"