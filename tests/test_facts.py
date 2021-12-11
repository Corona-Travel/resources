import mongomock
import pymongo
from fastapi.testclient import TestClient

from facts.app import app, get_settings, get_mongodb
from facts.settings import Settings
import mongomock


client = TestClient(app)


def override_get_settings():
    return None


objects = [
    {
        "name": "Req Square",
        "description": "Red Square was built in 16-th century",
        "fact_id": "moscow_red_sqr",
        "pos": [55.7446371, 37.5967391],
    },
]


def override_get_mongodb():
    collection = mongomock.MongoClient().db.collection

    for obj in objects:
        collection.insert_one(obj)
        del obj["_id"]

    return collection


app.dependency_overrides[get_settings] = override_get_settings
app.dependency_overrides[get_mongodb] = override_get_mongodb



def test_get_facts():
    response = client.get("/facts")

    assert response.status_code == 200
    assert response.json() == objects
