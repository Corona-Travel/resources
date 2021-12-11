import mongomock
import pymongo
from fastapi.testclient import TestClient

from facts.app import app, get_settings, get_mongodb
from facts.settings import Settings
import mongomock


client = TestClient(app)


# def override_get_settings():
    # return None


facts = [
    {
        "name": "Req Square",
        "description": "Red Square was built in 16-th century",
        "fact_id": "moscow_red_sqr",
        "pos": [55.7446371, 37.5967391],
    },
    {
        "name": "Req Square",
        "description": "Red Square was built in 16-th century",
        "fact_id": "moscow_red_sqr",
        "pas": [55.7446371, 37.5967391],
    },
]

collection = mongomock.MongoClient().db.collection

for obj in facts:
    collection.insert_one(obj)
    del obj["_id"]  # for some reason it creates _id key on inserted dict


def override_get_mongodb():
    return collection


# app.dependency_overrides[get_settings] = override_get_settings
app.dependency_overrides[get_mongodb] = override_get_mongodb


def test_get_facts():
    response = client.get("/facts")

    assert response.status_code == 200
    assert response.json() == [facts[0]]


# def test_get_facts_by_id():
#     for fact in facts:
#         response = client.get(f"/facts/{fact['fact_id']}")

#         assert response.status_code == 200
#         assert response.json() == fact
