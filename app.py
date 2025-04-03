from enum import StrEnum

import fastapi
from fastapi import FastAPI, Response, status
from pydantic import ValidationError

from api.errors import TooManyPlayersError
from api.service.team_assembler_service import TeamAssemblerServiceInstance
from api.service.team_battle_service import BattlegroundServiceInstance, BattleResult
from assembler.team import AssemblyOptions
from models.team import Team

app = FastAPI()


class TeamType(StrEnum):
    pokemon = "pokemon"
    starwars = "starwars"


@app.post("/team/{team_type}")
async def assemble_pokemon_team(
    assembler: TeamAssemblerServiceInstance,
    options: AssemblyOptions,
    team_type: TeamType,
) -> Team:
    if (total := sum((options.attackers, options.defenders, 1))) > 5:
        raise TooManyPlayersError(expected=5, actual=total, options=options)

    match team_type:
        case TeamType.pokemon:
            return await assembler.assemble_pokemon_team(options)
        case TeamType.starwars:
            return await assembler.assemble_starwars_team(options)


@app.post("/battle")
async def battle(battleground: BattlegroundServiceInstance, teams: list[Team]) -> BattleResult:
    return await battleground.battle(teams)


@app.exception_handler(ValidationError)
async def handle_validation_error(r: fastapi.Request, exc: ValidationError) -> Response:
    return Response(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=exc.json(),
        headers={"content-type": "application/json"},
    )
