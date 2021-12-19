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
    "typo": "photo",
    "pos": { "type": "Point", "coordinates": [37.6215216, 55.7546967] },
    "url": "https://www.google.com/url?sa=i&url=https%3A%2F%2Fgum.ru%2Fnews%2F7721635%2F15.06.2020%2F&psig=AOvVaw2Ezg_5YJ2dweQbZgzdHVHW&ust=1639402989493000&source=images&cd=vfe&ved=0CAsQjRxqFwoTCJDYh5qy3vQCFQAAAAAdAAAAABAD",
  },
  {
    "media_id": "gostinyy_dvor",
    "name": "Gostinnyy Dvor",
    "type": "photo",
    "pos": { "type": "Point", "coordinates": [37.623925, 55.754277] },
    "url": "http://www.robertodemicheli.com/album_test/index.html?folder=Architecture/&file=IMG_2060.jpg",
  },
  {
    "media_id": "GUM_sound",
    "name": "GUM people",
    "type": "audio",
    "pos": { "type": "Point", "coordinates": [-37.6225106, -55.753579] },
    "url": "https://cdn.pixabay.com/download/audio/2021/11/25/audio_91b32e02f9.mp3?filename=jazzy-abstract-beat-11254.mp3",
  },
]

collection = mongomock.MongoClient().db.collection

for obj in media:
    collection.insert_one(obj)
    del obj["_id"]  # for some reason it creates _id key on inserted dict
    coordinates = obj["pos"]["coordinates"]
    obj["pos"] = coordinates


def override_get_mongodb():
    return collection


# app.dependency_overrides[get_settings] = override_get_settings
app.dependency_overrides[get_mongodb] = override_get_mongodb


def test_get_media():
    response = client.get("/media")

    assert response.status_code == 200
    assert response.json() == [media[0], media[2], media[3]]

def test_get_one_media():
    response = client.get("/media/red_sq_photo")
    assert response.status_code == 200
    assert response.json() == media[0]

def test_get_non_exist_media():
    response = client.get("/media/ksf")
    assert response.status_code == 404

def test_post_media():
    item = {
        "media_id": "lobn_video",
        "name": "Lobnoe mesto",
        "type": "video",
        "pos": [37.6225886, 55.7532491],
        "url": "https://media.istockphoto.com/videos/victory-day-decoration-on-the-red-square-moscow-russia-video-id644998210",
    }
    response = client.post("/media", json=item)
    assert response.status_code == 200
    response = client.get("/media/lobn_video")
    assert response.status_code == 200
    assert response.json() == item

def test_post_incorrect_media():
    item = {
        "media_id": "lobn_video",
        "name": "Lobnoe mesto",
        "type": "video",
        "pos": { "type": "Point", "coordinates": [37.6225886, 55.7532491] },
        "url": "https://media.istockphoto.com/videos/victory-day-decoration-on-the-red-square-moscow-russia-video-id644998210",
    }
    response = client.post("/media", json=item)
    assert response.status_code == 422

def test_delete_media():
    response = client.delete("/media/gostinyy_dvor")
    assert response.status_code == 200
    response = client.get("/media/gostinyy_dvor")
    assert response.status_code == 404

def test_delete_non_existing_media():
    response = client.delete("/media/ghjshd")
    assert response.status_code == 404

def test_put_media():
    expected_media = {
        "name": "Red Square",
        "type": "photo",
        "pos": [37.5967391, 55.7446371],
        "url": "new_url",
    }
    response = client.put("/media/red_sq_photo", json=expected_media)
    assert response.status_code == 200
    expected_media["media_id"] = "red_sq_photo"
    response = client.get("/media/red_sq_photo")
    assert response.status_code == 200
    assert response.json() == expected_media

def test_put_incorrect_media():
    incorrect_media = {
        "media_id": "jdh",
        "name": "Red Square",
        "typo": "photo",
        "pos": [37.5967391, 55.7446371],
        "url": "new_url",
    }
    response = client.put("/media/red_sq_photo", json=incorrect_media)
    assert response.status_code == 422

def test_put_non_existing_media():
    incorrect_media = {
        "name": "Red Square",
        "type": "photo",
        "pos": [37.5967391, 55.7446371],
        "url": "new_url",
    }
    response = client.put("/media/not_ex", json=incorrect_media)
    assert response.status_code == 404
