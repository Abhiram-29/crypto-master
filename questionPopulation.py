from dotenv import load_dotenv
import os
from pymongo import MongoClient
from pydantic import BaseModel,Field,field_validator
from typing import Optional,List


class BaseQuestion(BaseModel):
    question_id : int = Field(...,alias="_id")
    topic : str
    difficulty : str = Field(..., pattern="^(easy|medium|hard|jackpot)$")
    hint : Optional[str]
    question_type : str

class MCQ(BaseModel):
    question_type: Literal['mcq'] = 'mcq'
    question: str
    options: List[str] = Field(..., min_items=4, max_items=4)
    correct_ans: str

    @field_validator("correct_ans", mode="after")
    @classmethod
    def is_correct(cls, value: str, values: dict) -> str:
        options = values.get("options", [])
        if value not in options:
            raise ValueError("correct_ans must be one of the provided options")
        return value

class FillInTheBlanks(BaseModel):
    question_type: Literal['fib'] = 'fib'
    question : str
    correct_ans : str


class MCQWithImage(BaseQuestion):
    question_type : Literal['mcq_image'] =  'mcq_image'
    question : str
    options : List[str] = Field(...,min_items = 4,max_items = 4)
    correct_ans : int = Field(...,gt=0,lt=5)

class Wordle(BaseQuestion):
    question_type : Literal['wordle'] = 'wordle'
    word : str = Field(...,min_length = 5, max_length = 5)






# load_dotenv()
# conn_uri = os.getenv("CONNECTION_STRING")

# client = MongoClient(conn_uri)

# try:
#     database = client.get_database("CryptoMaster")
#     print("HELLO")
# except Exception as e:
#     print(e)