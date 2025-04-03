from typing import Any, override

from client.api_client import ApiClient

SWAPI_URL = "https://swapi.dev/api/people"


class StarWarsApiClient(ApiClient):
    @override
    def next_url(self, data: Any) -> str | None:
        return data["next"]

    @override
    async def extract_results(self, data: Any) -> list[dict[str, Any]]:
        return data["results"]
