from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Transaction
from schemas import TransactionCreate, Transaction as TransactionSchema
import uuid
from datetime import datetime

router = APIRouter()

@router.post("/api/transactions", response_model=TransactionSchema)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    db_transaction = Transaction(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),  
        stock_id=transaction.stock_id,
        amount=transaction.amount,
        price=transaction.price,
        type=transaction.type,
        created_at=datetime.utcnow()
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@router.get("/api/transactions", response_model=list[TransactionSchema])
def read_transactions(db: Session = Depends(get_db)):
    transactions = db.query(Transaction).all()
    return transactions