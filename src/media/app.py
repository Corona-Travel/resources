from typing import Optional

from fastapi import Depends, FastAPI
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


@app.get("/media", response_model=Medias, tags=["resource:media"])
def get_medias(settings: Settings = Depends(get_settings)):
    media_collection = get_collection(settings.mongo_url, "media")
    medias = media_collection.find({})

    res = []
    for m in medias:
        try:
            res.append(Media(**m))
        except Exception as e:
            print(str(e))
    return res


@app.get("/media/near/{lng}/{lat}", response_model=Medias, tags=["resource:media"])
def get_nearest(
    lng: float,
    lat: float,
    max_dist: Optional[float] = 10000,
    settings: Settings = Depends(get_settings),
):
    media_collection = get_collection(settings.mongo_url, "media")

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
    for media in nearest:
        try:
            res.append(Media(**media))
        except Exception as e:
            print(str(e))
    return res
