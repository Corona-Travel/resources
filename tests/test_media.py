import mongomock
import pymongo
from fastapi.testclient import TestClient

from media.app import app, get_settings, get_mongodb
from media.settings import Settings
import mongomock


client = TestClient(app)


# def override_get_settings():
    # return None


media = [
 {
    "media_id": "red_sq_photo",
    "name": "Red Square",
    "type": "photo",
    "pos": { "type": "Point", "coordinates": [37.5967391, 55.7446371] },
    "url": "https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.lonelyplanet.com%2Farticles%2Fmoscow-e2-80-99s-red-square&psig=AOvVaw0mznzK4RolAkwM1p7E5cE_&ust=1639402766684000&source=images&cd=vfe&ved=0CAsQjRxqFwoTCOii77Cx3vQCFQAAAAAdAAAAABAS",
  },
  {
    "media_id": "gum_photo",
    "name": "GUM",
    "type": "photo",
    "pos": { "type": "Point", "coordinates": [37.6215216, 55.7546967] },
    "url": "https://www.google.com/url?sa=i&url=https%3A%2F%2Fgum.ru%2Fnews%2F7721635%2F15.06.2020%2F&psig=AOvVaw2Ezg_5YJ2dweQbZgzdHVHW&ust=1639402989493000&source=images&cd=vfe&ved=0CAsQjRxqFwoTCJDYh5qy3vQCFQAAAAAdAAAAABAD",
  }
]

collection = mongomock.MongoClient().db.collection

for obj in media:
    collection.insert_one(obj)
    del obj["_id"]  # for some reason it creates _id key on inserted dict


def override_get_mongodb():
    return collection


# app.dependency_overrides[get_settings] = override_get_settings
app.dependency_overrides[get_mongodb] = override_get_mongodb


def test_get_media():
    response = client.get("/media")

    assert response.status_code == 200
    assert response.json() == [media[0]]
