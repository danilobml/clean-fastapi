import os
from typing import Annotated
from fastapi import Depends
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from ..errors.custom import FailedDbInitError

load_dotenv()

db_url = os.getenv("DB_URL")

if not db_url:
    raise FailedDbInitError()

engine = create_engine(db_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    
    try:
        yield db
    finally:
        db.close()
    

DbSession = Annotated[Session, Depends(get_db)]
