from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, repository
from app.database import get_db

router = APIRouter(prefix="/people", tags=["people"])

@router.post("/", response_model=schemas.Person)
def create_person(person: schemas.PersonCreate, db: Session = Depends(get_db)):
    db_person = repository.get_person_by_cpf(db, cpf=person.cpf)
    if db_person:
        raise HTTPException(status_code=400, detail="CPF already registered")
    return repository.create_person(db=db, person=person)

@router.get("/", response_model=list[schemas.Person])
def read_people(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    people = repository.get_people(db, skip=skip, limit=limit)
    return people

@router.get("/{person_id}", response_model=schemas.PersonWithCars)
def read_person(person_id: int, db: Session = Depends(get_db)):
    db_person = repository.get_person_with_cars(db, person_id=person_id)
    if db_person is None:
        raise HTTPException(status_code=404, detail="Person not found")
    return db_person

@router.put("/{person_id}", response_model=schemas.Person)
def update_person(
    person_id: int, person: schemas.PersonUpdate, db: Session = Depends(get_db)
):
    db_person = repository.update_person(db=db, person_id=person_id, person=person)
    if db_person is None:
        raise HTTPException(status_code=404, detail="Person not found")
    return db_person

@router.delete("/{person_id}")
def delete_person(person_id: int, db: Session = Depends(get_db)):
    success = repository.delete_person(db=db, person_id=person_id)
    if not success:
        raise HTTPException(status_code=404, detail="Person not found")
    return {"message": "Person deleted successfully"}