from pydantic import BaseModel
from typing import NamedTuple


class Coordinates(NamedTuple):
    lng: float
    lat: float

class Position(BaseModel):
    type: str
    coordinates: Coordinates


class FactWithoutId(BaseModel):
    name: str
    description: str
    pos: Position

    """class Config:
        schema_extra = {
            "example": {
                "name": "London",
                "pos": (-0.118092, 51.509865),
                "description": "London is the capital of Great Britain",
            }
        }"""


class Fact(FactWithoutId):
    fact_id: str

    """class Config:
        schema_extra = {
            "example": {
                "name": "London",
                "pos": (-0.118092, 51.509865),
                "description": "London is the capital of Great Britain",
                "fact_id": "london_fact",
            }
        }"""


Facts = list[Fact]
