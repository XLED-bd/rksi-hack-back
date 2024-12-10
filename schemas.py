from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: UUID
    created_at: datetime

    class Config:
        orm_mode = True

class Stock(BaseModel):
    id: UUID
    symbol: str
    name: str
    last_price: float
    currency: str

    class Config:
        orm_mode = True

class TransactionCreate(BaseModel):
    stock_id: UUID
    amount: int
    price: float
    type: str

class Transaction(TransactionCreate):
    id: UUID
    created_at: datetime

    class Config:
        orm_mode = True

class Portfolio(BaseModel):
    id: UUID
    created_at: datetime

    class Config:
        orm_mode = True

class PortfolioPosition(BaseModel):
    stock_id: UUID
    amount: int
    average_price: float

    class Config:
        orm_mode = True