import mongomock
import pymongo
from fastapi.testclient import TestClient

from quizzes.app import app, get_settings, get_mongodb
from quizzes.settings import Settings
import mongomock


client = TestClient(app)


# def override_get_settings():
    # return None


quizzes = [
 {
  "quiz_id": "mscw_c",
  "name": "Moscow center",
  "questions": [
    {
      "question":
        "When  was the beginning of the period of the new heyday of the Red Square?",
      "answers": [
        { "option": "12th century", "correct": False },
        { "option": "19th century", "correct": True },
        { "option": "20th century", "correct": False },
      ],
    },
    {
      "question": "When was Lenin's Mausoleum at Red Square opened?",
      "answers": [
        { "option": "it is not a Mausoleum", "correct": False },
        { "option": "1930", "correct": True },
        { "option": "1941", "correct": False },
      ],
    },
    {
      "question": "What is GUM famous for among the tourists?",
      "answers": [
        { "option": "clothes", "correct": False },
        { "option": "height of the building", "correct": False },
        { "option": "ice cream", "correct": True },
      ],
    },
    {
      "question": "What kind of sport could you do right on the Red Square?",
      "answers": [
        { "option": "ice skating", "correct": True },
        { "option": "golfing", "correct": False },
        { "option": "swimming", "correct": False },
      ],
    },
    {
      "question": "What happened on Nikolsakaya street in summer 2018?",
      "answers": [
        { "option": "massive football fans' festivities", "correct": True },
        { "option": "meeting of all presidents", "correct": False },
        { "option": "carnival", "correct": False },
      ],
    },
  ],
  "pos": { "type": "Point", "coordinates": [37.620795, 55.7539303] },
}
]

collection = mongomock.MongoClient().db.collection

for obj in quizzes:
    collection.insert_one(obj)
    del obj["_id"]  # for some reason it creates _id key on inserted dict


def override_get_mongodb():
    return collection


# app.dependency_overrides[get_settings] = override_get_settings
app.dependency_overrides[get_mongodb] = override_get_mongodb


def test_get_quizzes():
    response = client.get("/quizzes")

    assert response.status_code == 200
    assert response.json() == [quizzes[0]]

