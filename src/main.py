from typing import List
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
import os
from . import crud, models, schemas
from .database import SessionLocal, engine
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/getAllData")
def getAllData(db: Session = Depends(get_db)):
    return crud.get_all_data(db)
