from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel

from api.errors import NotEnoughTeamsError
from models.team import Team

MINIMUM_TEAM_SIZE = 2


class BattleResult(BaseModel):
    teams: list[Team]
    winner: str


class BattlegroundService:
    async def battle(self, teams: list[Team]) -> BattleResult:
        teams_len = len(teams)
        if teams_len != MINIMUM_TEAM_SIZE:
            raise NotEnoughTeamsError(
                expected_team_size=MINIMUM_TEAM_SIZE,
                actual_team_size=teams_len,
            )
        raise


BattlegroundServiceInstance = Annotated[BattlegroundService, Depends(BattlegroundService)]
