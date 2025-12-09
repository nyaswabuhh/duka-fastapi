from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import app.models as models
from app.database import session, engine
from sqlalchemy.orm import Session
from datetime import datetime
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500","http://localhost:3000", "http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
models.Base.metadata.create_all(bind=engine)


# DB Session Dependency
def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()


# =======================
#   Pydantic Models
# =======================

# Products
class ProductData(BaseModel):
    name: str
    buying_price: float
    selling_price: float

class ProductDataResponse(ProductData):
    id: int

# Users
class User(BaseModel):
    full_name: str
    email: str
    password: str

class UserResponse(User):
    id: int

class UserLogin(BaseModel):
    email: str
    password: str


# Sales
class Sale(BaseModel):
    pid: int
    quantity: int

class SaleResponse(Sale):
    id: int
    created_at: datetime


# Payments
class Payment(BaseModel):
    sale_id: int
    trans_code: str
    mrid: str
    crid: str
    amount: int

class PaymentResponse(Payment):
    id: int
    created_at: datetime


# =======================
#       Routes
# =======================

@app.get("/")
def home():
    return {"message": "Duka FastAPI 1.0 — JWT Disabled"}


# -------- PRODUCTS ----------
@app.get("/products", response_model=list[ProductDataResponse])
def get_products(db: Session = Depends(get_db)):
    return db.query(models.Product).all()


@app.post("/products", response_model=ProductDataResponse)
def add_product(prod: ProductData, db: Session = Depends(get_db)):
    db_prod = models.Product(**prod.model_dump())
    db.add(db_prod)
    db.commit()
    db.refresh(db_prod)
    return db_prod


# -------- USERS ----------
@app.get("/users", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()


@app.post("/register", response_model=UserResponse)
def register(user: User, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user.password = password_hash.hash(user.password)

    db_user = models.User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not password_hash.verify(user.password, db_user.password): # pyright: ignore[reportArgumentType]
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {"message": "Login successful", "full_name": db_user.full_name}


# -------- SALES ----------
@app.get("/sales", response_model=list[SaleResponse])
def get_sales(db: Session = Depends(get_db)):
    return db.query(models.Sale).all()


@app.post("/sales", response_model=SaleResponse)
def create_sale(sale: Sale, db: Session = Depends(get_db)):
    db_sale = models.Sale(**sale.model_dump())
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    return db_sale


# -------- PAYMENTS ----------
@app.get("/payments", response_model=list[PaymentResponse])
def get_payments(db: Session = Depends(get_db)):
    return db.query(models.Payment).all()


@app.post("/payments", response_model=PaymentResponse)
def create_payment(payment: Payment, db: Session = Depends(get_db)):
    db_payment = models.Payment(**payment.model_dump())
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment


# Why FastAPI?
# - Type hints for validation
# - Pydantic for data integrity
# - Async support
# - Swagger UI for documentation
