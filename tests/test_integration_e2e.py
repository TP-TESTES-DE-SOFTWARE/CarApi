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
        assert response.json()["cpf"] == "12345678901"
        assert response.json()["birth_date"] == "1990-05-20"

    def test_get_car_with_owner(self, client, car, person):
        response = client.get(f"/cars/{car['id']}")
        assert response.status_code == 200
        assert response.json()["owner"]["id"] == person["id"]
        assert response.json()["make"] == "Toyota"
        assert response.json()["model"] == "Corolla"

    def test_update_person_name(self, client, person):
        response = client.put(f"/people/{person['id']}", json={"name": "Carlos M. Silva"})
        assert response.status_code == 200
        assert response.json()["name"] == "Carlos M. Silva"
        response_get = client.get(f"/people/{person['id']}")
        assert response_get.status_code == 200
        assert response_get.json()["cpf"] == "12345678901"

    def test_update_car_price(self, client, car):
        response = client.put(f"/cars/{car['id']}", json={"price": 87000.0})
        assert response.status_code == 200
        assert response.json()["price"] == 87000.0
        response_get = client.get(f"/cars/{car['id']}")
        assert response_get.status_code == 200
        assert response_get.json()["make"] == "Toyota"

    def test_delete_person_not_found(self, client):
        response = client.delete(f"/people/{9999}")
        assert response.status_code == 404
        assert response.json()["detail"] == "Person not found"

    def test_create_another_person(self, client):
        response = client.post("/people/", json={
            "name": "Maria Souza",
            "cpf": "98765432109",
            "birth_date": "1985-11-15"
        })
        assert response.status_code == 200
        assert response.json()["name"] == "Maria Souza"
        assert "id" in response.json()

    def test_create_person_duplicate_cpf(self, client, person):
        response = client.post("/people/", json={
            "name": "João Duplicado",
            "cpf": person["cpf"],
            "birth_date": "1992-03-25"
        })
        assert response.status_code == 400
        assert response.json()["detail"] == "CPF already registered"

    def test_create_car_owner_not_found(self, client):
        response = client.post("/cars/", json={
            "make": "Honda",
            "model": "Civic",
            "year": 2020,
            "color": "Branco",
            "price": 75000.0,
            "owner_id": 9999
        })
        assert response.status_code == 400
        assert response.json()["detail"] == "Owner not found"

    def test_get_non_existent_person(self, client):
        response = client.get(f"/people/{9999}")
        assert response.status_code == 404
        assert response.json()["detail"] == "Person not found"

    def test_get_non_existent_car(self, client):
        response = client.get(f"/cars/{9999}")
        assert response.status_code == 404
        assert response.json()["detail"] == "Car not found"

    def test_get_all_cars(self, client, car):
        person_for_another_car = client.post("/people/", json={
            "name": "Car Owner Two",
            "cpf": "77777777777",
            "birth_date": "1975-03-03"
        }).json()

        client.post("/cars/", json={
            "make": "Ford",
            "model": "Fiesta",
            "year": 2018,
            "color": "Azul",
            "price": 45000.0,
            "owner_id": person_for_another_car["id"]
        })
        response = client.get("/cars/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) >= 2
        car_models = [c["model"] for c in response.json()]
        assert car["model"] in car_models

    def test_update_car_with_invalid_data(self, client, car):
        response = client.put(f"/cars/{car['id']}", json={"year": "not-a-year"})
        assert response.status_code == 422
        assert "detail" in response.json()
        assert any("year" in error["loc"] for error in response.json()["detail"])

    def test_delete_car_not_found(self, client):
        response = client.delete(f"/cars/{9999}")
        assert response.status_code == 404
        assert response.json()["detail"] == "Car not found"

    def test_patch_car_owner_to_null(self, client):
        person_for_null = client.post("/people/", json={
            "name": "Person For Null",
            "cpf": "33333333333",
            "birth_date": "1970-07-07"
        }).json()
        car_to_null = client.post("/cars/", json={
            "make": "BMW",
            "model": "X5",
            "year": 2021,
            "color": "White",
            "price": 150000.0,
            "owner_id": person_for_null["id"]
        }).json()

        response = client.patch(f"/cars/{car_to_null['id']}/owner", json={"owner_id": None})
        assert response.status_code == 200
        assert response.json()["owner"] is None
        assert response.json()["id"] == car_to_null["id"]

        retrieved_car = client.get(f"/cars/{car_to_null['id']}").json()
        assert retrieved_car["owner"] is None

    def test_patch_car_owner_car_not_found(self, client):
        response = client.patch(f"/cars/{9999}/owner", json={"owner_id": 1})
        assert response.status_code == 404
        assert response.json()["detail"] == "Car not found or invalid owner"

    def test_patch_car_owner_new_owner_not_found(self, client, car):
        response = client.patch(f"/cars/{car['id']}/owner", json={"owner_id": 9999})
        assert response.status_code == 404
        assert response.json()["detail"] == "Car not found or invalid owner"

    def test_get_cars_by_owner(self, client):
        person_with_cars = client.post("/people/", json={
            "name": "Owner With Cars",
            "cpf": "44444444444",
            "birth_date": "1988-08-08"
        }).json()
        
        car1 = client.post("/cars/", json={
            "make": "VW", "model": "Golf", "year": 2015, "color": "Grey",
            "price": 60000.0, "owner_id": person_with_cars["id"]
        }).json()
        car2 = client.post("/cars/", json={
            "make": "Fiat", "model": "Uno", "year": 2010, "color": "Red",
            "price": 30000.0, "owner_id": person_with_cars["id"]
        }).json()

        response = client.get(f"/cars/owner/{person_with_cars['id']}")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) == 2
        retrieved_car_models = [c["model"] for c in response.json()]
        assert car1["model"] in retrieved_car_models
        assert car2["model"] in retrieved_car_models

    def test_get_cars_by_owner_no_cars(self, client):
        person_no_cars = client.post("/people/", json={
            "name": "Owner No Cars",
            "cpf": "55555555555",
            "birth_date": "1999-09-09"
        }).json()
        response = client.get(f"/cars/owner/{person_no_cars['id']}")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) == 0

    def test_get_cars_by_owner_not_found(self, client):
        response = client.get(f"/cars/owner/{9999}")
        assert response.status_code == 404
        assert response.json()["detail"] == "Owner not found"

    def test_person_add_car(self, client):
        person_for_add = client.post("/people/", json={
            "name": "Person For Add",
            "cpf": "66666666666",
            "birth_date": "1980-01-01"
        }).json()
        car_for_add = client.post("/cars/", json={
            "make": "Mercedes",
            "model": "C-Class",
            "year": 2023,
            "color": "Silver",
            "price": 180000.0,
            "owner_id": None
        }).json()
        
        response = client.post(f"/people/{person_for_add['id']}/cars", json={
            "car_id": car_for_add["id"],
            "action": "add"
        })
        assert response.status_code == 200
        assert response.json()["id"] == person_for_add["id"]
        assert len(response.json()["cars"]) == 1
        assert response.json()["cars"][0]["id"] == car_for_add["id"]
        
        retrieved_car = client.get(f"/cars/{car_for_add['id']}").json()
        assert retrieved_car["owner"]["id"] == person_for_add["id"]

    def test_person_add_car_person_not_found(self, client, car):
        response = client.post(f"/people/{9999}/cars", json={
            "car_id": car["id"],
            "action": "add"
        })
        assert response.status_code == 404
        assert response.json()["detail"] == "Person not found"

    def test_person_add_car_car_not_found(self, client, person):
        response = client.post(f"/people/{person['id']}/cars", json={
            "car_id": 9999,
            "action": "add"
        })
        assert response.status_code == 404
        assert response.json()["detail"] == "Car not found"

    def test_person_remove_car_car_not_found(self, client, person):
        response = client.post(f"/people/{person['id']}/cars", json={
            "car_id": 9999,
            "action": "remove"
        })
        assert response.status_code == 404
        assert response.json()["detail"] == "Car not found"

    def test_person_manage_car_invalid_action(self, client, person, car):
        response = client.post(f"/people/{person['id']}/cars", json={
            "car_id": car["id"],
            "action": "invalid_action"
        })
        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid action"