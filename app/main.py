from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app import models, schemas, repository
from app.database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Car API",
    description="A simple Car API to exercise UnitTests",
    version="0.1.0"
)

@app.post("/cars/", response_model=schemas.Car)
def create_car(car: schemas.CarCreate, db: Session = Depends(get_db)):
    return repository.create_car(db=db, car=car)

@app.get("/cars/", response_model=list[schemas.Car])
def read_cars(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return repository.get_cars(db=db, skip=skip, limit=limit)

@app.get("/cars/{car_id}", response_model=schemas.Car)
def read_car(car_id: int, db: Session = Depends(get_db)):
    db_car = repository.get_car(db=db, car_id=car_id)
    if db_car is None:
        raise HTTPException(status_code=404, detail="Car not found")
    return db_car

@app.put("/cars/{car_id}", response_model=schemas.Car)
def update_car(car_id: int, car: schemas.CarUpdate, db: Session = Depends(get_db)):
    db_car = repository.update_car(db=db, car_id=car_id, car=car)
    if db_car is None:
        raise HTTPException(status_code=404, detail="Car not found")
    return db_car

@app.delete("/cars/{car_id}")
def delete_car(car_id: int, db: Session = Depends(get_db)):
    success = repository.delete_car(db=db, car_id=car_id)
    if not success:
        raise HTTPException(status_code=404, detail="Car not found")
    return {"message": "Car deleted successfully"}