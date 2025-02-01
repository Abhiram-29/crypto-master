from fastapi import FastAPI, APIRouter, Depends
from typing import Optional, List, Literal
from dotenv import load_dotenv
import json
import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient,AsyncIOMotorDatabase
from pymongo.server_api import ServerApi
from models import MCQ, MCQWithImage, FillInTheBlanks
import random
from datetime import datetime,timedelta
from pydantic import BaseModel,Field

class updateParameters(BaseModel):
    user_id : str
    question_id : int
    spent_amt : int
    winning_amt : int
    difficulty : str = Field(..., pattern="^(easy|medium|hard|jackpot)$")
    timestamp : datetime
    user_start_time : datetime
    solved : bool

app = FastAPI()

MONGO_URI = os.getenv("CONNECTION_STRING")
Game_Duration = 30 #in minutes
Winnings = {"easy": 0.20, "medium": 0.40, "hard": 0.80, "jackpot":2.00}

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

async def get_database():
    if MongoDB.db is None:
        await MongoDB.connect()
    return MongoDB.db


@app.on_event("startup")
async def startup_db():
    await MongoDB.connect()

@app.on_event("shutdown")
async def shutdown_db():
    await MongoDB.close()


def serialize_document(doc):
    """Convert MongoDB document to a JSON-serializable format."""
    doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
    return doc

@app.get("/questions/{user_id}")
async def sendQuestions(user_id: str,db: AsyncIOMotorDatabase = Depends(get_database)):
    questions = await db.Questions.find().to_list()
    print(questions)
    questions = [serialize_document(q) for q in questions]
    return random.sample(questions,min(len(questions),30))

@app.get("/")
async def greet():
    return "API is running"

@app.get("/login/{user_id}")
async def login(user_id,db: AsyncIOMotorDatabase = Depends(get_database)):
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
            "logged_in": "True"
        }},
        upsert=False
    )
        return {"success" : True,"message": "User loggedin for the first time"}
    else:
        if (datetime.utcnow()- start_time) < timedelta(minutes= Game_Duration):
            return {"success" : True, "message": "User logged in again"}
        else:
            return {"success":False,"message": "User has played the game"}


@app.post("/update")
async def updateScore(params: updateParameters, db : AsyncIOMotorDatabase = Depends(get_database)):
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

