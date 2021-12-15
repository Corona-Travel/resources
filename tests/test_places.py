import mongomock
import pymongo
from fastapi.testclient import TestClient

from places.app import app, get_settings, get_mongodb
from places.settings import Settings
import mongomock


client = TestClient(app)


# def override_get_settings():
    # return None


places = [
    {
    "name": "Moscow",
    "place_id": "moscow",
    "pos": { "type": "Point", "coordinates": [37.6203479, 55.7539765] },
    },
    {
    "name": "Madrid",
    "place_id": "madrid",
    "pos": { "type": "Point", "coordinates": [-3.70379, 40.416775] },
    },
]

collection = mongomock.MongoClient().db.collection

for obj in places:
    collection.insert_one(obj)
    del obj["_id"]  # for some reason it creates _id key on inserted dict


def override_get_mongodb():
    return collection


# app.dependency_overrides[get_settings] = override_get_settings
app.dependency_overrides[get_mongodb] = override_get_mongodb


def test_get_places():
    response = client.get("/paces")

    assert response.status_code == 200
    assert response.json() == [places[0]]

