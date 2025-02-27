from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from ..dependencies import get_database
from models import auctionParameters
from core.utils import LeaderBoard
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.post("/auction"):
def auction(
    request: Request,
    params: auctionParameters,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    