from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Infraction

app = FastAPI(title="Condo Infraction API")

@app.get("/")
def root():
    return {"message": "API is running with clean architecture"}

@app.get("/infractions")
def read_infractions(db: Session = Depends(get_db)):
    return db.query(Infraction).all()