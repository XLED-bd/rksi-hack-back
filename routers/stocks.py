from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Stock
from schemas import Stock as StockSchema, StockCreate as StockCreateSchema
from uuid import UUID, uuid4
from datetime import datetime

router = APIRouter()

@router.get("/api/stocks", response_model=list[StockSchema])
def read_stocks(db: Session = Depends(get_db)):
    stocks = db.query(Stock).all()
    return stocks

@router.get("/api/stocks/{stock_id}", response_model=StockSchema)
def read_stock(stock_id: UUID, db: Session = Depends(get_db)):
    stock = db.query(Stock).filter(Stock.id == stock_id).first()
    return stock

@router.post("/api/stocks", response_model=StockSchema)
def create_stock(
    stock: StockCreateSchema,
    db: Session = Depends(get_db)):
    db_stock = db.query(Stock).filter(Stock.symbol == stock.symbol).first()
    if db_stock:
        raise HTTPException(status_code=400, detail="Stock with this symbol already exists")

    new_stock = Stock(
        id=uuid4(),
        symbol=stock.symbol,
        name=stock.name,
        currency=stock.currency,
        last_price=stock.last_price,
        last_updated=datetime.utcnow()
    )

    db.add(new_stock)
    db.commit()
    db.refresh(new_stock)

    return new_stock