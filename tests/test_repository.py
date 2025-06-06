import pytest
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import repository, models, schemas
from unittest.mock import patch, MagicMock



@pytest.fixture(scope="function")
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    models.Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def car_data():
    return {
        "model": "Fiat",
        "make": "Uno",
        "year": 2020,
        "color": "Red",
        "price": 30000.0,
        "owner_id": None
    }

@pytest.fixture
def car_update_data():
    return {"model": "Ford"}

@pytest.fixture
def person_data():
    return {
        "name": "Pedro",
        "cpf": "12345678900",
        "birth_date": datetime.date(1990, 1, 1)
    }

@pytest.fixture
def person_update_data():
    return {"name": "Joao"}

def test_create_car(db, car_data):
    car_schema = schemas.CarCreate(**car_data)
    car = repository.create_car(db, car_schema)
    # Compare all fields
    for key, value in car_data.items():
        assert getattr(car, key) == value

def test_get_car(db, car_data):
    car_schema = schemas.CarCreate(**car_data)
    created = repository.create_car(db, car_schema)
    fetched = repository.get_car(db, created.id)
    assert fetched.id == created.id

def test_update_car_success(db, car_data, car_update_data):
    car_schema = schemas.CarCreate(**car_data)
    created = repository.create_car(db, car_schema)
    update_schema = schemas.CarUpdate(**car_update_data)
    updated = repository.update_car(db, created.id, update_schema)
    assert updated.model == "Ford"

def test_update_car_not_found(db, car_update_data):
    update_schema = schemas.CarUpdate(**car_update_data)
    result = repository.update_car(db, 999, update_schema)
    assert result is None

def test_delete_car_success(db, car_data):
    car_schema = schemas.CarCreate(**car_data)
    created = repository.create_car(db, car_schema)
    result = repository.delete_car(db, created.id)
    assert result is True
    assert repository.get_car(db, created.id) is None

def test_delete_car_not_found(db):
    result = repository.delete_car(db, 999)
    assert result is False

def test_create_person(db, person_data):
    person_schema = schemas.PersonCreate(**person_data)
    person = repository.create_person(db, person_schema)
    for key, value in person_data.items():
        assert getattr(person, key) == value

def test_get_person(db, person_data):
    person_schema = schemas.PersonCreate(**person_data)
    created = repository.create_person(db, person_schema)
    fetched = repository.get_person(db, created.id)
    assert fetched.id == created.id

def test_associate_car_to_person_success(db, car_data, person_data):
    person_schema = schemas.PersonCreate(**person_data)
    person = repository.create_person(db, person_schema)
    car_schema = schemas.CarCreate(**car_data)
    car = repository.create_car(db, car_schema)
    result = repository.associate_car_to_person(db, person.id, car.id)
    assert result is True
    updated_car = repository.get_car(db, car.id)
    assert updated_car.owner_id == person.id

def test_associate_car_to_person_fail(db):
    result = repository.associate_car_to_person(db, 1, 2)
    assert result is False
    
def test_get_cars(db, car_data):
    repository.create_car(db, schemas.CarCreate(**car_data))
    cars = repository.get_cars(db)
    assert len(cars) == 1
    assert cars[0].model == car_data["model"]

def test_get_car_with_owner(db, car_data):
    car = repository.create_car(db, schemas.CarCreate(**car_data))
    result = repository.get_car_with_owner(db, car.id)
    assert result.id == car.id

def test_get_person_by_cpf(db, person_data):
    person = repository.create_person(db, schemas.PersonCreate(**person_data))
    fetched = repository.get_person_by_cpf(db, person.cpf)
    assert fetched.id == person.id

def test_get_people(db, person_data):
    repository.create_person(db, schemas.PersonCreate(**person_data))
    people = repository.get_people(db)
    assert len(people) == 1
    assert people[0].cpf == person_data["cpf"]

def test_update_person_success(db, person_data, person_update_data):
    person = repository.create_person(db, schemas.PersonCreate(**person_data))
    update_schema = schemas.PersonUpdate(**person_update_data)
    updated = repository.update_person(db, person.id, update_schema)
    assert updated.name == "Joao"

def test_update_person_not_found(db, person_update_data):
    update_schema = schemas.PersonUpdate(**person_update_data)
    result = repository.update_person(db, 999, update_schema)
    assert result is None

def test_delete_person_success(db, person_data):
    person = repository.create_person(db, schemas.PersonCreate(**person_data))
    result = repository.delete_person(db, person.id)
    assert result is True
    assert repository.get_person(db, person.id) is None

def test_delete_person_not_found(db):
    result = repository.delete_person(db, 999)
    assert result is False

def test_get_person_with_cars(db, person_data):
    person = repository.create_person(db, schemas.PersonCreate(**person_data))
    result = repository.get_person_with_cars(db, person.id)
    assert result.id == person.id

def test_disassociate_car_from_person(db, car_data):
    car = repository.create_car(db, schemas.CarCreate(**car_data))
    car.owner_id = 1  # simulate ownership
    db.commit()
    result = repository.disassociate_car_from_person(db, car.id)
    assert result is True
    updated = repository.get_car(db, car.id)
    assert updated.owner_id is None

def test_get_person_cars(db, person_data, car_data):
    person = repository.create_person(db, schemas.PersonCreate(**person_data))
    car_data["owner_id"] = person.id
    repository.create_car(db, schemas.CarCreate(**car_data))
    cars = repository.get_person_cars(db, person.id)
    assert len(cars) == 1
    assert cars[0].owner_id == person.id

def test_update_car_owner_success(db, person_data, car_data):
    person = repository.create_person(db, schemas.PersonCreate(**person_data))
    car = repository.create_car(db, schemas.CarCreate(**car_data))
    updated = repository.update_car_owner(db, car.id, person.id)
    assert updated.owner_id == person.id

def test_update_car_owner_invalid_car(db, person_data):
    person = repository.create_person(db, schemas.PersonCreate(**person_data))
    result = repository.update_car_owner(db, 999, person.id)
    assert result is None

def test_update_car_owner_invalid_person(db, car_data):
    car = repository.create_car(db, schemas.CarCreate(**car_data))
    result = repository.update_car_owner(db, car.id, 999)
    assert result is None

def test_update_car_owner_remove_owner(db, car_data):
    car = repository.create_car(db, schemas.CarCreate(**car_data))
    updated = repository.update_car_owner(db, car.id, None)
    assert updated.owner_id is None


def test_update_car_owner_invalid_person(db, car_data):
    car = repository.create_car(db, schemas.CarCreate(**car_data))
    result = repository.update_car_owner(db, car.id, owner_id=999)  # Pessoa inexistente
    assert result is None


def test_get_person_cars(db, person_data, car_data):
    person = repository.create_person(db, schemas.PersonCreate(**person_data))
    car_data["owner_id"] = person.id
    car = repository.create_car(db, schemas.CarCreate(**car_data))

    cars = repository.get_person_cars(db, person.id)
    assert len(cars) == 1
    assert cars[0].id == car.id
    assert cars[0].owner_id == person.id


def test_disassociate_car_from_person_returns_when_car_not_found():
    db = MagicMock()
    db.query().filter().first.return_value = None  # Simula carro inexistente
    result = repository.disassociate_car_from_person(db, car_id=999)
    assert result is False