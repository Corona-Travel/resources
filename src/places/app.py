from typing import Optional

from fastapi import FastAPI, HTTPException, Depends
from pymongo import  GEO2D
from bson.son import SON
from reusable_mongodb_connection.fastapi import get_collection

from .types import Place, PlaceWithoutID, Places
from .settings import Settings, get_settings

app = FastAPI(
    openapi_tags=[
        {
            "name": "resource:places",
        }
    ]
)


@app.get("/places", response_model=Places, tags=["resource:places"])
def get_places(settings: Settings = Depends(get_settings)):
    place_collection = get_collection(settings.mongo_url, "places")

    markers = place_collection.find({})

    res = []
    for m in markers:
        try:
            res.append(Place(**m))
        except Exception as e:
            print(str(e))
    return res


@app.post("/places", tags=["resource:places"])
def post_place(place: Place, settings: Settings = Depends(get_settings)):
    place_collection = get_collection(settings.mongo_url, "places")

    place_with_same_id = place_collection.find_one({"place_id": place.place_id})

    if place_with_same_id is not None:
        raise HTTPException(status_code=400, detail="place ID occupied")

    place_collection.insert_one(place.dict())


@app.get("/places/{place_id}", response_model=Place, tags=["resource:places"])
def get_places_by_id(place_id: str, settings: Settings = Depends(get_settings)):
    collection = get_collection(settings.mongo_url, "places")

    place = collection.find_one({"place_id": place_id})

    if place is None:
        raise HTTPException(
            status_code=404, detail="Place with specified id was not found"
        )
    return Place(**place)


@app.patch("/places/{place_id}", response_model=Place, tags=["resource:places"])
def patch_place(
    place_id: str,
    name: Optional[str] = None,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    settings: Settings = Depends(get_settings),
):
    places_collection = get_collection(settings.mongo_url, "places")

    old_pos = places_collection.find_one({"place_id": place_id})["pos"]

    new_place_dict = {}
    if name is not None:
        new_place_dict["name"] = name
    if (lat is not None) or (lng is not None):
        new_pos = list(old_pos)
        if lat is not None:
            new_pos[0] = lat
        if lng is not None:
            new_pos[1] = lng
        new_place_dict["pos"] = tuple(new_pos)

    if not new_place_dict:
        raise HTTPException(status_code=409, detail="No new parameters were supplied")

    res = places_collection.update_one({"place_id": place_id}, {"$set": new_place_dict})

    if not res.modified_count:
        raise HTTPException(status_code=409, detail="No new parameters were supplied")
    if not res.matched_count:
        raise HTTPException(
            status_code=404, detail="Place with specified ID was not found"
        )
    new_place = places_collection.find_one({"place_id": place_id})
    return Place(**new_place)


@app.put("/places/{place_id}", response_model=Place, tags=["resource:places"])
def put_place(
    place_id: str, place: PlaceWithoutID, settings: Settings = Depends(get_settings)
):
    places_collection = get_collection(settings.mongo_url, "places")

    res = places_collection.update_one({"place_id": place_id}, {"$set": place.dict()})

    if not res.matched_count:
        raise HTTPException(
            status_code=404, detail="Place with specified ID was not found"
        )
    new_place = places_collection.find_one({"place_id": place_id})
    return Place(**new_place)


@app.delete("/places/{place_id}", tags=["resource:places"])
def delete_place(place_id: str, settings: Settings = Depends(get_settings)):
    places_collection = get_collection(settings.mongo_url, "places")

    res = places_collection.delete_one({"place_id": place_id})

    if not res.deleted_count:
        raise HTTPException(
            status_code=404, detail="Place with specified ID was not found"
        )

@app.get("/places/near/{lat}/{lng}", response_model=Places, tags=["resource:places"])
def get_nearest(lat: float, lng: float, max_dist: Optional[float] = 100, settings: Settings = Depends(get_settings)):
    places_collection = get_collection(settings.mongo_url)
    places_collection.create_index([("pos", GEO2D)])
    nearest = places_collection.find({"pos": SON([("$near", [lat, lng]), ("$maxDistance", max_dist)])}).limit(3)
    res = []
    for place in nearest:
        try:
            res.append(Place(**place))
        except Exception as e:
            print(str(e))
    return res