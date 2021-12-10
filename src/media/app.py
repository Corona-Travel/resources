from typing import Optional

from fastapi import FastAPI, HTTPException, Depends
from reusable_mongodb_connection.fastapi import get_collection
from pymongo import  GEO2D
from bson.son import SON

from .types import MediaWithoutId, Media, Medias
from .settings import Settings, get_settings

app = FastAPI(
    openapi_tags=[
        {
            "name": "resource:media",
        }
    ]
)

@app.get("/media/near/{lat}/{lng}", response_model=Medias, tags=["resource:facts"])
def get_nearest(lat: float, lng: float, max_dist: Optional[float] = 100, settings: Settings = Depends(get_settings)):
    media_collection = get_collection(settings.mongo_url, "media")
    media_collection.create_index([("pos", GEO2D)])
    nearest = media_collection.find({"pos": SON([("$near", [lat, lng]), ("$maxDistance", max_dist)])}).limit(3)
    res = []
    for media in nearest:
        try:
            res.append(Media(**media))
        except Exception as e:
            print(str(e))
    return res