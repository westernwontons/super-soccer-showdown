import abc
from typing import Any

from client.api_client import ApiClient
from models.player import BasePlayer


class PlayerProvider(abc.ABC):
    def __init__(self, client: ApiClient) -> None:
        self.client = client

    def validate_player(self, data: dict[str, Any]) -> BasePlayer | None:
        raise NotImplementedError

    async def provide(self) -> list[BasePlayer]:
        all_people = await self.client.fetch_all()
        players = (self.validate_player(people) for people in all_people)
        return list(filter(None, players))
