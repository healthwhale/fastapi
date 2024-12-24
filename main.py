from fastapi import FastAPI
from .api_routes import app as api_routes_app

app = FastAPI()

app.mount("/", api_routes_app)
