from enum import Enum
from typing import NamedTuple
from pydantic import BaseModel


class Coordinates(NamedTuple):
    lng: float
    lat: float

class Position(BaseModel):
    type: str
    coordinates: Coordinates


class MediaType(str, Enum):
    photo = "photo"
    audio = "audio"
    video = "video"


class MediaWithoutId(BaseModel):
    name: str
    type: MediaType
    pos: Position


class Media(MediaWithoutId):
    media_id: str


Medias = list[Media]
