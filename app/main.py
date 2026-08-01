from fastapi import FastAPI
from app.config import settings
from app.database import engine, Base
from app.models import db_models

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def read_root():
    return {"status":"HR integration platform is running"}