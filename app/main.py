from fastapi import FastAPI
from app.config import settings
from app.database import engine, Base
from app.models import db_models
from app.routers import webhooks, employees

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(webhooks.router)
app.include_router(employees.router)

@app.get("/")
def read_root():
    return {"status":"HR integration platform is running"}