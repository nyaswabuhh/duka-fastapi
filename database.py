from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

db_url="postgresql://postgres:simbapos%402019@localhost:5432/fastapi_myduka"
engine=create_engine(db_url)

session=sessionmaker(autocommit=False, autoflush=False, bind=engine)