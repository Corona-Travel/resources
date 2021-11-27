from typing import Optional

from fastapi import FastAPI, HTTPException, Depends
from reusable_mongodb_connection.fastapi import get_collection

from .types import MediaWithoutId, Media
from .settings import Settings, get_settings

app = FastAPI(
    openapi_tags=[
        {
            "name": "resource:media",
        }
    ]
)