from typing import NamedTuple
from pydantic import BaseModel


class Position(NamedTuple):
    lat: float
    lng: float


class OptionWithoutAnswer(BaseModel):
    option: str


class OptionWithAnswer(OptionWithoutAnswer):
    correct: bool


class QuestionWithoutAnswer(BaseModel):
    task: str
    answers: list[OptionWithoutAnswer]


class QuestionWithAnswer(BaseModel):
    task: str
    answers: list[OptionWithAnswer]


class QuizWithoutAnswerWithoutId(BaseModel):
    name: str
    pos: Position
    questions: list[QuestionWithoutAnswer]


class QuizWithoutAnswer(QuizWithoutAnswerWithoutId):
    quiz_id: str


class QuizWithAnswerWithoutId(BaseModel):
    name: str
    pos: Position
    questions: list[QuestionWithAnswer]


class QuizWithAnswer(QuizWithAnswerWithoutId):
    quiz_id: str


Quizes = list[QuizWithAnswer]

QuizesWithoutAnswer = list[QuizWithAnswer]
