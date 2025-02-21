# api/dependencies.py
from fastapi import Security, HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader
from core.config import settings  # Import from core.config
from core.database import MongoDB
from starlette.status import HTTP_403_FORBIDDEN
import logging

logger = logging.getLogger(__name__)

api_key_header = APIKeyHeader(name="API_KEY", auto_error=True)

async def get_database():
    if MongoDB.db is None:
        await MongoDB.connect()
    return MongoDB.db