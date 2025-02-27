# main.py
from fastapi import FastAPI, Request, Security, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from core.database import MongoDB, initialize_leaderboard
from api.routers import questions, users, leaderboard, gameControl, admin
from core.config import settings
import logging
import os
import secrets
from dotenv import load_dotenv
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN


VALID_API_KEYS = set(settings.API_KEY.split(','))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)

api_key_header = APIKeyHeader(name="API_KEY", auto_error=False)

async def get_api_key(api_key: str = Security(api_key_header)):
    if not api_key or not any(secrets.compare_digest(api_key, key) for key in VALID_API_KEYS):
        logger.error(api_key)
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid API Key")
    return api_key

app = FastAPI(dependencies=[Depends(get_api_key)])

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
class DocsBypassMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in ["/docs", "/openapi.json", "/redoc"]:
            return await call_next(request)
        return await call_next(request)

app.add_middleware(DocsBypassMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(questions.router)
app.include_router(users.router)
app.include_router(leaderboard.router)
app.include_router(gameControl.router)
app.include_router(admin.router)

@app.on_event("startup")
async def startup_db():
    await MongoDB.connect()
    await initialize_leaderboard()
    logger.info("Database connected successfully")


@app.on_event("shutdown")
async def shutdown_db():
    await MongoDB.close()
    logger.info("Database disconnected")