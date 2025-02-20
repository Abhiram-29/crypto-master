from fastapi import FastAPI, APIRouter, Depends,  Security, HTTPException, Request
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

class startParameters(BaseModel):
    user_id : str
    question_id : int
    bet_amt : int

@app.post("/questions")
@limiter.limit("20/second")
async def sendQuestions(
    request: Request,
    question_request : UserRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    api_key : str = Depends(verifyApiKey)
):
    user_id  = question_request.user_id
    user = await db.Users.find_one({"user_id" : user_id})
    if not user:
        return {"success":"False","message":"User not found"}
    
    question_status = user.get("questions_generated")
    if question_status == "false": question_status = False
    print(question_status)
    if question_status:
        return {"success":"True","message":"questions retrieved successfully","questions":user.get("questions")}
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
            {"user_id":user_id},
            {"$set":{
                "questions_generated":True,
                "questions":all_questions
            }  }
        )

        return {"success":True,"message":"Questions generated successfully","questions":all_questions}

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
    success = True
    message = ""
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
            "questions_attempted" : []
        }},
        upsert=True
    )
        message = "User loggedin for the first time"
    else:
        if (datetime.utcnow()- start_time) < timedelta(minutes= Game_Duration):
            message = "User logged in again"
        else:
            message = "User has played the game"
            success = False
    return {"success": success,"message": message,"user_id":user_id, "name": user.get("name"),"email_id":user.get("email_id"),"coins":user.get("coins"),"time_left": 1500,"questions_attempted": user.get("questions_attempted")}

@app.post("/update")
@limiter.limit("30/second")
#need to add tracking for the last question solved by user
async def updateScore(
    request : Request,
    params: updateParameters,
    db : AsyncIOMotorDatabase = Depends(get_database),
    api_key : str = Depends(verifyApiKey)
    ):
    user = await db.Users.find_one({"user_id" : params.user_id})

    if (params.timestamp - params.user_start_time) > timedelta(minutes= 30):
        return {
            "success" : False,
            "message" : "user submitted the question after the deadline",
            "coins" : user.get("coins")
        }
    message = ""
    updated_coins = 0
    if params.solved != True:
        print(params.solved)
        updated_coins = user.get("coins")-params.spent_amt
        message = f"the user lost {params.spent_amt} coins"
    else:
        updated_coins = user.get("coins") + params.spent_amt*(Winnings[params.difficulty])
        message = f"the user won {updated_coins - params.spent_amt} coins"
    print(updated_coins)
    questions = user.get("questions")
    print(params.question_id)
    idx = -1
    for i in range(len(questions)):
        if questions[i].get("question_id")  == params.question_id:
            print("question found")
            print(params.solved == True)
            idx = i
            if params.solved:
                questions[i]["status"] = "solved"
            else:
                questions[i]['status'] = "wrong answer"
            break
    print(idx)
    print(questions[idx])
    update_doc = {
        "$set": {"coins": updated_coins,"questions":questions},
        "$push": {"questions_attempted": {"question_id": params.question_id, "solved": params.solved}}
    }

    result = await db.Users.update_one({"user_id": params.user_id}, update_doc)
    print(result)
    return {
            "success" : True,
            "message" : message,
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


@app.post("/questionStart")
@limiter.limit("30/second")
async def questionStart(
    request : Request,
    params : startParameters,
    db : AsyncIOMotorDatabase = Depends(get_database),
    api_key : str = Depends(verifyApiKey)
):
    user = await db.Users.find_one({"user_id" : params.user_id})
    questions = user.get("questions")
    coins = user.get("coins")
    updated_coins = coins - params.bet_amt
    if updated_coins < 0:
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
            "questions" : questions
        } }
    )

    return {"success":True,"message":"user state updated","question_id":params.question_id,"updated_coins":updated_coins}