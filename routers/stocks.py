from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Stock
from schemas import Stock as StockSchema
from uuid import UUID

router = APIRouter()

@router.get("/api/stocks", response_model=list[StockSchema])
def read_stocks(db: Session = Depends(get_db)):
    stocks = db.query(Stock).all()
    return stocks

@router.get("/api/stocks/{stock_id}", response_model=StockSchema)
def read_stock(stock_id: UUID, db: Session = Depends(get_db)):
    stock = db.query(Stock).filter(Stock.id == stock_id).first()
    return stock