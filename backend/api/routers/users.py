# api/routers/users.py
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


@router.post("/login")
@limiter.limit("20/second")
async def login(
    request: Request,
    login_request: UserRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    success = True
    message = ""
    user_id = login_request.user_id
    user = await db.Users.find_one({"user_id": user_id})
    if not user:
        return {"success": False, "message": "User not found"}
    start_time = user.get("start_time")
    logged_in = user.get("logged_in")
    time_left = user.get("time_left")
    if logged_in == "False":
        logged_in = False
    if not logged_in:
        time_left = 1500
        await db.Users.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "start_time": datetime.utcnow(),
                    "logged_in": True,
                    "questions_attempted": [],
                    "time_left": 1500,
                }
            },
            upsert=True,
        )
        message = "User loggedin for the first time"
    return {
        "success": success,
        "message": message,
        "user_id": user_id,
        "name": user.get("name"),
        "email_id": user.get("email_id"),
        "coins": user.get("coins"),
        "time_left": time_left,
        "questions_attempted": user.get("questions_attempted"),
    }


@router.post("/update")
@limiter.limit("30/second")
# need to add tracking for the last question solved by user
async def update_score(
    request: Request,
    params: updateParameters,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    print("Entered update")
    user = await db.Users.find_one({"user_id": params.user_id})
    print("User fetch done")
    message = ""
    updated_coins = 0
    if params.solved != True:
        logger.info(params.solved)
        updated_coins = user.get("coins")
        message = f"the user lost {params.spent_amt} coins"
    else:
        updated_coins = user.get("coins") + params.spent_amt * params.multiplier
        message = f"the user won {updated_coins - params.spent_amt} coins"
    logger.info(updated_coins)
    questions = user.get("questions")
    logger.info(params.question_id)
    idx = -1
    for i in range(len(questions)):
        if questions[i].get("question_id") == params.question_id:
            logger.info("question found")
            logger.info(params.solved == True)
            idx = i
            if params.solved:
                questions[i]["status"] = "solved"
            else:
                questions[i]["status"] = "wrong answer"
            break
    print("Here done")
    update_doc = {
        "$set": {
            "coins": updated_coins,
            "questions": questions,
            "time_left": params.time_left,
        },
        "$push": {
            "questions_attempted": {
                "question_id": params.question_id,
                "solved": params.solved,
            }
        },
    }

    result = await db.Users.update_one({"user_id": params.user_id}, update_doc)
    print(result)
    return {"success": True, "message": message, "coins": updated_coins}
