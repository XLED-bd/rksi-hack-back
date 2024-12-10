from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Portfolio, PortfolioPosition
from schemas import Portfolio as PortfolioSchema, PortfolioPosition as PortfolioPositionSchema
import uuid
from uuid import UUID
from datetime import datetime

router = APIRouter()

@router.get("/api/portfolios", response_model=list[PortfolioSchema])
def read_portfolios(db: Session = Depends(get_db)):
    portfolios = db.query(Portfolio).all()
    return portfolios

@router.post("/api/portfolios", response_model=PortfolioSchema)
def create_portfolio(db: Session = Depends(get_db)):
    portfolio = Portfolio(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),  # Assuming user is authenticated
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