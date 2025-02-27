# api/routers/questions.py
from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from ..dependencies import get_database
from models import createParams, UserRequest
from core.utils import serialize_document
from motor.motor_asyncio import AsyncIOMotorDatabase
import random
import logging


logger = logging.getLogger(__name__)
router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.post("/user_reset")
def userReset(
    request : Request,
    params : UserRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    db.Users.update_one(
        {"user_id" : params.user_id},
        {"$set" : {
            "coins" : 500,
            "logged_in" : False,
            "questions_generated" : False
        } }
    )
    return {"success" : True, "message" : "User reset successfully"}

@router.post("/user_create")
def createUser(
    request: Request,
    params : createParams,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    db.Users.insert_one({
        "user_id": params.user_id,
        "name": params.name,
        "email_id": params.email_id,
        "start_time": {"$date": {"$numberLong": "1738848640720"}},
        "end_time": {"$date": {"$numberLong": "1738496201292"}},
        "logged_in": "False",
        "coins": {"$numberDouble": "1248.0"},
        "correct_answers": {"$numberInt": "0"},
        "wrong_answers": {"$numberInt": "0"},
        "questions": [],
        "questions_generated": False
    })
    return {"success" : True, "message" : "User created successfully"}