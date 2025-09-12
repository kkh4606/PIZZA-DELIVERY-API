from fastapi import FastAPI
from app.routers import auth, order
from .database import Base, engine
from fastapi.openapi.utils import get_openapi

Base.metadata.create_all(bind=engine)
app = FastAPI()


app.include_router(auth.router)
app.include_router(order.router)
