from typing import Optional, Any

from fastapi import FastAPI, HTTPException, Depends
from reusable_mongodb_connection import get_db

app = FastAPI(
    openapi_tags=[
        {
            "name": "service:quizes",
        }
    ]
)

def get_places_collection(mongo_url: Any):
    try:
        db = get_db(mongo_url)
    except Exception as e:
        print("Connection to DB was unsuccessful")
        print(f"Exception: {e}")
        raise HTTPException(status_code=500, detail="Connection to DB was unsuccessful")

    if "quizes" not in db.list_collection_names():
        print("Collection not found")
        raise HTTPException(
            status_code=500,
            detail="Collection not found",
        )
    return db.quizes
