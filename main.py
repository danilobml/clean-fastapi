from fastapi import FastAPI
from dotenv import load_dotenv
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from src.rate_limiting import rate_limit_handler

from src.auth.controller.auth_controller import auth_router

load_dotenv()

limiter = Limiter(key_func=get_remote_address)

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
app.add_middleware(SlowAPIMiddleware)

app.include_router(auth_router)


@app.get("/")
async def root():
    return {"message": "hello world"}
