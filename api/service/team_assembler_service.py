from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from assembler.team import AssemblyOptions, TeamAssembler
from client.pokemon_api_client import POKEAPI_URL, PokeApiClient
from client.star_wars_api_client import SWAPI_URL, StarWarsApiClient
from errors import NotEnoughPlayers
from models.team import Team
from provider.poke_player_provider import PokePlayerProvider
from provider.star_wars_player_provider import StarWarsPlayerProvider


class TeamAssemblerService:
    def __init__(self) -> None:
        poke_api_client = PokeApiClient(POKEAPI_URL, cache_file="./poke_cache.json")
        poke_provider = PokePlayerProvider(poke_api_client)
        self.poke_assembler = TeamAssembler(poke_provider, 5)

        sw_api_client = StarWarsApiClient(SWAPI_URL, cache_file="./swapi_cache.json")
        sw_provider = StarWarsPlayerProvider(sw_api_client)
        self.sw_assembler = TeamAssembler(sw_provider, 5)

    async def assemble_pokemon_team(self, options: AssemblyOptions) -> Team:
        try:
            return await self.poke_assembler.assemble(options)
        except NotEnoughPlayers:
            self.poke_assembler.pool.reset()
            return await self.poke_assembler.assemble(options)

    async def assemble_starwars_team(self, options: AssemblyOptions) -> Team:
        try:
            return await self.sw_assembler.assemble(options)
        except NotEnoughPlayers:
            self.sw_assembler.pool.reset()
            return await self.sw_assembler.assemble(options)


@lru_cache(1)
def get_team_assembler_service() -> TeamAssemblerService:
    return TeamAssemblerService()


TeamAssemblerServiceInstance = Annotated[TeamAssemblerService, Depends(get_team_assembler_service)]
