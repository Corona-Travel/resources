from logging import getLogger
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, Query
from reusable_mongodb_connection.fastapi import get_collection
from pymongo import  GEO2D
from bson.son import SON

from .types import Fact, FactWithoutId, Facts, Position
from .settings import Settings, get_settings

app = FastAPI(openapi_tags=[{"name": "resource:facts"}])

logger = getLogger("facts")
logger.setLevel(get_settings().log_level)


@app.get("/facts", response_model=Facts, tags=["resource:facts"])
def get_facts(settings: Settings = Depends(get_settings)):
    facts_collection = get_collection(settings.mongo_url, "facts")
    facts = facts_collection.find({})

    logger.debug("getting facts: %s", facts)

    res = []
    for f in facts:
        try:
            res.append(Fact(**f))
        except Exception as e:
            print(str(e))
    return res


@app.post("/facts", tags=["resource:facts"])
def post_fact(fact: Fact, settings: Settings = Depends(get_settings)):
    facts_collection = get_collection(settings.mongo_url, "facts")

    fact_with_same_id = facts_collection.find_one({"fact_id": fact.fact_id})

    if fact_with_same_id is not None:
        raise HTTPException(status_code=400, detail="fact ID occupied")

    facts_collection.insert_one(fact.dict())


@app.get("/facts/{fact_id}", response_model=Fact, tags=["resource:facts"])
def get_fact_by_id(fact_id: str, settings: Settings = Depends(get_settings)):
    facts_collection = get_collection(settings.mongo_url, "facts")

    fact = facts_collection.find_one({"fact_id": fact_id})

    if fact is None:
        raise HTTPException(
            status_code=404, detail="Fact with specified id was not found"
        )
    return Fact(**fact)


@app.patch("/facts/{fact_id}", response_model=Fact, tags=["resource:facts"])
def patch_fact(
    fact_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    settings: Settings = Depends(get_settings),
):
    if (name is not None) or (description is not None) or (lat is not None) or (lng is not None):
        raise HTTPException(status_code=409, detail="No new parameters were supplied")

    facts_collection = get_collection(settings.mongo_url, "facts")
    old_fact_pos = facts_collection.find_one({"fact_id": fact_id})["pos"]

    new_fact_dict = {}
    if name is not None:
        new_fact_dict["name"] = name
    if description is not None:
        new_fact_dict["description"] = description
    if (lat is not None) or (lng is not None):
        new_pos = list(old_fact_pos)
        if lat is not None:
            new_pos[0] = lng
        if lng is not None:
            new_pos[1] = lat
        new_fact_dict["pos"] = tuple(new_pos)

    result = facts_collection.update_one({"fact_id": fact_id}, {"$set": new_fact_dict})

    if result.matched_count != 1:
        raise HTTPException(
            status_code=404, detail="Fact with specified id was not found"
        )
    if result.modified_count != 1:
        raise HTTPException(status_code=409, detail="No new parameters were supplied")

    new_fact = facts_collection.find_one({"fact_id": fact_id})
    return Fact(**new_fact)


@app.put("/facts/{fact_id}", response_model=Fact, tags=["resource:facts"])
def put_fact(
    fact_id: str, fact: FactWithoutId, settings: Settings = Depends(get_settings)
):
    facts_collection = get_collection(settings.mongo_url, "facts")

    result = facts_collection.replace_one(
        {"fact_id": fact_id},
        {
            "fact_id": fact_id,
            "name": fact.name,
            "description": fact.description,
            "pos": {"lng": fact.pos[0], "lat": fact.pos[1]},
        },
    )

    if result.matched_count != 1:
        raise HTTPException(
            status_code=404, detail="Fact with specified ID was not found"
        )
    return {
        "fact_id": fact_id,
        "name": fact.name,
        "description": fact.description,
        "pos": {"lng": fact.pos[0], "lat": fact.pos[1]},
    }


@app.delete("/facts/{fact_id}", tags=["resource:facts"])
def delete_fact(fact_id: str, settings: Settings = Depends(get_settings)):
    facts_collection = get_collection(settings.mongo_url, "facts")

    res = facts_collection.delete_one({"fact_id": fact_id})

    if res.deleted_count != 1:
        raise HTTPException(
            status_code=404, detail="Fact with specified id was not found"
        )

@app.get("/facts/near/{lng}/{lat}", response_model=Facts, tags=["resource:facts"])
def get_nearest(lng: float, lat: float, max_dist: Optional[float] = 100, settings: Settings = Depends(get_settings)):
    facts_collection = get_collection(settings.mongo_url, "facts")
    nearest = facts_collection.find({"pos": SON([("$near", [lng, lat]), ("$maxDistance", max_dist)])}).limit(3)
    res = []
    for fact in nearest:
        try:
            res.append(Fact(**fact))
        except Exception as e:
            print(str(e))
    return res