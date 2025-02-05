from fastapi import FastAPI, APIRouter, Depends,  Security, HTTPException, Request
from fastapi.security.api_key import APIKeyHeader
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from typing import Optional, List, Literal
from dotenv import load_dotenv
import json
import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient,AsyncIOMotorDatabase
from pymongo.server_api import ServerApi
from models import *
import random
from datetime import datetime,timedelta
from pydantic import BaseModel,Field
from starlette.status import HTTP_403_FORBIDDEN
import logging
import bisect


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

API_KEY = os.getenv("API_KEY")
API_KEY_NAME = "API_KEY"
MONGO_URI = os.getenv("CONNECTION_STRING")
Game_Duration = 30 #in minutes
Winnings = {"easy": 0.20, "medium": 0.40, "hard": 0.80, "jackpot":2.00}


api_key_header = APIKeyHeader(name=API_KEY_NAME,auto_error= True)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded,_rate_limit_exceeded_handler)

LeaderBoard = []

async def verifyApiKey(api_key_header: str = Security(api_key_header)):

    if api_key_header is None:
        logger.warning("No API key provided.")
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="API key is required"
        )
    if api_key_header not in API_KEY:
        logger.warning(f"Invalid API key received: {api_key_header}")
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Invalid or missing API Key"
        )

    logger.info("API key verification successful")
    return api_key_header


class MongoDB:
    client: AsyncIOMotorClient = None
    db  = None

    @classmethod
    async def connect(cls):
        cls.client = AsyncIOMotorClient(MONGO_URI,maxPoolSize = 10, minPoolSize = 1)
        cls.db = cls.client['CryptoMaster']

    @classmethod
    async def close(cls):
        if cls.client:
            cls.client.close()

class LeaderBoard:
    leader_board = []

    @classmethod
    def initialize_leaderboard(cls,users):
        for user in users:
            cls.leader_board.append((user.get("coins"),user.get("user_id")))
        cls.leader_board.sort(key = lambda x : -x[0])
    
    @classmethod
    def update(cls, user_id, score):
        for i, entry in enumerate(cls.leader_board):
            if entry[1] == user_id:
                cls.leader_board.pop(i)
                break
        new_entry = (score, user_id)
        index = bisect.insort_right(cls.leader_board, new_entry, key=lambda x: -x[0])
        # cls.leader_board.insert(index, new_entry)

    @classmethod
    def showLeaderboard(cls):
        return leader_board


async def get_database():
    if MongoDB.db is None:
        await MongoDB.connect()
    return MongoDB.db


async def initialize_leaderboad():
    db = await get_database()
    users = await db.Users.find().to_list()
    LeaderBoard.initialize_leaderboard(users)

@app.on_event("startup")
async def startup_db():
    await MongoDB.connect()
    await initialize_leaderboad()

@app.on_event("shutdown")
async def shutdown_db():
    await MongoDB.close()


def serialize_document(doc):
    """Convert MongoDB document to a JSON-serializable format."""
    doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
    return doc

class UserRequest(BaseModel):
    user_id: str

@app.post("/questions")
@limiter.limit("20/second")
async def sendQuestions(
    request: Request,
    question_request = UserRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    api_key : str = Depends(verifyApiKey)
):

    easy_questions = await db.Easy.find().to_list()
    easy_questions = random.sample([serialize_document(q) for q in easy_questions],min(len(easy_questions),15))
    medium_questions = await db.Medium.find().to_list()
    medium_questions = random.sample([serialize_document(q) for q in medium_questions],min(len(medium_questions),15))
    hard_questions = await db.Hard.find().to_list()
    hard_questions = random.sample([serialize_document(q) for q in hard_questions],min(len(hard_questions),10))

    questions = [*easy_questions,*medium_questions,*hard_questions]
    return random.sample(questions,min(len(questions),30))

@app.get("/")
async def greet():
    return "API is running"

@app.post("/login")
@limiter.limit("20/second")
async def login(
    request : Request,
    login_request : UserRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    api_key : str = Depends(verifyApiKey)
):
    user_id = login_request.user_id
    user = await db.Users.find_one({"user_id" : user_id})
    if not user:
        return {"success" : False, "message":"User not found"}
    start_time = user.get("start_time")
    logged_in = user.get("logged_in")
    if logged_in == "False":
        await db.Users.update_one(
        {"user_id": user_id},
        {"$set": {
            "start_time": datetime.utcnow(),
            "logged_in": "True",
            "questions_solved" : []
        }},
        upsert=False
    )
        return {"success" : True,"message": "User loggedin for the first time", "name" : user.get("name"),"email_id":user.get("email_id"),"questions_solved" : user.get("questions_solved")}
    else:
        if (datetime.utcnow()- start_time) < timedelta(minutes= Game_Duration):
            return {"success" : True, "message": "User logged in again","name" : user.get("name"),"email_id":user.get("email_id"),"questions_solved" : user.get("questions_solved")}
        else:
            return {"success":False,"message": "User has played the game","name" : user.get("name"),"email_id":user.get("email_id"),"questions_solved" : user.get("questions_solved")}


@app.post("/update")
@limiter.limit("30/second")
#need to add tracking for the last question solved by user
async def updateScore(
    request : Request,
    params: updateParameters,
    db : AsyncIOMotorDatabase = Depends(get_database),
    api_key : str = Depends(verifyApiKey)
    ):
    '''
        {
            sucesss : True/False
            message : string
            coins : total number of coins (int)
        }
    '''
    user = await db.Users.find_one({"user_id" : params.user_id})

    if (params.timestamp - params.user_start_time) > timedelta(minutes= 30):
        return {
            "success" : False,
            "message" : "user submitted the question after the deadline",
            "coins" : user.get("coins")
        }
    print(params.solved)
    print(user.get("coins"))
    message = ""
    updated_coins = 0
    if params.solved != True:
        updated_coins = user.get("coins")-params.spent_amt
        message = f"the user lost {params.spent_amt} coins"
    else:
        updated_coins = user.get("coins") + params.spent_amt*(Winnings[params.difficulty])
        message = f"the user won {updated_coins - params.spent_amt} coins"
    print(updated_coins)
    await db.Users.update_one(
            {"user_id" : params.user_id},
            {"$set":{"coins": updated_coins} }
        )
    return {
            "success" : True,
            "message" : "user lost {params.spent_amt} coins",
            "coins" : updated_coins
        }


@app.get("/leaderboard")
@limiter.limit("5/minute")
async def displayLeaderboard(
    request: Request,
    api_key : str = Depends(verifyApiKey)
):
    if LeaderBoard.leader_board is None:
        await initialize_leaderboad()
    return LeaderBoard.leader_board


@app.post("/end")
@limiter.limit("30/second")
async def gameEnd(
    request : Request,
    params : endParameters,
    db : AsyncIOMotorDatabase = Depends(get_database),
    api_key : str  = Depends(verifyApiKey)
):
    user = await db.Users.find_one({"user_id" : params.user_id})
    LeaderBoard.update(params.user_id,user.get('coins'))
    await db.Users.update_one(
        {"user_id" : params.user_id},
        {"$set" : {"end_time" : datetime.utcnow() } }
    )

    return {"success" : True,"Final coin tally":user.get("coins")}
