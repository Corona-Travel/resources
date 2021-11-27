from typing import List
from pydantic import BaseModel

class OptionWithoutAnswer(BaseModel):
    option: str

class OptionWithAnswer(OptionWithoutAnswer):
    correct: bool

class QuestionWithoutAnswer(BaseModel):
    task: str
    answers: List[OptionWithoutAnswer]

class QuestionWithAnswer(BaseModel):
    task: str
    answers: List[OptionWithAnswer]

class QuizWithoutAnswerWithoutId(BaseModel):
    name: str
    questions: List[QuestionWithoutAnswer]

class QuizWithoutAnswer(QuizWithoutAnswerWithoutId):
    quiz_id: str

class QuizWithAnswerWithoutId(BaseModel):
    name: str
    questions: List[QuestionWithAnswer]

class QuizWithAnswer(QuizWithAnswerWithoutId):
    quiz_id: str
