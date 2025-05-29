from fastapi import FastAPI
from app.database import engine
from app import models
from app.routers import cars, people

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Car API",
    description="A simple Car API to exercise UnitTests",
    version="0.1.0"
)

app.include_router(people.router)
app.include_router(cars.router)