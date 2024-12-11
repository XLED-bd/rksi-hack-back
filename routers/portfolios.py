from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Portfolio, PortfolioPosition, Stock, User as UserModel
from schemas import Portfolio as PortfolioSchema, PortfolioPosition as PortfolioPositionSchema, PortfolioPositionResponse, PortfolioPositionCreate
from uuid import UUID
import uuid
from datetime import datetime
from routers.users import get_current_user

router = APIRouter()

@router.get("/api/portfolios", response_model=list[PortfolioPositionResponse])
def get_portfolio(
    current_user: UserModel = Depends(get_current_user),  # Проверяем авторизацию
    db: Session = Depends(get_db)
):
    # Получаем портфель пользователя
    portfolio = db.query(Portfolio).filter(Portfolio.user_id == current_user.id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found for this user")

    # Получаем позиции в портфеле с объединением таблиц
    positions = db.query(
        PortfolioPosition.portfolio_id,
        Stock.name.label("stock_name"),
        Stock.symbol.label("stock_symbol"),
        Stock.last_price.label("current_price"),
        PortfolioPosition.amount,
        PortfolioPosition.average_price.label("average_purchase_price")
    ).join(Stock, PortfolioPosition.stock_id == Stock.id) \
     .filter(PortfolioPosition.portfolio_id == portfolio.id) \
     .all()

    if not positions:
        raise HTTPException(status_code=404, detail="No positions found in the portfolio")

    return positions

@router.post("/api/portfolio_positions", response_model=PortfolioPositionSchema)
def create_portfolio_position(
    position_data: PortfolioPositionCreate,  # Тело запроса
    current_user: UserModel = Depends(get_current_user),  # Проверка авторизации
    db: Session = Depends(get_db)
):
    # Проверяем, существует ли портфель
    portfolio = db.query(Portfolio).filter(Portfolio.id == position_data.portfolio_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    # Проверяем, что текущий пользователь владеет этим портфелем
    if portfolio.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have access to this portfolio")

    # Проверяем, существует ли акция
    stock = db.query(Stock).filter(Stock.id == position_data.stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")

    # Проверяем, что количество акций положительное
    if position_data.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")

    # Создаем новую позицию в портфеле
    new_position = PortfolioPosition(
        id=uuid.uuid4(),
        portfolio_id=position_data.portfolio_id,
        stock_id=position_data.stock_id,
        amount=position_data.amount,
        average_price=position_data.average_price
    )

    # Добавляем позицию в базу данных
    db.add(new_position)
    db.commit()
    db.refresh(new_position)

    return new_position




@router.delete("/api/portfolio_positions/{position_id}", response_model=dict)
def delete_portfolio_position(
    position_id: UUID,
    current_user: UserModel = Depends(get_current_user),  # Проверка авторизации
    db: Session = Depends(get_db)
):
    # Проверяем, существует ли позиция
    position = db.query(PortfolioPosition).filter(PortfolioPosition.id == position_id).first()
    if not position:
        raise HTTPException(status_code=404, detail="Portfolio position not found")

    # Проверяем, что текущий пользователь владеет этим портфелем
    portfolio = db.query(Portfolio).filter(Portfolio.id == position.portfolio_id).first()
    if portfolio.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have access to this portfolio")

    # Удаляем позицию из базы данных
    db.delete(position)
    db.commit()

    return {"message": "Portfolio position deleted successfully"}


@router.get("/api/portfolios/{portfolio_id}/positions", response_model=list[PortfolioPositionSchema])
def read_portfolio_positions(portfolio_id: UUID, db: Session = Depends(get_db)):
    positions = db.query(PortfolioPosition).filter(PortfolioPosition.portfolio_id == portfolio_id).all()
    return positions