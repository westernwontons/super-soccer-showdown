from typing import Any
import httpx
import pytest

from assembler.team import AssemblyOptions, TeamAssembler
from client.api_client import ApiClient
from models.player import BasePlayer
from provider.player_provider import PlayerProvider


@pytest.mark.asyncio
async def test_team_is_assembled() -> None:
    class DummyPlayerProvider(PlayerProvider):
        def validate_player(self, data: Any) -> BasePlayer | None:
            return BasePlayer.model_validate(
                {
                    "weight": data["weight"],
                    "name": data["name"],
                    "height": data["height"],
                },
                by_name=True,
                by_alias=True,
            )

    class DummyApiClient(ApiClient):
        def next_url(self, data: Any) -> str | None:
            return data["next"]

        async def extract_results(self, data: Any) -> list[dict[str, Any]]:
            return data["results"]

    async def mock_handler(_r: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "results": [
                    {"height": 20, "name": "venusaur", "weight": 1000},
                    {"height": 17, "name": "charizard", "weight": 905},
                    {"height": 16, "name": "blastoise", "weight": 855},
                    {"height": 11, "name": "charmeleon", "weight": 190},
                    {"height": 11, "name": "butterfree", "weight": 320},
                    {"height": 10, "name": "ivysaur", "weight": 130},
                    {"height": 10, "name": "wartortle", "weight": 225},
                    {"height": 7, "name": "bulbasaur", "weight": 69},
                    {"height": 7, "name": "metapod", "weight": 99},
                    {"height": 6, "name": "charmander", "weight": 85},
                    {"height": 5, "name": "squirtle", "weight": 90},
                    {"height": 3, "name": "caterpie", "weight": 29},
                ],
                "next": None,
                "count": 1,
            },
        )

    client = DummyApiClient(
        "http://localhost:8000", transport=httpx.MockTransport(handler=mock_handler)
    )
    provider = DummyPlayerProvider(client)
    assembler = TeamAssembler(provider, 5)
    assert len(assembler.pool.attackers) == 0
    assert len(assembler.pool.defenders) == 0
    assert len(assembler.pool.goalies) == 0

    await assembler.pool.pool()

    assert len(assembler.pool.attackers) == 12
    assert len(assembler.pool.defenders) == 12
    assert len(assembler.pool.goalies) == 12

    team = await assembler.assemble(AssemblyOptions(attackers=3, defenders=1))

    assert len(team.attackers) == 3
    assert len(team.defenders) == 1

    assert assembler.pool.attackers_consumed == 3
    assert assembler.pool.defenders_consumed == 1
    assert assembler.pool.goalies_consumed == 1

    team = await assembler.assemble(AssemblyOptions(attackers=2, defenders=2))

    assert len(team.attackers) == 2
    assert len(team.defenders) == 2

    assert assembler.pool.attackers_consumed == 5
    assert assembler.pool.defenders_consumed == 3
    assert assembler.pool.goalies_consumed == 2
