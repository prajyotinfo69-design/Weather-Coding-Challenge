from fastapi import FastAPI
from src.db.session import engine
from src.models import Base
from src.api.v1.api import api_router

# Create tables on first run
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Weather & Yield API", version="1.0.0")
app.include_router(api_router)
