import os
from typing import Annotated
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DB_URL")

if not db_url:
    raise RuntimeError("Failed to initialize database. The URL string variable is required.")

engine = create_engine(db_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    
    try:
        yield db
    finally:
        db.close()
    

DbSession = Annotated[Session, Depends(get_db)]
