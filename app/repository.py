from typing import Optional
from sqlalchemy.orm import Session
from app import models, schemas

def get_car(db: Session, car_id: int):
    return db.query(models.Car).filter(models.Car.id == car_id).first()

def get_cars(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Car).offset(skip).limit(limit).all()

def create_car(db: Session, car: schemas.CarCreate):
    db_car = models.Car(**car.dict())
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    return db_car

def update_car(db: Session, car_id: int, car: schemas.CarUpdate):
    db_car = db.query(models.Car).filter(models.Car.id == car_id).first()
    if not db_car:
        return None
    
    update_data = car.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_car, key, value)
    
    db.commit()
    db.refresh(db_car)
    return db_car

def delete_car(db: Session, car_id: int):
    db_car = db.query(models.Car).filter(models.Car.id == car_id).first()
    if not db_car:
        return False
    
    db.delete(db_car)
    db.commit()
    return True

def create_person(db: Session, person: schemas.PersonCreate):
    db_person = models.Person(**person.dict())
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person

def get_person(db: Session, person_id: int):
    return db.query(models.Person).filter(models.Person.id == person_id).first()

def get_person_by_cpf(db: Session, cpf: str):
    return db.query(models.Person).filter(models.Person.cpf == cpf).first()

def get_people(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Person).offset(skip).limit(limit).all()

def update_person(db: Session, person_id: int, person: schemas.PersonUpdate):
    db_person = db.query(models.Person).filter(models.Person.id == person_id).first()
    if not db_person:
        return None
    
    update_data = person.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_person, key, value)
    
    db.commit()
    db.refresh(db_person)
    return db_person

def delete_person(db: Session, person_id: int):
    db_person = db.query(models.Person).filter(models.Person.id == person_id).first()
    if not db_person:
        return False
    
    db.delete(db_person)
    db.commit()
    return True

def get_person_with_cars(db: Session, person_id: int):
    return db.query(models.Person).filter(models.Person.id == person_id).first()

def get_car_with_owner(db: Session, car_id: int):
    return db.query(models.Car).filter(models.Car.id == car_id).first()

def associate_car_to_person(db: Session, person_id: int, car_id: int):
    """Associa um carro existente a uma pessoa"""
    db_person = db.query(models.Person).filter(models.Person.id == person_id).first()
    db_car = db.query(models.Car).filter(models.Car.id == car_id).first()
    
    if not db_person or not db_car:
        return False
    
    db_car.owner_id = person_id
    db.commit()
    db.refresh(db_car)
    return True

def disassociate_car_from_person(db: Session, car_id: int):
    """Remove a associação de um carro com seu proprietário"""
    db_car = db.query(models.Car).filter(models.Car.id == car_id).first()
    if not db_car:
        return False
    
    db_car.owner_id = None
    db.commit()
    db.refresh(db_car)
    return True

def get_person_cars(db: Session, person_id: int):
    """Retorna todos os carros de uma pessoa"""
    return db.query(models.Car).filter(models.Car.owner_id == person_id).all()

def update_car_owner(db: Session, car_id: int, owner_id: Optional[int]):
    """Atualiza o proprietário de um carro"""
    db_car = db.query(models.Car).filter(models.Car.id == car_id).first()
    if not db_car:
        return None
    
    if owner_id is not None:
        db_person = db.query(models.Person).filter(models.Person.id == owner_id).first()
        if not db_person:
            return None
    
    db_car.owner_id = owner_id
    db.commit()
    db.refresh(db_car)
    return db_car