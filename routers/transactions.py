from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Transaction, Stock, User as UserModel
from schemas import TransactionCreate, Transaction as TransactionSchema, TransactionHistory
from schemas import TransactionCreate, TransactionSchema
from models import Portfolio, PortfolioPosition, Stock
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




@router.post("/api/transactions/buy", response_model=TransactionSchema)
def buy_stock(
    transaction_data: TransactionCreate,  # Тело запроса
    current_user: UserModel = Depends(get_current_user),  # Проверка авторизации
    db: Session = Depends(get_db)
):
    # Проверяем, существует ли акция
    stock = db.query(Stock).filter(Stock.id == transaction_data.stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")

    # Проверяем, что количество акций положительное
    if transaction_data.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")

    # Получаем портфель пользователя
    portfolio = db.query(Portfolio).filter(Portfolio.user_id == current_user.id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found for this user")

    # Создаем новую транзакцию
    new_transaction = Transaction(
        id=uuid4(),
        user_id=current_user.id,
        stock_id=transaction_data.stock_id,
        amount=transaction_data.amount,
        price=transaction_data.price,
        type="BUY",
        created_at=datetime.utcnow()
    )

    # Обновляем позицию в портфеле
    position = db.query(PortfolioPosition).filter(
        PortfolioPosition.portfolio_id == portfolio.id,
        PortfolioPosition.stock_id == transaction_data.stock_id
    ).first()

    if position:
        # Если позиция уже существует, обновляем её
        position.amount += transaction_data.amount
        position.average_price = (
            (position.average_price * (position.amount - transaction_data.amount)) +
            (transaction_data.price * transaction_data.amount)
        ) / position.amount
    else:
        # Если позиции нет, создаем новую
        new_position = PortfolioPosition(
            id=uuid4(),
            portfolio_id=portfolio.id,
            stock_id=transaction_data.stock_id,
            amount=transaction_data.amount,
            average_price=transaction_data.price
        )
        db.add(new_position)

    # Добавляем транзакцию в базу данных
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction


@router.post("/api/transactions/sell", response_model=TransactionSchema)
def sell_stock(
    transaction_data: TransactionCreate,  # Тело запроса
    current_user: UserModel = Depends(get_current_user),  # Проверка авторизации
    db: Session = Depends(get_db)
):
    # Проверяем, существует ли акция
    stock = db.query(Stock).filter(Stock.id == transaction_data.stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")

    # Проверяем, что количество акций положительное
    if transaction_data.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")

    # Получаем портфель пользователя
    portfolio = db.query(Portfolio).filter(Portfolio.user_id == current_user.id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found for this user")

    # Проверяем, есть ли достаточное количество акций для продажи
    position = db.query(PortfolioPosition).filter(
        PortfolioPosition.portfolio_id == portfolio.id,
        PortfolioPosition.stock_id == transaction_data.stock_id
    ).first()

    if not position or position.amount < transaction_data.amount:
        raise HTTPException(status_code=400, detail="Not enough stocks to sell")

    # Создаем новую транзакцию
    new_transaction = Transaction(
        id=uuid4(),
        user_id=current_user.id,
        stock_id=transaction_data.stock_id,
        amount=transaction_data.amount,
        price=transaction_data.price,
        type="SELL",
        created_at=datetime.utcnow()
    )

    # Обновляем позицию в портфеле
    position.amount -= transaction_data.amount
    if position.amount == 0:
        # Если количество акций стало 0, удаляем позицию
        db.delete(position)
    else:
        # Иначе обновляем позицию
        position.average_price = (
            (position.average_price * (position.amount + transaction_data.amount)) -
            (transaction_data.price * transaction_data.amount)
        ) / position.amount

    # Добавляем транзакцию в базу данных
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction