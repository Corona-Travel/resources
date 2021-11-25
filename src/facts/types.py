from pydantic import BaseModel


class FactWithoutId(BaseModel):
    name: str
    description: str
    pos: Position

    class Config:
        schema_extra = {
            'example': {
                "name": "London",
                "pos": {
                    "lat": 51.509865,
                    "lng": -0.118092
                },
                "description": "London is the capital of Great Britain"
            }
        }


class Fact(FactWithoutId):
    fact_id: str

    class Config:
        schema_extra = {
            'example': {
                "name": "London",
                "pos": {
                    "lat": 51.509865,
                    "lng": -0.118092
                },
                "description": "London is the capital of Great Britain",
                "fact_id": "london_fact"
            }
        }


Facts = list[Fact]
