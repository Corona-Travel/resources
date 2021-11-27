from enum import Enum
from typing import List
from pydantic import BaseModel

class MediaType(str, Enum):
    photo = "photo"
    audio = "audio"
    video = "video"

class MediaWithoutId(BaseModel):
    name: str
    type: MediaType
    pos: tuple[float, float]

class Media(MediaWithoutId):
    media_id: str