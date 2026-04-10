from fastapi import FastAPI
from dotenv import load_dotenv

from src.auth.controller.auth_controller import auth_router

load_dotenv()

app = FastAPI()

app.include_router(auth_router)

@app.get("/")
async def root():
    return {"message": "hello world"}
