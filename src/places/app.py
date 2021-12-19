from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from reusable_mongodb_connection.fastapi import get_collection

from .settings import Settings, get_settings
from .types import Place, Places, PlaceWithoutID

app = FastAPI(
    openapi_tags=[
        {
            "name": "resource:places",
        }
    ]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_mongodb(settings: Settings = Depends(get_settings)):
    return get_collection(settings.mongo_url, "places")


@app.get("/places", response_model=Places, tags=["resource:places"])
def get_places(place_collection=Depends(get_mongodb)):

    places = place_collection.find({})

    res = []
    for place in places:
        try:
            res.append(
                Place(
                    place_id=place["place_id"],
                    name=place["name"],
                    pos=place["pos"]["coordinates"],
                )
            )
        except Exception as e:
            print(str(e))
    return res


@app.post("/places", tags=["resource:places"])
def post_place(place: Place, place_collection=Depends(get_mongodb)):

    place_with_same_id = place_collection.find_one({"place_id": place.place_id})

    if place_with_same_id is not None:
        raise HTTPException(status_code=400, detail="place ID occupied")

    coordinates = place.pos
    place.pos = {"type": "Point", "coordinates": coordinates}

    place_collection.insert_one(place.dict())


@app.get("/places/{place_id}", response_model=Place, tags=["resource:places"])
def get_places_by_id(place_id: str, place_collection=Depends(get_mongodb)):

    place = place_collection.find_one({"place_id": place_id})

    if place is None:
        raise HTTPException(
            status_code=404, detail="Place with specified id was not found"
        )
    return Place(
        place_id=place["place_id"],
        name=place["name"],
        pos=place["pos"]["coordinates"],
    )


@app.patch("/places/{place_id}", response_model=Place, tags=["resource:places"])
def patch_place(
    place_id: str,
    name: Optional[str] = None,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    place_collection=Depends(get_mongodb),
):

    old_pos = place_collection.find_one({"place_id": place_id})["pos"]

    new_place_dict = {}
    if name is not None:
        new_place_dict["name"] = name
    if (lat is not None) or (lng is not None):
        new_pos = list(old_pos)
        if lat is not None:
            new_pos[0] = lat
        if lng is not None:
            new_pos[1] = lng
        new_place_dict["pos"] = {"type": "Point", "coordinates": tuple(new_pos)}

    if not new_place_dict:
        raise HTTPException(status_code=409, detail="No new parameters were supplied")

    res = place_collection.update_one({"place_id": place_id}, {"$set": new_place_dict})

    if not res.modified_count:
        raise HTTPException(status_code=409, detail="No new parameters were supplied")
    if not res.matched_count:
        raise HTTPException(
            status_code=404, detail="Place with specified ID was not found"
        )
    new_place = place_collection.find_one({"place_id": place_id})
    return Place(
        place_id=new_place["place_id"],
        name=new_place["name"],
        pos=new_place["pos"]["coordinates"],
    )


@app.put("/places/{place_id}", response_model=Place, tags=["resource:places"])
def put_place(
    place_id: str, place: PlaceWithoutID, place_collection=Depends(get_mongodb)
):

    coordinates = place.pos
    place.pos = {"type": "Point", "coordinates": coordinates}

    res = place_collection.update_one({"place_id": place_id}, {"$set": place.dict()})

    if not res.matched_count:
        raise HTTPException(
            status_code=404, detail="Place with specified ID was not found"
        )
    new_place = place_collection.find_one({"place_id": place_id})
    return Place(
        place_id=new_place["place_id"],
        name=new_place["name"],
        pos=new_place["pos"]["coordinates"],
    )


@app.delete("/places/{place_id}", tags=["resource:places"])
def delete_place(place_id: str, place_collection=Depends(get_mongodb)):

    res = place_collection.delete_one({"place_id": place_id})

    if not res.deleted_count:
        raise HTTPException(
            status_code=404, detail="Place with specified ID was not found"
        )


@app.get("/places/near/{lng}/{lat}", response_model=Places, tags=["resource:places"])
def get_nearest(
    lat: float,
    lng: float,
    max_dist: Optional[float] = 100,
    place_collection=Depends(get_mongodb),
):
    nearest = place_collection.find(
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
    for place in nearest:
        try:
            res.append(Place(**place))
        except Exception as e:
            print(str(e))
    return res
