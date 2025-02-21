# api/routers/questions.py
from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from ..dependencies import get_database
from models import UserRequest
from core.utils import serialize_document
from motor.motor_asyncio import AsyncIOMotorDatabase
import random
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("/questions")
@limiter.limit("20/second")
async def send_questions(
    request: Request,
    question_request: UserRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    user_id = question_request.user_id
    user = await db.Users.find_one({"user_id": user_id})
    if not user:
        return {"success": "False", "message": "User not found"}

    question_status = user.get("questions_generated")
    if question_status == "false":
        question_status = False
    logger.info(question_status)
    if question_status:
        return {
            "success": "True",
            "message": "questions retrieved successfully",
            "questions": user.get("questions"),
        }
    else:
        easy_questions = await db.Easy.find().to_list(length=None)
        easy_questions = random.sample(
            [serialize_document(q) for q in easy_questions], min(len(easy_questions), 10)
        )  # 10 Easy

        medium_questions = await db.Medium.find().to_list(length=None)
        medium_questions = random.sample(
            [serialize_document(q) for q in medium_questions], min(len(medium_questions), 8)
        )  # 8 Medium

        hard_questions = await db.Hard.find().to_list(length=None)
        hard_questions = random.sample(
            [serialize_document(q) for q in hard_questions], min(len(hard_questions), 5)
        )  # 5 Hard

        all_questions = easy_questions + medium_questions + hard_questions

        for question in all_questions:
            question["status"] = "locked"
            question["multiplier"] = 1.5
            question["minimum_spend"] = 30

        result = await db.Users.update_one(
            {"user_id": user_id},
            {"$set": {"questions_generated": True, "questions": all_questions}},
        )

        return {
            "success": True,
            "message": "Questions generated successfully",
            "questions": all_questions,
        }