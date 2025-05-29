from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, repository
from app.database import get_db

router = APIRouter(prefix="/cars", tags=["cars"])

@router.post("/", response_model=schemas.Car)
def create_car(car: schemas.CarCreate, db: Session = Depends(get_db)):
    if car.owner_id is not None:
        db_person = repository.get_person(db, person_id=car.owner_id)
        if not db_person:
            raise HTTPException(status_code=400, detail="Owner not found")
    return repository.create_car(db=db, car=car)

@router.get("/", response_model=list[schemas.Car])
def read_cars(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    cars = repository.get_cars(db, skip=skip, limit=limit)
    return cars

@router.get("/{car_id}", response_model=schemas.CarWithOwner)
def read_car(car_id: int, db: Session = Depends(get_db)):
    db_car = repository.get_car_with_owner(db, car_id=car_id)
    if db_car is None:
        raise HTTPException(status_code=404, detail="Car not found")
    return db_car

@router.put("/{car_id}", response_model=schemas.Car)
def update_car(
    car_id: int, car: schemas.CarUpdate, db: Session = Depends(get_db)
):
    if car.owner_id is not None:
        db_person = repository.get_person(db, person_id=car.owner_id)
        if not db_person:
            raise HTTPException(status_code=400, detail="Owner not found")
    
    db_car = repository.update_car(db=db, car_id=car_id, car=car)
    if db_car is None:
        raise HTTPException(status_code=404, detail="Car not found")
    return db_car

@router.delete("/{car_id}")
def delete_car(car_id: int, db: Session = Depends(get_db)):
    success = repository.delete_car(db=db, car_id=car_id)
    if not success:
        raise HTTPException(status_code=404, detail="Car not found")
    return {"message": "Car deleted successfully"}