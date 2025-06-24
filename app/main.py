from fastapi import FastAPI
from app.database import engine
from app import models
from app.routers import cars, people
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Car API",
    description="A simple Car API to exercise UnitTests",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ Em produção, use apenas domínios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(people.router)
app.include_router(cars.router)