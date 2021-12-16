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
    coordinates = obj["pos"]["coordinates"]
    obj["pos"] = coordinates


def override_get_mongodb():
    return collection


# app.dependency_overrides[get_settings] = override_get_settings
app.dependency_overrides[get_mongodb] = override_get_mongodb


def test_get_quizzes():
    response = client.get("/quizzes")

    assert response.status_code == 200
    assert response.json() == [quizzes[0]]

def test_get_one_quizzes():
    response = client.get("/quizzes/mscw_c")
    assert response.status_code == 200
    assert response.json() == quizzes[0]

def test_get_non_exist_quizzes():
    response = client.get("/quizzes/mscw_f")
    assert response.status_code == 404

def test_post_quizzes():
    item = {
  "quiz_id": "mscw_h",
  "name": "Moscow history",
  "questions": [
    {
      "question": "When were the first written mentions about Moscow made?",
      "answers": [
        { "option": "In the XI century", "correct": False },
        { "option": "In the XII century", "correct": True },
        { "option": "In the XV century", "correct": False },
      ],
    },
    {
      "question": "When did Moscow become the capital of Russia?",
      "answers": [
        { "option": "In 1200", "correct": False },
        { "option": "In 1340", "correct": True },
        { "option": "In 1147", "correct": False },
      ],
    },
    {
      "question": "When did Moscow become the capital of the Soviet state?",
      "answers": [
        { "option": "1931", "correct": False },
        { "option": "1925", "correct": False },
        { "option": "1922", "correct": True },
      ],
    },
    {
      "question":
        "The only sculptured monument on the square is a bronze statue of:",
      "answers": [
        { "option": "Kuzma Minin and Dmitry Pozharsky", "correct": True },
        { "option": "Tsar Nicholas and Empress Alexandra", "correct": False },
        { "option": "Ivan III", "correct": False },
      ],
    },
    {
      "question": "When did Moscow host the summer Olympic games?",
      "answers": [
        { "option": "In 1980", "correct": True },
        { "option": "In 1978", "correct": False },
        { "option": "In 1970", "correct": False },
      ],
    },
  ],
  "pos": [37.619556, 55.754496],
    }
    response = client.post("/quizzes", json=item)
    assert response.status_code == 200
    response = client.get("/quizzes/mscw_h")
    assert response.status_code == 200
    assert response.json() == item

def test_post_in_correct_quizzes():
    item = {
        "quiz_id": "mscw_h",
  "name": "Moscow history",
  "questions": [
    {
      "question": "When were the first written mentions about Moscow made?",
      "answers": [
        { "option": "In the XI century", "correct": False },
        { "option": "In the XII century", "correct": True },
        { "option": "In the XV century", "correct": False },
      ],
    },
    {
      "question": "When did Moscow become the capital of Russia?",
      "answers": [
        { "option": "In 1200", "correct": False },
        { "option": "In 1340", "correct": True },
        { "option": "In 1147", "correct": False },
      ],
    },
    {
      "question": "When did Moscow become the capital of the Soviet state?",
      "answers": [
        { "option": "1931", "correct": False },
        { "option": "1925", "correct": False },
        { "option": "1922", "correct": True },
      ],
    },
    {
      "question":
        "The only sculptured monument on the square is a bronze statue of:",
      "answers": [
        { "option": "Kuzma Minin and Dmitry Pozharsky", "correct": True },
        { "option": "Tsar Nicholas and Empress Alexandra", "correct": False },
        { "option": "Ivan III", "correct": False },
      ],
    },
    {
      "question": "When did Moscow host the summer Olympic games?",
      "answers": [
        { "option": "In 1980", "correct": True },
        { "option": "In 1978", "correct": False },
        { "option": "In 1970", "correct": False },
      ],
    },
  ],
  "pos": { "type": "Point", "coordinates": [37.620795, 55.7539303] },
    }
    response = client.post("/quizzes", json=item)
    assert response.status_code == 422

def test_delete_quizzes():
    response = client.delete("/quizzes/mscw_h")
    assert response.status_code == 200
    response = client.get("/quizzes/mscw_c")
    assert response.status_code == 404