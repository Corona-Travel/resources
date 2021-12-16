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
        "pos": { "type": "Point", "coordinates": [37.620302, 55.754131] },
    },
    {
        "name": "Christ the Saviour Cathedral",
        "description": "The most important and the largest cathedral in Russia",
        "fact_id": "moscow_chr_sav_cath",
        "pos": { "type": "Point", "coordinates": [37.6054939, 55.7446375] },
    },
]


json_facts = []
for fact in facts:
    fact["pos"] = fact["pos"]["coordinates"]
    json_facts.append(fact)


new_fact = {
    "name": "City Hill",
    "description": "City Hill is a five hectare landscaped hill located in the centre of Canberra and surrounded by Vernon Circle",
    "fact_id": "city_hill_Canberra",
    "pos": { "type": "Point", "coordinates": [149.12383, -35.27583] }
}


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
    assert response.json() == json_facts


def test_get_fact_by_id():
    for fact in facts:
        response = client.get(f"/facts/{fact['fact_id']}")

        assert response.status_code == 200
        assert response.json() == json_facts


def test_post_fact():
    response = client.post(
        "/facts",
        json=new_fact,
    )
    assert response.status_code == 200
    assert response.json() == None

    response = client.get(f"/facts/{new_fact['fact_id']}")
    assert response.status_code == 200
    assert response.json() == new_fact


def test_post_duplicat_fact():
    response = client.post(
        "/facts",
        json=facts[0],
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "fact ID occupied"}

