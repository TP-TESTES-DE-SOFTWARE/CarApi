from pydantic import BaseModel
from typing import Optional

class CarBase(BaseModel):
    make: str
    model: str
    year: int
    color: str
    price: float

class CarCreate(CarBase):
    pass

class Car(CarBase):
    id: int

    class Config:
        from_attributes = True

class CarUpdate(BaseModel):
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    color: Optional[str] = None
    price: Optional[float] = None