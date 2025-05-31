import pytest
from unittest.mock import MagicMock, patch
from app import repository

@pytest.fixture
def db():
    return MagicMock()

@pytest.fixture
def car():
    car = MagicMock()
    car.dict.return_value = {"model": "Fiat", "year": 2020, "owner_id": None}
    return car

@pytest.fixture
def car_update():
    car = MagicMock()
    car.dict.return_value = {"model": "Ford"}
    car.dict.side_effect = lambda exclude_unset=False: {"model": "Ford"} if exclude_unset else {"model": "Ford"}
    return car

@pytest.fixture
def person():
    person = MagicMock()
    person.dict.return_value = {"name": "Pedro", "cpf": "12345678900"}
    return person

@pytest.fixture
def person_update():
    person = MagicMock()
    person.dict.return_value = {"name": "Joao"}
    person.dict.side_effect = lambda exclude_unset=False: {"name": "Joao"} if exclude_unset else {"name": "Joao"}
    return person

def test_create_car(db, car):
    db.add = MagicMock()
    db.commit = MagicMock()
    db.refresh = MagicMock()
    with patch("app.models.Car", autospec=True) as Car:
        Car.return_value = MagicMock()
        result = repository.create_car(db, car)
        db.add.assert_called()
        db.commit.assert_called()
        db.refresh.assert_called()
        assert result is not None

def test_get_car(db):
    db.query().filter().first.return_value = "car"
    result = repository.get_car(db, 1)
    assert result == "car"

def test_update_car_success(db, car_update):
    db_car = MagicMock()
    db.query().filter().first.return_value = db_car
    db.commit = MagicMock()
    db.refresh = MagicMock()
    result = repository.update_car(db, 1, car_update)
    db.commit.assert_called()
    db.refresh.assert_called()
    assert result == db_car

def test_update_car_not_found(db, car_update):
    db.query().filter().first.return_value = None
    result = repository.update_car(db, 1, car_update)
    assert result is None

def test_delete_car_success(db):
    db_car = MagicMock()
    db.query().filter().first.return_value = db_car
    db.delete = MagicMock()
    db.commit = MagicMock()
    result = repository.delete_car(db, 1)
    db.delete.assert_called_with(db_car)
    db.commit.assert_called()
    assert result is True

def test_delete_car_not_found(db):
    db.query().filter().first.return_value = None
    result = repository.delete_car(db, 1)
    assert result is False

def test_create_person(db, person):
    db.add = MagicMock()
    db.commit = MagicMock()
    db.refresh = MagicMock()
    with patch("app.models.Person", autospec=True) as Person:
        Person.return_value = MagicMock()
        result = repository.create_person(db, person)
        db.add.assert_called()
        db.commit.assert_called()
        db.refresh.assert_called()
        assert result is not None

def test_get_person(db):
    db.query().filter().first.return_value = "person"
    result = repository.get_person(db, 1)
    assert result == "person"

def test_associate_car_to_person_success(db):
    db_person = MagicMock()
    db_car = MagicMock()
    db.query().filter().first.side_effect = [db_person, db_car]
    db.commit = MagicMock()
    db.refresh = MagicMock()
    result = repository.associate_car_to_person(db, 1, 2)
    db.commit.assert_called()
    db.refresh.assert_called_with(db_car)
    assert result is True

def test_associate_car_to_person_fail(db):
    db.query().filter().first.side_effect = [None, None]
    result = repository.associate_car_to_person(db, 1, 2)
    assert result is False