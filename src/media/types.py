from enum import Enum
from typing import NamedTuple, Tuple, List
from pydantic import BaseModel


class Position(NamedTuple):
    lng: float
    lat: float


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