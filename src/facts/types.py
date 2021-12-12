from typing import NamedTuple

from pydantic import BaseModel


class Position(NamedTuple):
    lng: float
    lat: float


class FactWithoutId(BaseModel):
    name: str
    description: str
    pos: Position

    class Config:
        schema_extra = {
            "example": {
                "name": "London",
                "pos": (-0.118092, 51.509865),
                "description": "London is the capital of Great Britain",
            }
        }


class Fact(FactWithoutId):
    fact_id: str

    class Config:
        schema_extra = {
            "example": {
                "name": "London",
                "pos": (-0.118092, 51.509865),
                "description": "London is the capital of Great Britain",
                "fact_id": "london_fact",
            }
        }


Facts = list[Fact]
