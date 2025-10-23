
from typing import Union
from fastapi import FastAPI, Depends
from pydantic import BaseModel
import models
from database import session, engine
from sqlalchemy.orm import Session
from datetime import datetime


#Sentry/Slack/SQLAlchemy/Unit Tests /Gitflow Workflow/Jira/CI/CD, Docker

app=FastAPI()

models.Base.metadata.create_all(bind=engine)

def get_db():
    db=session()
    try:
        yield db
    finally:
        db.close()

#products
class ProductData(BaseModel):
    name:str
    buying_price:float
    selling_price: float

class ProductDataResponse(ProductData):
    id: int

#users
class User(BaseModel):
    full_name:str
    email: str
    password: str

class UserResponse(User):
    id: int

class UserLogin(BaseModel):
    email: str
    password: str

class UserLoginResponse(BaseModel):
    email: str
    full_name: str
    


#sales    
class Sale(BaseModel):
    pid: int
    quantity: int

class SaleResponse(Sale):
    id: int
    created_at: datetime



@app.get("/")
def home():
    return {"Duka FastAPI: 1.0"}

#get products route
@app.get("/products", response_model=list[ProductDataResponse])
def get_products(db:Session=Depends(get_db)):
    return db.query(models.Product).all()

#create products route
@app.post("/products", response_model=ProductDataResponse)
def add_product(prod : ProductData, db:Session=Depends(get_db)):
    db_prod=models.Product(**prod.model_dump())
    db.add(db_prod)
    db.commit()
    return db_prod

#get users route
@app.get("/users", response_model=list[UserResponse])
def get_users(db:Session=Depends(get_db)):
    return db.query(models.User).all()

# register user
@app.post("/users", response_model=UserResponse)
def add_user(user: User, db:Session=Depends(get_db)):
    db_user=models.User(**user.model_dump())
    db.add(db_user)
    db.commit()
    return db_user

#login user
@app.post("/users/login", response_model=UserLoginResponse)
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email, models.User.password == user.password).first()

    if not db_user:
        return "Invalid email or password"

    return db_user
    

#get sales
@app.get("/sales", response_model=list[SaleResponse])
def get_sales(db:Session=Depends(get_db)):
    return db.query(models.Sale).all()

#create a sale
@app.post("/sales", response_model=SaleResponse)
def create_sale(sale:Sale, db:Session=Depends(get_db)):
    db_sale=models.Sale(**sale.model_dump())
    db.add(db_sale)
    db.commit()
    return db_sale

#Why FastAPI
#1. Type Hints - we can validate the data type expected by a route
#2. Classes/Objects which convert json to object and Pydantic to validate
#3. Aysnc/Await perform heavy tast like file upload asynchronously
#4. Swagger library - to document and test api routes