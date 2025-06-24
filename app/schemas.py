from datetime import date
from pydantic import BaseModel
from typing import Optional, List

class CarBase(BaseModel):
    make: str
    model: str
    year: int
    color: str
    price: float
    owner_id: Optional[int] = None

class CarCreate(CarBase):
    pass

class Car(CarBase):
    id: int
    
    class Config:
        from_attributes = True
        orm_mode = True

class CarUpdate(BaseModel):
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    color: Optional[str] = None
    price: Optional[float] = None
    owner_id: Optional[int] = None

class PersonBase(BaseModel):
    name: str
    cpf: str
    birth_date: date

class PersonCreate(PersonBase):
    pass

class Person(PersonBase):
    id: int
    
    class Config:
        from_attributes = True
        orm_mode = True

class PersonUpdate(BaseModel):
    name: Optional[str] = None
    cpf: Optional[str] = None
    birth_date: Optional[date] = None

class PersonWithCars(Person):
    cars: List[Car] = []
    
    class Config:
        from_attributes = True
        orm_mode = True
class CarWithOwner(Car):
    owner: Optional[Person] = None
    
    class Config:
        from_attributes = True
        orm_mode = True

class CarOwnerUpdate(BaseModel):
    """Schema para atualizar apenas o proprietário do carro"""
    owner_id: Optional[int] = None

class PersonCarAssociation(BaseModel):
    """Schema para associar/desassociar carros de pessoas"""
    car_id: int
    action: str  # 'add' or 'remove'