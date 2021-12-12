from typing import Optional

from fastapi import FastAPI, Depends
from reusable_mongodb_connection.fastapi import get_collection

from .types import MediaWithoutId, Media, Medias
from .settings import Settings, get_settings

app = FastAPI(
    openapi_tags=[
        {
            "name": "resource:media",
        }
    ]
)


@app.get("/media/near/{lng}/{lat}", response_model=Medias, tags=["resource:media"])
def get_nearest(
    lng: float,
    lat: float,
    max_dist: Optional[float] = 10000,
    settings: Settings = Depends(get_settings),
):
    media_collection = get_collection(settings.mongo_url, "media")

    nearest = media_collection.find({"pos": { "$near" :
          {
            "$geometry" : {
               "type" : "Point" ,
               "coordinates" : [lng, lat] },
            "$maxDistance" : max_dist
          }
    }
       })

    res = []
    for media in nearest:
        try:
            res.append(Media(**media))
        except Exception as e:
            print(str(e))
    return res
