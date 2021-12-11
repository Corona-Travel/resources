from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Depends
from reusable_mongodb_connection import get_db
from reusable_mongodb_connection.fastapi import get_collection
from bson.son import SON

from .types import (
    Quiz,
    Quizzes,
    QuizWithoutId,
)
from .settings import Settings, get_settings

app = FastAPI(
    openapi_tags=[
        {
            "name": "resource:quiz",
        }
    ]
)


@app.get("/quizzes", response_model=Quizzes, tags=["resource:quiz"])
def get_quizzes(settings: Settings = Depends(get_settings)):
    quiz_collection = get_collection(settings.mongo_url, "quizzes")

    quizzes = quiz_collection.find({})

    result = []
    for q in quizzes:
        try:
            result.append(Quiz(**q))
        except Exception as e:
            print(str(e))
    return result


@app.post("/quizzes", tags=["resource:quiz"])
def add_quiz(quiz: Quiz, settings: Settings = Depends(get_settings)):
    quiz_collection = get_collection(settings.mongo_url, "quizzes")
    check_quiz_id = quiz_collection.find_one({})

    if check_quiz_id is not None:
        raise HTTPException(status_code=400, detail="quiz ID occupied")

    quiz_collection.insert_one(quiz.dict())


@app.get("/quizzes/{quiz_id}", response_model=Quiz, tags=["resource:quiz"])
def get_quiz(quiz_id: str, settings: Settings = Depends(get_settings)):
    quiz_collection = get_collection(settings.mongo_url, "quizzes")

    quiz = quiz_collection.find_one({"quiz_id": quiz_id})

    if quiz is None:
        raise HTTPException(
            status_code=404, detail="Quiz with specified id was not found"
        )

    return Quiz(**quiz)


@app.put("/quizzes/{quiz_id}", response_model=Quiz, tags=["resource:quiz"])
def update_quiz(
    quiz_id: str,
    quiz: QuizWithoutId,
    settings: Settings = Depends(get_settings),
):
    quiz_collection = get_collection(settings.mongo_url, "quizzes")

    result = quiz_collection.update_one({"quiz_id": quiz_id}, {"$set": quiz.dict()})

    if not result.matched_count:
        raise HTTPException(
            status_code=404, detail="Place with specified ID was not found"
        )

    new_quiz = quiz_collection.find_one({"quiz_id": quiz_id})
    return Quiz(**new_quiz)


@app.delete("/quizzes/{quiz_id}", tags=["resource:quiz"])
def delete_quiz(quiz_id: str, settings: Settings = Depends(get_settings)):
    quiz_collection = get_collection(settings.mongo_url, "quizzes")

    result = quiz_collection.deleta_one({"quiz_id": quiz_id})

    if not result.deleted_count:
        raise HTTPException(
            status_code=404, detail="Quiz with specified ID was not found"
        )


@app.get(
    "/quizzes/near/{lng}/{lat}",
    response_model=Quizzes,
    tags=["resource:quiz"],
)
def get_nearest(
    lng: float,
    lat: float,
    max_dist: Optional[float] = 100,
    settings: Settings = Depends(get_settings),
):
    quiz_collection = get_collection(settings.mongo_url, "quizzes")
    nearest = quiz_collection.find(
        {"pos": SON([("$near", [lng, lat]), ("$maxDistance", max_dist)])}
    ).limit(3)
    res = []
    for quiz in nearest:
        try:
            res.append(Quiz(**quiz))
        except Exception as e:
            print(str(e))
    return res
