from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import User

router = APIRouter()

@router.get("/api/users/me", response_model=User)
def read_users_me(db: Session = Depends(get_db)):
    user = db.query(User).first()
    return user