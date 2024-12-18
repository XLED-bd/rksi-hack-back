from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from uuid import UUID

class UserBase(BaseModel):
    email: EmailStr

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


class StockCreate(BaseModel):
    symbol: str
    name: str
    currency: str
    last_price: float

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

class TransactionHistory(BaseModel):
    id: UUID
    stock_name: str
    stock_symbol: str
    stock_last_price: float
    amount: int
    price: float
    type: str
    created_at: datetime

    class Config:
        orm_mode = True

class TransactionCreate(BaseModel):
    stock_id: UUID
    amount: int
    price: float
    type: str

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

class PortfolioPositionResponse(BaseModel):
    portfolio_id: UUID
    stock_name: str
    stock_symbol: str
    amount: int
    current_price: float
    average_purchase_price: float

    class Config:
        orm_mode = True


class PortfolioValue(BaseModel):
    total_value: float


class PortfolioPositionCreate(BaseModel):
    portfolio_id: UUID
    stock_id: UUID
    amount: int
    average_price: float

class PortfolioPositionSchema(BaseModel):
    id: UUID
    portfolio_id: UUID
    stock_id: UUID
    amount: int
    average_price: float

    class Config:
        orm_mode = True


class TransactionCreate(BaseModel):
    stock_id: UUID
    amount: int
    price: float
    type: str  # BUY или SELL

class TransactionSchema(BaseModel):
    id: UUID
    stock_id: UUID
    amount: int
    price: float
    type: str
    created_at: datetime

    class Config:
        orm_mode = True