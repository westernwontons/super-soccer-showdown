from enum import StrEnum
from typing import Any
from pydantic import AliasChoices, BaseModel, Field, ValidationError, field_validator


class PlayerType(StrEnum):
    GOALIE = "GOALIE"
    DEFENCE = "DEFENCE"
    OFFENCE = "OFFENCE"


class BasePlayer(BaseModel):
    name: str
    weight: float = Field(validation_alias=AliasChoices("weight", "mass"))
    height: float

    @field_validator("weight", "height", mode="wrap")
    @classmethod
    def weight_and_height_validator(cls, value: Any, wrap) -> float:
        try:
            return wrap(value)
        except ValidationError as error:
            for err in error.errors():
                if err["type"] == "float_parsing":
                    if "," in value:
                        # value is a float, let's try parsing it like so
                        # this method is quite crude, but since the swapi dataset is simple,
                        # it should be fine
                        value = value.replace(",", ".")
                        return float(value)
                    else:
                        return float(value)
            raise error


class Player(BasePlayer):
    type_: PlayerType
