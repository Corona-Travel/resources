from typing import NamedTuple
from pydantic import BaseModel


class Coordinates(NamedTuple):
    lng: float
    lat: float

class Position(BaseModel):
    type: str
    coordinates: Coordinates


class PlaceWithoutID(BaseModel):
    name: str
    pos: Position

    class Config:
        schema_extra = {
            "example": {
                "name": "London",
                "pos": (51.509865, -0.118092),
            },
        }


class Place(PlaceWithoutID):
    place_id: str

    class Config:
        schema_extra = {
            "example": {
                "name": "London",
                "pos": (51.509865, -0.118092),
                "place_id": "lond",
            }
        }


Places = list[Place]
