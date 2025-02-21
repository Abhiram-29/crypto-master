# main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from core.database import MongoDB, initialize_leaderboard
from api.routers import questions, users, leaderboard, gameControl
from core.config import settings
import logging
import os
import secrets
from dotenv import load_dotenv
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

load_dotenv("../.env")

VALID_API_KEYS = set(os.getenv("API_KEYS","").split(','))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)

class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self,request: Request, call_next):
        api_key = request.headers.get("API-Key")

        if not api_key or not any(secrets.compare_digest(api_key,key) for key in VALID_API_KEYS):
            return JSONResponse(status_code=403,content={"detail":"Invalid API Key"})
        
        return await call_next(request)


app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    APIKeyMiddleware,
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(questions.router)
app.include_router(users.router)
app.include_router(leaderboard.router)


@app.on_event("startup")
async def startup_db():
    await MongoDB.connect()
    await initialize_leaderboard()


@app.on_event("shutdown")
async def shutdown_db():
    await MongoDB.close()

@app.get("/")
async def greet():
    return "API is running"