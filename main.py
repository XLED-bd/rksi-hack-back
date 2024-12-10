from fastapi import FastAPI
from routers import auth, users, stocks, portfolios, transactions

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(stocks.router)
app.include_router(portfolios.router)
app.include_router(transactions.router)

@app.get("/")
def read_root():
    return {"message": "hello"}


from database import Base, engine

Base.metadata.create_all(bind=engine)