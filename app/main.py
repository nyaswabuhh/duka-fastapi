
from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import app.models as models
from app.database import session, engine
from sqlalchemy.orm import Session
from datetime import datetime
from app.jwt_service import create_access_token, get_current_active_user
from fastapi import Depends, FastAPI, HTTPException, status
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

#Sentry/Slack/SQLAlchemy/Unit Tests /Gitflow Workflow/Jira/CI/CD, Docker

app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

class Token(BaseModel):
    access_token: str |None=None  


#sales    
class Sale(BaseModel):
    pid: int
    quantity: int

class SaleResponse(Sale):
    id: int
    created_at: datetime

#payment
class Payment(BaseModel):
    sale_id: int
    trans_code: str
    mrid: str
    crid: str
    amount: int

class PaymentRepsonse(Payment):
    id: int
    created_at: datetime   


@app.get("/")
def home():
    return {"Duka FastAPI: 1.0"}

#get products route
@app.get("/products", response_model=list[ProductDataResponse])
async def get_products(user: Annotated[str, Depends(get_current_active_user)],db:Session=Depends(get_db)):
    print("from main the user is.........", user)
    return db.query(models.Product).all()

#create products route
@app.post("/products", response_model=ProductDataResponse)
def add_product(user: Annotated[str, Depends(get_current_active_user)],prod : ProductData, db:Session=Depends(get_db)):
    print("current user.............",user)
    db_prod=models.Product(**prod.model_dump())
    db.add(db_prod)
    db.commit()
    return db_prod

#get users route
@app.get("/users", response_model=list[UserResponse])
def get_users(db:Session=Depends(get_db)):
    return db.query(models.User).all()

# register user
@app.post("/register", response_model=Token)
def register(user: User, db:Session=Depends(get_db)):
    try:
        existing_user = db.query(models.User).filter(models.User.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")    
        user.password = password_hash.hash(user.password)    
        db_user=models.User(**user.model_dump())
        db.add(db_user)
        db.commit()    
        token= create_access_token(user.email)
        return {"access_token":token}
    except:
        raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Something went wrong"
    )     

#login user
@app.post("/login", response_model=Token | dict[str,str])
def login(user: UserLogin, db: Session = Depends(get_db)):
    try:
        db_user = db.query(models.User).filter(models.User.email == user.email).first()
        response = password_hash.verify(user.password, str(db_user.password))      # type: ignore
        if response == True:
            token= create_access_token(user.email)            
            return {"access_token":token}
        else:
            pass
    except:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid Email or Password"
    )     

#get sales
@app.get("/sales", response_model=list[SaleResponse])
def get_sales(db:Session=Depends(get_db)):
    return db.query(models.Sale).all()

#create a sale
@app.post("/sales", response_model=SaleResponse)
def create_sale(user: Annotated[str, Depends(get_current_active_user)],sale:Sale, db:Session=Depends(get_db)):
    db_sale=models.Sale(**sale.model_dump())
    db.add(db_sale)
    db.commit()
    return db_sale

#fetch payments
@app.get("/payments", response_model=list[PaymentRepsonse])
def get_payments(db:Session=Depends(get_db)):
    return db.query(models.Payment).all()

#create payment
@app.post("/payments", response_model=PaymentRepsonse)
def create_payment(payment:Payment, db:Session=Depends(get_db)):
    db_payment= models.Payment(**payment.model_dump())
    db.add(db_payment)
    db.commit()
    return db_payment




#Why FastAPI
#1. Type Hints - we can validate the data type expected by a route
#2. Classes/Objects which convert json to object and Pydantic to validate
#3. Aysnc/Await perform heavy tast like file upload asynchronously
#4. Swagger library - to document and test api routes