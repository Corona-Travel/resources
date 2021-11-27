from pydantic import BaseModel
from typing import NamedTuple, Tuple, List


class Position(NamedTuple):
    lat: float
    lng: float


class FactWithoutId(BaseModel):
    name: str
    description: str
    pos: Position

    class Config:
        schema_extra = {
            "example": {
                "name": "London",
                "pos": (51.509865, -0.118092),
                "description": "London is the capital of Great Britain",
            }
        }


class Fact(FactWithoutId):
    fact_id: str

    class Config:
        schema_extra = {
            "example": {
                "name": "London",
                "pos": (51.509865, -0.118092),
                "description": "London is the capital of Great Britain",
                "fact_id": "london_fact",
            }
        }


Facts = list[Fact]
