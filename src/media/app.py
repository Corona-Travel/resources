from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from reusable_mongodb_connection.fastapi import get_collection

from .settings import Settings, get_settings
from .types import Media, Medias, MediaWithoutId

app = FastAPI(
    openapi_tags=[
        {
            "name": "resource:media",
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
    return get_collection(settings.mongo_url, "media")


@app.get("/media", response_model=Medias, tags=["resource:media"])
def get_medias(media_collection=Depends(get_mongodb)):
    medias = media_collection.find({})

    res = []
    for m in medias:
        try:
            res.append(
                Media(
                    media_id=m["media_id"],
                    name=m["name"],
                    type=m["type"],
                    pos=m["pos"]["coordinates"],
                    url=m["url"],
                )
            )
        except Exception as e:
            print(str(e))
    return res


@app.post("/media", tags=["resource:media"])
def post_media(media: Media, media_collection=Depends(get_mongodb)):

    media_with_same_id = media_collection.find_one({"media_id": media.media_id})

    if media_with_same_id is not None:
        raise HTTPException(status_code=400, detail="place ID occupied")

    coordinates = media.pos
    media.pos = {"type": "Point", "coordinates": coordinates}

    media_collection.insert_one(media.dict())


@app.get("/media/{media_id}", response_model=Media, tags=["resource:media"])
def get_media_by_id(media_id: str, media_collection=Depends(get_mongodb)):

    media = collection.find_one({"media_id": media_id})

    if media is None:
        raise HTTPException(
            status_code=404, detail="Place with specified id was not found"
        )
    return Media(
        media_id=media["media_id"],
        name=media["name"],
        url=media["url"],
        type=media["type"],
        pos=media["pos"]["coordinates"],
    )


@app.patch("/media/{media_id}", response_model=Media, tags=["resource:media"])
def patch_place(
    media_id: str,
    name: Optional[str] = None,
    url: Optional[str] = None,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    media_collection=Depends(get_mongodb),
):

    old_pos = media_collection.find_one({"media_id": media_id})["pos"]

    new_media_dict = {}
    if name is not None:
        new_media_dict["name"] = name
    if url is not None:
        new_media_dict["url"] = url
    if (lat is not None) or (lng is not None):
        new_pos = list(old_pos)
        if lat is not None:
            new_pos[0] = lat
        if lng is not None:
            new_pos[1] = lng
        new_media_dict["pos"] = {"type": "Point", "coordinates": tuple(new_pos)}

    if not new_media_dict:
        raise HTTPException(status_code=409, detail="No new parameters were supplied")

    res = media_collection.update_one({"media_id": media_id}, {"$set": new_media_dict})

    if not res.modified_count:
        raise HTTPException(status_code=409, detail="No new parameters were supplied")
    if not res.matched_count:
        raise HTTPException(
            status_code=404, detail="Media with specified ID was not found"
        )
    new_media = media_collection.find_one({"media_id": media_id})
    return Media(
        media_id=new_media["media_id"],
        name=new_media["name"],
        url=new_media["url"],
        type=new_media["type"],
        pos=new_media["pos"]["coordinates"],
    )


@app.put("/media/{media_id}", response_model=Media, tags=["resource:media"])
def put_place(
    media_id: str, media: MediaWithoutId, media_collection=Depends(get_mongodb)
):

    coordinates = media.pos
    media.pos = {"type": "Point", "coordinates": coordinates}

    res = media_collection.update_one({"media_id": media_id}, {"$set": media.dict()})

    if not res.matched_count:
        raise HTTPException(
            status_code=404, detail="Place with specified ID was not found"
        )
    new_media = media_collection.find_one({"media_id": media_id})
    return Media(
        media_id=new_media["media_id"],
        name=new_media["name"],
        url=new_media["url"],
        type=new_media["type"],
        pos=new_media["pos"]["coordinates"],
    )


@app.delete("/media/{media_id}", tags=["resource:media"])
def delete_place(media_id: str, media_collection=Depends(get_mongodb)):

    res = media_collection.delete_one({"media_id": media_id})

    if not res.deleted_count:
        raise HTTPException(
            status_code=404, detail="Media with specified ID was not found"
        )


@app.get("/media/near/{lng}/{lat}", response_model=Medias, tags=["resource:media"])
def get_nearest(
    lng: float,
    lat: float,
    max_dist: Optional[float] = 10000,
    media_collection=Depends(get_mongodb),
):

    nearest = media_collection.find(
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
    for m in nearest:
        try:
            res.append(
                Media(
                    media_id=m["media_id"],
                    name=m["name"],
                    type=m["type"],
                    pos=m["pos"]["coordinates"],
                    url=m["url"],
                )
            )
        except Exception as e:
            print(str(e))
    return res
