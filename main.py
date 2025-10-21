
from typing import Union
from fastapi import FastAPI, Depends
from pydantic import BaseModel
import models
from database import session, engine
from sqlalchemy.orm import Session

#Sentry/Slack/SQLAlchemy/Unit Tests /Gitflow Workflow/Jira/CI/CD, Docker

app=FastAPI()

models.Base.metadata.create_all(bind=engine)

def get_db():
    db=session()
    try:
        yield db
    finally:
        db.close()

class ProductData(BaseModel):
    name:str
    buying_price:float
    selling_price: float

class ProductDataResponse(ProductData):
    id: int
    


@app.get("/")
def home():
    return {"Duka FastAPI: 1.0"}


@app.get("/products", response_model=list[ProductDataResponse])
def get_products(db:Session=Depends(get_db)):
    return db.query(models.Product).all()


@app.post("/products", response_model=ProductDataResponse)
def add_product(prod : ProductData, db:Session=Depends(get_db)):
    db_prod=models.Product(**prod.model_dump())
    db.add(db_prod)
    db.commit()
    return db_prod
    


#Why FastAPI
#1. Type Hints - we can validate the data type expected by a route
#2. Classes/Objects which convert json to object and Pydantic to validate
#3. Aysnc/Await perform heavy tast like file upload asynchronously
#4. Swagger library - to document and test api routes