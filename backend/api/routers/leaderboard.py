# api/routers/leaderboard.py
from fastapi import APIRouter, Depends, Request, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging
from api.dependencies import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)
router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.get("/leaderboard")
@limiter.limit("5/minute")
async def display_leaderboard(
    request: Request,
    db : AsyncIOMotorDatabase = Depends(get_database)
    
    ):
    """
    Get the current leaderboard.
    Returns top users sorted by coins in descending order.
    """
    try:
        users = await db.Users.find({}).to_list(length=None)
        leaderboard = {}
        for user in users:
            leaderboard[user.get("user_id")] = user.get("coins")
        return leaderboard
    
    except Exception as e:
        logger.error(f"Error displaying leaderboard: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve leaderboard")