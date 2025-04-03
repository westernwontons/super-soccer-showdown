import asyncio
from typing import Any, override

from client.api_client import ApiClient

POKEAPI_URL = "https://pokeapi.co/api/v2/pokemon"


class PokeApiClient(ApiClient):
    @override
    def next_url(self, data: Any) -> str | None:
        return data["next"]

    @override
    async def extract_results(self, data: Any) -> list[dict[str, Any]]:
        urls = [item["url"] for item in data["results"]]
        responses = await asyncio.gather(*[self.client.get(url) for url in urls])
        json = [r.json() for r in responses]
        keys = ["name", "weight", "height"]
        return [{key: value for key, value in item.items() if key in keys} for item in json]
