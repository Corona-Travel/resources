from logging import getLogger
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from reusable_mongodb_connection.fastapi import get_collection

from .settings import Settings, get_settings
from .types import Fact, Facts, FactWithoutId, Position

app = FastAPI(openapi_tags=[{"name": "resource:facts"}])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = getLogger("facts")
logger.setLevel(get_settings().log_level)


def get_mongodb(settings: Settings = Depends(get_settings)):
    return get_collection(settings.mongo_url, "facts")


@app.get("/facts", response_model=Facts, tags=["resource:facts"])
def get_facts(facts_collection=Depends(get_mongodb)):
    facts = facts_collection.find({})

    logger.debug("getting facts: %s", facts)

    res = []
    for f in facts:
        try:
            res.append(
                Fact(
                    fact_id=f["fact_id"],
                    name=f["name"],
                    description=f["description"],
                    pos=f["pos"]["coordinates"],
                )
            )
        except Exception as e:
            print(str(e))
    return res


@app.post("/facts", tags=["resource:facts"])
def post_fact(
    fact: Fact,
    facts_collection = Depends(get_mongodb),
):

    print(fact.dict())

    fact_with_same_id = facts_collection.find_one({"fact_id": fact.fact_id})

    if fact_with_same_id is not None:
        raise HTTPException(status_code=400, detail="fact ID occupied")

    coordinates = fact.pos
    fact.pos = {"type": "Point", "coordinates": coordinates}

    facts_collection.insert_one(fact.dict())


@app.get("/facts/{fact_id}", response_model=Fact, tags=["resource:facts"])
def get_fact_by_id(fact_id: str, facts_collection=Depends(get_mongodb)):
    fact = facts_collection.find_one({"fact_id": fact_id})

    if fact is None:
        raise HTTPException(
            status_code=404, detail="Fact with specified id was not found"
        )
    return Fact(
        fact_id=fact["fact_id"],
        name=fact["name"],
        description=fact["description"],
        pos=fact["pos"]["coordinates"],
    )


@app.patch("/facts/{fact_id}", response_model=Fact, tags=["resource:facts"])
def patch_fact(
    fact_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    lng: Optional[float] = None,
    lat: Optional[float] = None,
    facts_collection = Depends(get_mongodb),
):
    if (name is None) and (description is None) and (lat is None) and (lng is None):
        raise HTTPException(status_code=409, detail="No new parameters were supplied")

    old_fact_pos = facts_collection.find_one({"fact_id": fact_id})["pos"]

    new_fact_dict = {}
    if name is not None:
        new_fact_dict["name"] = name
    if description is not None:
        new_fact_dict["description"] = description
    if (lng is not None) or (lat is not None):
        new_pos = list(old_fact_pos)
        if lng is not None:
            new_pos[0] = lng
        if lat is not None:
            new_pos[1] = lat
        new_fact_dict["pos"] = {"type": "Point", "coordinates": tuple(new_pos)}

    result = facts_collection.update_one({"fact_id": fact_id}, {"$set": new_fact_dict})

    if result.matched_count != 1:
        raise HTTPException(
            status_code=404, detail="Fact with specified id was not found"
        )
    if result.modified_count != 1:
        raise HTTPException(status_code=409, detail="No new parameters were supplied")

    new_fact = facts_collection.find_one({"fact_id": fact_id})
    return Fact(
        fact_id=new_fact["fact_id"],
        name=new_fact["name"],
        description=new_fact["description"],
        pos=new_fact["pos"]["coordinates"],
    )


@app.put("/facts/{fact_id}", response_model=Fact, tags=["resource:facts"])
def put_fact(
    fact_id: str, fact: FactWithoutId, facts_collection = Depends(get_mongodb)
):
    logger.debug(f"updating fact with id {fact_id} with {fact.dict()}")

    result = facts_collection.replace_one(
        {"fact_id": fact_id},
        {
            "fact_id": fact_id,
            "name": fact.name,
            "description": fact.description,
            "pos": {"type": "Point", "coordinates": fact.pos},
        },
    )

    if result.matched_count != 1:
        raise HTTPException(
            status_code=404, detail="Fact with specified ID was not found"
        )
    return Fact(
        fact_id=fact_id,
        name=fact.name,
        description=fact.description,
        pos=fact.pos,
    )


@app.delete("/facts/{fact_id}", tags=["resource:facts"])
def delete_fact(fact_id: str, facts_collection = Depends(get_mongodb)):

    res = facts_collection.delete_one({"fact_id": fact_id})

    if res.deleted_count != 1:
        raise HTTPException(
            status_code=404, detail="Fact with specified id was not found"
        )


@app.get("/facts/near/{lng}/{lat}", response_model=Facts, tags=["resource:facts"])
def get_nearest(
    lng: float,
    lat: float,
    max_dist: Optional[float] = 10000,
    facts_collection = Depends(get_mongodb),
):
    facts = facts_collection.find(
        {
            "pos": {
                "$near": {
                    "$geometry": {"type": "Point", "coordinates": [lng, lat]},
                    "$maxDistance": max_dist,
                }
            }
        }
    )

    res = []
    for fact in facts:
        try:
            res.append(
                Fact(
                    fact_id=fact["fact_id"],
                    name=fact["name"],
                    description=fact["description"],
                    pos=fact["pos"]["coordinates"],
                )
            )
        except Exception as e:
            print(str(e))
    return res
