from collections.abc import Iterable
from typing import Self
from pydantic import BaseModel, field_validator, model_validator

from errors import NotEnoughPlayers
from models.player import Player, PlayerType


def player_type_validator(players: Iterable[Player], player_type: PlayerType) -> list[Player]:
    return [player for player in players if player.type_ == player_type]


class Team(BaseModel):
    goalie: Player
    attackers: list[Player]
    defenders: list[Player]

    @field_validator("goalie", mode="after")
    @classmethod
    def validate_goalie(cls, player: Player) -> Player:
        return player_type_validator((player,), PlayerType.GOALIE)[0]

    @field_validator("attackers")
    @classmethod
    def validate_attackers(cls, players: Iterable[Player]) -> list[Player]:
        return player_type_validator(players, PlayerType.OFFENCE)

    @field_validator("defenders")
    @classmethod
    def validate_defenders(cls, players: Iterable[Player]) -> list[Player]:
        return player_type_validator(players, PlayerType.DEFENCE)

    @model_validator(mode="after")
    def verify_players(self) -> Self:
        MAX_TEAM_SIZE = 5

        attackers_len = len(self.attackers)
        defenders_len = len(self.defenders)
        total = sum((attackers_len, defenders_len, 1))

        if total != MAX_TEAM_SIZE:
            raise NotEnoughPlayers(f"Expected 5 players in the team, found {total}")

        return self
