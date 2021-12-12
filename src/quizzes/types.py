from typing import NamedTuple
from pydantic import BaseModel


class Coordinates(NamedTuple):
    lng: float
    lat: float

class Position(BaseModel):
    type: str
    coordinates: Coordinates

class Answer(BaseModel):
    option: str
    correct: bool


class Question(BaseModel):
    question: str
    answers: list[Answer]


class QuizWithoutId(BaseModel):
    name: str
    pos: Position
    questions: list[Question]


class Quiz(QuizWithoutId):
    quiz_id: str


Quizzes = list[Quiz]
