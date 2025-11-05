from sqlalchemy import Column, DateTime, Integer, Float, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship 
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash


Base=declarative_base()

class Product(Base):
    __tablename__='products'
    id=Column(Integer, primary_key=True)
    name=Column(String, nullable=False)
    buying_price=Column(Float,nullable=False)
    selling_price=Column(Float, nullable=False)

    sales=relationship("Sale", back_populates="product")

class Sale(Base):
    __tablename__="sales"
    id=Column(Integer, primary_key=True)
    pid=Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity=Column(Integer, nullable=False)
    created_at=Column(DateTime, default=datetime.utcnow, nullable=False)  

    product = relationship("Product", back_populates="sales")
    payments = relationship("Payment", back_populates="sale")

class User(Base):
    __tablename__="users"
    id=Column(Integer, primary_key=True)
    full_name=Column(String, nullable=False)
    email=Column(String, nullable=False,unique=True)
    password=Column(String, nullable=False)
    

class Payment(Base):
    __tablename__="payments"
    id=Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=True)
    trans_code=Column(String, nullable=True)
    mrid=Column(String, nullable=False)
    crid=Column(String, nullable=False)
    amount=Column(Integer, nullable=True)
    created_at=Column(DateTime, default=datetime.utcnow)

    sale = relationship("Sale", back_populates="payments")
