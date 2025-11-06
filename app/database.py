from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

#db_url="postgresql://postgres:simbapos%402019@host.docker.internal:5432/fastapi_myduka"
db_url='postgresql://myduka_user:simbapos2019@172.17.0.1:5432/fastapi_myduka'
engine=create_engine(db_url)

session=sessionmaker(autocommit=False, autoflush=False, bind=engine)