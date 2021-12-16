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


new_place = {
    "name": "Vienna",
    "place_id": "vien",
    "pos": [16.311865, 48.184517],
}


collection = mongomock.MongoClient().db.collection

for obj in places:
    collection.insert_one(obj)
    del obj["_id"]  # for some reason it creates _id key on inserted dict
    obj['pos'] = obj['pos']['coordinates']


def override_get_mongodb():
    return collection


# app.dependency_overrides[get_settings] = override_get_settings
app.dependency_overrides[get_mongodb] = override_get_mongodb


def test_get_places():
    response = client.get("/places")

    assert response.status_code == 200
    assert response.json() == places


def test_get_place_by_id():
    for place in places:
        response = client.get(f"/places/{place['place_id']}")

        assert response.status_code == 200
        assert response.json() == place


def test_post_place():
    response = client.post(
        "/places",
        json=new_place,
    )
    assert response.status_code == 200
    assert response.json() == None

    response = client.get(f"/places/{new_place['place_id']}")
    assert response.status_code == 200
    assert response.json() == new_place


def test_post_duplicat_place():
    response = client.post(
        "/places",
        json=places[0],
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "place ID occupied"}


def test_patch_place():
    response = client.patch(
        f"/places/{places[0]['place_id']}?name={new_place['name']}"
    )
    assert response.status_code == 200
    copy = places[0].copy()
    copy['name'] = new_place['name']
    assert response.json() == copy


def test_patch_no_changes_place():
    response = client.patch(
        f"/places/{places[0]['place_id']}?name={new_place['name']}"
    )
    assert response.status_code == 409
    assert response.json() == {"detail": "No new parameters were supplied"}


def test_put_place():
    copy = new_place.copy()
    del copy['place_id']
    response = client.put(
        f"/places/{places[0]['place_id']}",
        json=copy
    )
    copy = new_place.copy()
    copy['place_id'] = places[0]['place_id']
    assert response.status_code == 200
    assert response.json() == copy


def test_put_non_existing_place():
    copy = new_place.copy()
    del copy['place_id']
    response = client.put(
        f"/places/12",
        json=copy
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Place with specified ID was not found"}


def test_delete_place():
    response = client.delete(
        f"/places/{places[0]['place_id']}",
    )
    assert response.status_code == 200
    assert response.json() == None