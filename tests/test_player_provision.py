from typing import Any

import httpx
import pytest

from client.api_client import ApiClient
from provider.poke_player_provider import PokePlayerProvider
from provider.star_wars_player_provider import StarWarsPlayerProvider


@pytest.mark.asyncio
async def test_star_wars_players_are_provided():
    class SwapiClient(ApiClient):
        def next_url(self, _) -> str | None:
            return None

        async def extract_results(self, data: Any) -> list[dict[str, Any]]:
            return data["results"]

    async def mock_handler(r: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "results": [{"name": "player_name", "mass": 1, "height": 2}],
                "next": None,
                "count": 1,
            },
        )

    provider = StarWarsPlayerProvider(
        SwapiClient(
            "http://localhost:8000/people/1", transport=httpx.MockTransport(handler=mock_handler)
        )
    )

    players = await provider.provide()
    assert len(players) == 1

    player = players[0]
    assert player.name == "player_name"
    assert player.weight == 1
    assert player.height == 2


@pytest.mark.asyncio
async def test_pokemon_players_are_provided():
    class PokeClient(ApiClient):
        def next_url(self, _) -> str | None:
            return None

        async def extract_results(self, data: Any) -> list[dict[str, Any]]:
            return data["results"]

    async def mock_handler(r: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "results": [{"name": "player_name", "weight": 1, "height": 2}],
                "next": None,
                "count": 1,
            },
        )

    provider = PokePlayerProvider(
        PokeClient(
            "http://localhost:8000/people/1", transport=httpx.MockTransport(handler=mock_handler)
        )
    )

    players = await provider.provide()
    assert len(players) == 1

    player = players[0]
    assert player.name == "player_name"
    assert player.weight == 1
    assert player.height == 2
