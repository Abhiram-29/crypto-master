from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from ..dependencies import get_database
from models import UserRequest, updateParameters, endParameters, startParameters
from core.utils import LeaderBoard
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.post("/end")
@limiter.limit("30/second")
async def game_end(
    request: Request,
    params: endParameters,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    user = await db.Users.find_one({"user_id": params.user_id})
    if not user:
        logger.error("Invalid user Id entered")
        logger.error(params.user_id)
    LeaderBoard.update(params.user_id, user.get("coins"))
    result = await db.Users.update_one(
        {"user_id": params.user_id}, {"$set": {"end_time": datetime.utcnow()}}
    )
    if not result.modified_count:
        logger.error("Leaderboard was not updated")

    return {"success": True, "Final coin tally": user.get("coins")}

@router.post("/questionStart")
@limiter.limit("30/second")
async def question_start(
    request : Request,
    params : startParameters,
    db : AsyncIOMotorDatabase = Depends(get_database),
):
    user = await db.Users.find_one({"user_id" : params.user_id})
    if not user:
        logger.error(f"The user id {params.user_id} does not exist in the database")
        return {"success":False,"message":"The user does not exits","question_id":""}
    questions = user.get("questions")
    coins = user.get("coins")
    print(coins)
    updated_coins = coins - params.bet_amt
    if updated_coins < 0:
        logger.warning("Invalid bet amount recieved")
        return {"success":False,"message":"Bet amount exceeded total number of coins available to the player","question_id":""}
    found = False
    for i in range(len(questions)):
        if questions[i].get("question_id") == params.question_id:
            questions[i]["status"] = "attempting"
            found = True
            break
    if not found:
        return {"success":False,"messasge":"Invalid question id","question_id":""}
    
    result = await db.Users.update_one(
        {"user_id" : params.user_id},
        {"$set" : {
            "coins" : updated_coins,
            "questions" : questions,
            "time_left" : params.time_left
        } },
        upsert = True
    )

    return {"success":True,"message":"user state updated","question_id":params.question_id,"updated_coins":updated_coins}