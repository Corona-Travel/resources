from typing import Any, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from reusable_mongodb_connection.fastapi import get_collection

from .settings import Settings, get_settings
from .types import Quiz, QuizWithoutId, Quizzes

app = FastAPI(
    openapi_tags=[
        {
            "name": "resource:quizzes",
        }
    ]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_mongodb(settings: Settings = Depends(get_settings)):
    return get_collection(settings.mongo_url, "quizzes")


@app.get("/quizzes", response_model=Quizzes, tags=["resource:quiz"])
def get_quizzes(quiz_collection=Depends(get_mongodb)):

    quizzes = quiz_collection.find({})

    result = []
    for q in quizzes:
        try:
            result.append(
                Quiz(
                    quiz_id=q["quiz_id"],
                    name=q["name"],
                    pos=q["pos"]["coordinates"],
                    questions=q["questions"],
                )
            )
        except Exception as e:
            print(str(e))
    return result


@app.post("/quizzes", tags=["resource:quiz"], responses={400: {"description": "quiz ID occupied"}})
def add_quiz(quiz: Quiz, quiz_collection=Depends(get_mongodb)):
    check_quiz_id = quiz_collection.find_one({"quiz_id": quiz.quiz_id})

    if check_quiz_id is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="quiz ID occupied")

    coordinates = quiz.pos
    quiz.pos = {"type": "Point", "coordinates": coordinates}

    quiz_collection.insert_one(quiz.dict())


@app.get("/quizzes/{quiz_id}", response_model=Quiz, tags=["resource:quiz"], responses={404: {"description": "Quiz with specified ID was not found"}})
def get_quiz(quiz_id: str, quiz_collection=Depends(get_mongodb)):

    quiz = quiz_collection.find_one({"quiz_id": quiz_id})

    if quiz is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Quiz with specified id was not found"
        )

    return Quiz(
        quiz_id=quiz["quiz_id"],
        name=quiz["name"],
        pos=quiz["pos"]["coordinates"],
        questions=quiz["questions"],
    )


@app.put("/quizzes/{quiz_id}", response_model=Quiz, tags=["resource:quiz"], responses={404: {"description": "Quiz with specified ID was not found"}})
def update_quiz(
    quiz_id: str,
    quiz: QuizWithoutId,
    quiz_collection=Depends(get_mongodb),
):

    result = quiz_collection.update_one({"quiz_id": quiz_id}, {"$set": quiz.dict()})

    if not result.matched_count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Quiz with specified ID was not found"
        )

    new_quiz = quiz_collection.find_one({"quiz_id": quiz_id})
    return Quiz(
        quiz_id=new_quiz["quiz_id"],
        name=new_quiz["name"],
        pos=new_quiz["pos"],
        questions=new_quiz["questions"],
    )


@app.delete("/quizzes/{quiz_id}", tags=["resource:quiz"], responses={404: {"description": "Quiz with specified ID was not found"}})
def delete_quiz(quiz_id: str, quiz_collection=Depends(get_mongodb)):

    result = quiz_collection.deleta_one({"quiz_id": quiz_id})

    if not result.deleted_count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Quiz with specified ID was not found"
        )


@app.get(
    "/quizzes/near/{lng}/{lat}",
    response_model=Quizzes,
    tags=["resource:quiz"],
)
def get_nearest(
    lng: float,
    lat: float,
    max_dist: Optional[float] = 10000,
    quiz_collection=Depends(get_mongodb),
):
    nearest = quiz_collection.find(
        {
            "pos": {
                "$near": {
                    "$geometry": {"type": "Point", "coordinates": [lng, lat]},
                    "$maxDistance": max_dist,
                }
            }
        }
    )
    res = []
    for quiz in nearest:
        try:
            res.append(
                Quiz(
                    quiz_id=quiz["quiz_id"],
                    name=quiz["name"],
                    pos=quiz["pos"]["coordinates"],
                    questions=quiz["questions"],
                )
            )
        except Exception as e:
            print(str(e))
    return res
