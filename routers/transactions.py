from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Transaction, Stock, User as UserModel
from schemas import TransactionCreate, Transaction as TransactionSchema, TransactionHistory
import uuid
from uuid import uuid4
from datetime import datetime
from routers.users import get_current_user


router = APIRouter()

@router.post("/api/transaction", response_model=TransactionSchema)
def view_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
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


@router.post("/api/transactions", response_model=dict)
def create_transaction(
    transaction: TransactionCreate,
    current_user: UserModel = Depends(get_current_user),  # Проверяем авторизацию
    db: Session = Depends(get_db)
):
    print(current_user.id)
    print(current_user.email)
    # Проверяем, существует ли акция
    stock = db.query(Stock).filter(Stock.id == transaction.stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")

    # Проверяем, что тип транзакции корректен
    if transaction.type not in ["BUY", "SELL"]:
        raise HTTPException(status_code=400, detail="Transaction type must be BUY or SELL")

    # Создаем новую транзакцию
    new_transaction = Transaction(
        id=uuid4(),
        user_id=current_user.id,
        stock_id=transaction.stock_id,
        amount=transaction.amount,
        price=transaction.price,
        type=transaction.type,
        created_at=datetime.utcnow()
    )

    # Добавляем транзакцию в базу данных
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return {
        "id": str(new_transaction.id),
        "created_at": new_transaction.created_at
    }

@router.get("/api/transactions/history", response_model=list[TransactionHistory])
def get_transaction_history(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Объединяем таблицы transactions и stocks
    transactions = db.query(
        Transaction.id,
        Stock.name.label("stock_name"),
        Stock.symbol.label("stock_symbol"),
        Stock.last_price.label("stock_last_price"),
        Transaction.amount,
        Transaction.price,
        Transaction.type,
        Transaction.created_at
    ).join(Stock, Transaction.stock_id == Stock.id) \
     .filter(Transaction.user_id == current_user.id) \
     .all()

    if not transactions:
        raise HTTPException(status_code=404, detail="No transactions found for this user")

    return transactions