# api/routers/leaderboard.py
from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from ..dependencies import verify_api_key
from core.utils import LeaderBoard, initialize_leaderboard
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.get("/leaderboard")
@limiter.limit("5/minute")
async def display_leaderboard(
    request: Request, 
    api_key: str = Depends(verify_api_key)
):
    if not LeaderBoard.leader_board:
        await initialize_leaderboard()
    return LeaderBoard.leader_board