from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Literal
from datetime import datetime

class BaseQuestion(BaseModel):
    question_id: int = Field(..., alias="_id")
    topic: str
    difficulty: str = Field(..., pattern="^(easy|medium|hard|jackpot)$")
    hint: Optional[str]
    question_type: str

class MCQ(BaseQuestion):
    question_type: Literal['mcq'] = 'mcq'
    question: str
    options: List[str] = Field(..., min_items=4, max_items=4)
    correct_ans: str

    @model_validator(mode='after')
    def validate_correct_answer(self) -> 'MCQ':
        if self.correct_ans not in self.options:
            raise ValueError("correct_ans must be one of the provided options")
        return self

class FillInTheBlanks(BaseQuestion):
    question_type: Literal['fib'] = 'fib'
    question: str
    correct_ans: str

class MCQWithImage(BaseQuestion):
    question_type: Literal['mcq_image'] = 'mcq_image'
    question: str
    options: List[str] = Field(..., min_items=4, max_items=4)
    correct_ans: int = Field(..., gt=0, lt=5)

class Wordle(BaseQuestion):
    question_type: Literal['wordle'] = 'wordle'
    word: str = Field(..., min_length=4, max_length=5)


class updateParameters(BaseModel):
    user_id : str
    question_id : int
    spent_amt : float
    multiplier : float
    time_left : float
    solved : bool

class endParameters(BaseModel):
    user_id : str
    end_time : datetime
    coins : float

class UserRequest(BaseModel):
    user_id: str

class startParameters(BaseModel):
    user_id : str
    question_id : int
    bet_amt : float
    time_left : float

class auctionParameters(BaseModel):
    user_id : str
    jackpot_question_id : float
    jackpot_cost : float

class createParams(BaseModel):
    user_id : str
    name : str
    email_id : str

class timeParams(BaseModel):
    user_id : str
    time_left : float

class coinParams(BaseModel):
    user_id : str
    coins : float