from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Portfolio, PortfolioPosition, Stock, User as UserModel
from schemas import Portfolio as PortfolioSchema, PortfolioPosition as PortfolioPositionSchema, PortfolioPositionResponse
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

@router.post("/api/portfolios", response_model=PortfolioSchema)
def create_portfolio(db: Session = Depends(get_db)):
    portfolio = Portfolio(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(), 
        created_at=datetime.utcnow()
    )
    db.add(portfolio)
    db.commit()
    db.refresh(portfolio)
    return portfolio

@router.get("/api/portfolios/{portfolio_id}/positions", response_model=list[PortfolioPositionSchema])
def read_portfolio_positions(portfolio_id: UUID, db: Session = Depends(get_db)):
    positions = db.query(PortfolioPosition).filter(PortfolioPosition.portfolio_id == portfolio_id).all()
    return positions